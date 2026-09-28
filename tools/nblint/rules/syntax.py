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

"""Python syntax lint rule for Gemini API Cookbook notebooks.

This module parses every code cell with `ast.parse` so that a cell which cannot
compile is caught before it is published:
  - IPython line magics (`%pip install ...`), shell escapes (`!ls`), and shell
    capture assignments (`files = !ls`) are neutralized first, since they are
    valid in a kernel but not in plain Python.
  - Cells whose first line is a cell magic (`%%bash`, `%%writefile`, ...) are
    skipped entirely, because their body is not Python at all.

Use Cases:
  - Catching unterminated or prematurely closed triple-quoted strings, which
    silently truncate a long prompt or an embedded script and break every cell
    that depends on the names the cell was meant to define.
  - Preventing notebooks from shipping with cells that raise `SyntaxError` on
    the very first run in Colab.
"""

from typing import Any, Dict, List
import ast
import logging
import pathlib
import re

logger = logging.getLogger(__name__)

# Matches a shell capture assignment such as `files = !ls -l`.
SHELL_CAPTURE_REGEX = re.compile(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*\s*=\s*)!.*$')


def strip_ipython_syntax(source: str) -> str:
    """Replaces IPython magics and shell escapes with Python placeholders.

    Line numbers are preserved so that reported positions match the cell source.

    Args:
        source: Raw source of a single code cell.

    Returns:
        The source with every IPython-only line replaced by valid Python.
    """
    cleaned = []
    in_continuation = False

    for line in source.split("\n"):
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        if in_continuation:
            # Trailing part of a magic or shell line; a comment keeps it inert.
            cleaned.append("#")
        else:
            capture_match = SHELL_CAPTURE_REGEX.match(line)
            if capture_match:
                cleaned.append(capture_match.group(1) + capture_match.group(2) + "None")
            elif stripped.startswith("!") or stripped.startswith("%"):
                cleaned.append(indent + "pass")
            else:
                cleaned.append(line)
                continue

        in_continuation = line.rstrip().endswith("\\")

    return "\n".join(cleaned)


def check_code_cell_syntax(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Verifies that every code cell is parseable Python.

    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.

    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking code cell syntax for %s", file_path)
    violations = []
    cells = notebook_data.get("cells", [])

    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue

        src = "".join(cell.get("source", []))
        if not src.strip() or src.lstrip().startswith("%%"):
            # Empty cell, or a cell magic whose body is not Python.
            continue

        try:
            ast.parse(strip_ipython_syntax(src))
        except SyntaxError as e:
            offending_lines = (e.text or "").splitlines()
            snippet = offending_lines[-1].strip() if offending_lines else ""
            violations.append(
                f"Cell {cell_idx}, line {e.lineno}: "
                f"Code cell does not compile as Python ({e.msg}). Found: '{snippet}'"
            )

    return violations
