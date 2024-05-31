"""
https://github.com/google-gemini/generative-ai-python@main
"""

import logging
import pathlib
import re
import sys
import os
import traceback

from typing import Optional

import tqdm

from absl import app
from absl import flags
import absl.logging

import nbconvert
import nbformat

os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'

flags.DEFINE_bool("clean", False, "Remove the cache files and start a clearn run")
flags.DEFINE_bool("debug", False, "Print the notebook execution log")
flags.DEFINE_bool("save_output", False, "save the output back to the notebook file.")
flags.DEFINE_integer("timeout", 600, "Timeout in seconds for a cell's execution.")
flags.DEFINE_list('skip', None, "list of path patterns to skip")

FLAGS = flags.FLAGS

SKIP_EXECUTE = [re.compile("pip .*install .*google\.(ai\.generativelanguage|generativeai)"),
                re.compile("userdata\.get"),
                re.compile("google.colab.*?userdata"),
                re.compile("list(_tuned)?_models")]


class DiscardStatusMessagesFilter(logging.Filter):
    """Filters out jupyter execution status messages.

    These messages are just cluttter:

    ```
    I0507 execute.py:643] msg_type: status
    I0507 execute.py:645] content: {'execution_state': 'busy'}
    ```

    The records have the form:

    ```
    record.msg = "msg_type: %s"
    record.args = ('status',)
    ```

    and

    ```
    record.msg = "content: %s"
    record.args = {'execution_state': ...}
    ```
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Reject status messages.

        Args:
          record: A `logging.LogRecord`.

        Returns:
          False: (discard) for status messages.
          True: (keep) for anything else.
        """
        if record.msg.startswith("msg_type:"):
            if record.args == ("status",):
                return False

        if not record.msg.startswith("content:"):
            return True

        args = record.args
        if not isinstance(args, dict):
            return True

        if args.get("execution_state", None):
            return False

        return True


class DiscardRawDataFilter(logging.Filter):
    r"""Trims binary and html data, discards raw code and exceptions.

    Image and video data are long, trim those entries to the first few characters.

    Raw-exceptions are filled with escaped color control characters. These are
    not human readable, so these are discarded. We can rely on the
    pretty-printed exceptions, those work fine.

    Similarly code cells are pretty-printed as well by the "Executing Cell"
    records. So drop the raw-code `LogRecords`.

    These binary and html messages have the form:

    ```
    record.msg = "content: %s"
    record.args = {'data':{MIME-TYPE:CONTENT}}
    ```

    The raw exceptions have the form:

    ```
    record.msg = "content: %s"
    record.args = {'traceback': ...}
    record.args = {'code': ...}
    ```

    """

    _TRIM_LENGTH = 20

    def filter(self, record: logging.LogRecord) -> bool:
        """Trims binary and html data records, and discards raw-exceptions.

        Args:
          record: A `logging.LogRecord`.

        Returns:
          False: (discard) for raw-exception records.
          True: (keep) all other records.
        """
        if not record.msg.startswith("content:"):
            return True

        args = record.args
        if not isinstance(args, dict):
            return True

        if args.get("traceback") is not None:
            return False
        if args.get("code") is not None:
            return False

        data = args.get("data", None)
        if data is None:
            return True

        new_data = {}
        for key, value in data.items():
            key = key.lower()
            if "image" in key or "video" in key or "html" in key:
                value = value[: self._TRIM_LENGTH] + "..."
            new_data[key] = value

        # Replace the args dict with a copy, so it doesn't affect notebook output.
        new_args = args.copy()
        new_args["data"] = new_data
        record.args = new_args
        return True


class PrettyPrintNotebookStdout(logging.Filter):
    """Pretty-prints std-out messages generated during notebook exdecution.

    These messages have the form:

    ```
    record.msg = 'content: %s'
    record.args = {'name': 'stdout', 'text': '...'}
    ```

    The text __repr__ is hard to read, replace the record's dict with a
    pretty-printed text.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Converts stdout records to a pretty-printed form.

        Args:
          record: A `logging.LogRecord`.

        Returns:
          True: (keep) all records.
        """
        if not record.msg.startswith("content:"):
            return True

        if not isinstance(record.args, dict):
            return True

        name = record.args.get("name", None)
        if name is None:
            return True

        text = record.args.get("text", None)
        if name == "stdout" and text is not None:
            record.msg = "StdOut: \n\n%s"
            record.args = (text,)

        return True


class CustomNotebookExecutor(nbconvert.preprocessors.ExecutePreprocessor):
    """Executes all cells in a notebook."""

    def _should_execute(self, cell: nbformat.notebooknode.NotebookNode) -> bool:
        if cell["cell_type"] == "code":
            source: str = cell.source
            if any(pattern.search(source) for pattern in SKIP_EXECUTE):
                return False

        return True

    def preprocess_cell(self, cell, resources, cell_index, **kwargs):
        """Executes one cell in a notebook."""
        if not self._should_execute(cell):
            return cell, resources

        return super().preprocess_cell(cell, resources, cell_index, **kwargs)


def init_logging() -> None:
    """Initialize logger and handler to report execution results.

    `nbconvert` uses the LogRecords to capture notebook execution results.
    These handlers are independent from the ones used in nbconvert. They
      * Listen to the same stream of events.
      * Are careful not to modify mutable datastructures in the messages.

    See https://docs.python.org/3/howto/logging.html#logging-flow for details.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = absl.logging.get_absl_handler()
    handler.setLevel(logging.DEBUG)
    handler.addFilter(DiscardStatusMessagesFilter())
    handler.addFilter(DiscardRawDataFilter())
    handler.addFilter(PrettyPrintNotebookStdout())


def execute(
    processor: nbconvert.preprocessors.ExecutePreprocessor,
    input_notebook: str,
    output_notebook: Optional[str] = None,
):
    """Executes a notebook with the custom executor.

    It also saves the outputs:
      * To the same notebook if output notebook is not specified.
      * To an output notebook if it is specified.

    Args:
      processor: The processor to use to execute the notebooks.
      input_notebook: Path of the input notebook.
      output_notebook: Path of the output notebook.

    Raises:
      nbconvert.preprocessors.CellExecutionError: When a cell's execution fails.
    """

    # Read the notebook contents.
    with open(input_notebook) as input_nb:
        nb = nbformat.read(input_nb, as_version=4)

    # Default the output_notebook to the notebooks passed in via the flag.
    # If its `None`, then set the output_notebook to the input_notebook
    # overwriting the input_notebook.
    if output_notebook is None:
        output_notebook = input_notebook

    # Execute the notebook.
    processor.preprocess(
        nb,
        resources={"metadata": {"path": str(pathlib.Path(input_notebook).parent)}},
    )

    if FLAGS.save_output:
        with open(output_notebook, "w", encoding="utf-8") as output_nb:
            nbformat.write(nb, output_nb)


def test_notebook(processor, notebook):
    execute(
        processor=processor,
        input_notebook=str(notebook),
        output_notebook=str(notebook),
    )


def main(argv):
    notebooks = argv[1:]

    if FLAGS.debug:
        init_logging()

    if FLAGS.clean:
        pathlib.Path('error.txt').unlink(missing_ok=True)
        pathlib.Path('good.txt').unlink(missing_ok=True)
        pathlib.Path('tracebacks.txt').unlink(missing_ok=True)


    processor = CustomNotebookExecutor(timeout=FLAGS.timeout)

    if notebooks:
        if len(notebooks) == 1:
            nb = pathlib.Path(notebooks[0])
            if nb.is_file():
                print(nb)
                test_notebook(processor, nb)
                print('    Okay!')
                return

    else:
        notebooks = [os.getcwd()]
    notebooks = [pathlib.Path(p) for p in notebooks]

    def expand_dirs(paths):
        for p in paths:
            if p.is_dir():
                yield from p.rglob("*.ipynb")
            else:
                yield p


    notebooks = expand_dirs(notebooks)
    skip = [".ipynb_checkpoints"]
    if FLAGS.skip:
        skip.extend(FLAGS.skip)

    def filter(paths):
        for path in paths:
            if any(s in str(path) for s in skip):
                continue
            yield path

    notebooks = filter(notebooks)
    notebooks = list(notebooks)

    good_file = pathlib.Path('good.txt')
    if good_file.exists():
        good_notebooks = set(good_file.read_text().splitlines())
    else:
        good_notebooks = []

    error_file = pathlib.Path('error.txt')
    if error_file.exists():
        error_notebooks = set(error_file.read_text().splitlines())
    else:
        error_notebooks = []

    traceback_file = pathlib.Path('tracebacks.txt')
    with open(error_file, 'a') as ef, open(good_file, 'a') as df, open(traceback_file, 'a') as tbf:
        for notebook in tqdm.tqdm(notebooks):
            print("\n\n"+"_"*80)
            print(notebook)
            if str(notebook) in good_notebooks:
                print('    Okay!')
                continue
            if str(notebook) in error_notebooks:
                print('    Error!')
                continue

            # Execute a notebook with the custom executor.
            try:
                test_notebook(processor, notebook)
            except Exception as e:
                print("    Error!")
                tbf.write("_"*80 + "\n")
                tbf.write(f"notebook: {notebook}\n")
                traceback.print_exception(e, file=tbf)
                traceback.print_exception(e)
                print(f"\n\nin notebook: {notebook}")
                ef.write(str(notebook)+'\n')
            else:
                print("    Okay!")
                df.write(str(notebook)+'\n')


if __name__ == "__main__":
    app.run(main)
