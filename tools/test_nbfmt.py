# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Regression tests for the notebook formatter."""

import json
import pathlib
import tempfile
import unittest

from tools.nbfmt.formatter import NotebookFormatter


class TestNotebookFormatter(unittest.TestCase):
    """Checks that formatting preserves notebook content and valid JSON."""

    def test_unicode_separators_round_trip(self):
        for separator in ("\u0085", "\u2028", "\u2029"):
            for source_is_string in (False, True):
                with self.subTest(separator=repr(separator), source_is_string=source_is_string):
                    text = f"before{separator}after"
                    data = {
                        "cells": [{
                            "cell_type": "markdown",
                            "metadata": {},
                            "source": text if source_is_string else [text],
                        }],
                        "metadata": {},
                        "nbformat": 4,
                        "nbformat_minor": 0,
                    }
                    formatter = NotebookFormatter()
                    path = pathlib.Path("example.ipynb")

                    formatted = formatter.format_bytes(data, path)
                    parsed = json.loads(formatted)

                    self.assertEqual("".join(parsed["cells"][0]["source"]), text)
                    self.assertEqual(formatter.format_bytes(parsed, path), formatted)

    def test_unicode_separators_in_outputs_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = pathlib.Path(temp_dir) / "example.ipynb"
            text = "before\u0085middle\u2028more\u2029after"
            outputs = [{"output_type": "stream", "name": "stdout", "text": [text]}]
            data = {
                "cells": [{
                    "cell_type": "code",
                    "metadata": {},
                    "source": ["print('example')"],
                    "execution_count": 1,
                    "outputs": outputs,
                }],
                "metadata": {"language_info": {"name": "python", "description": text}},
                "nbformat": 4,
                "nbformat_minor": 0,
            }
            path.write_text(json.dumps(data), encoding="utf-8")
            formatter = NotebookFormatter()

            result = formatter.format_file(path)
            self.assertTrue(result.is_formatted)
            parsed = json.loads(path.read_bytes())

            self.assertEqual(parsed["cells"][0]["outputs"], outputs)
            self.assertEqual(parsed["metadata"]["language_info"]["description"], text)
            self.assertTrue(formatter.format_file(path, test_only=True).is_formatted)


if __name__ == "__main__":
    unittest.main()
