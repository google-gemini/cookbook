#!/usr/bin/env python3
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

"""Unit tests for tools/nblint/rules/syntax.py code cell validation."""

import pathlib
import unittest

from tools.nblint.rules.syntax import check_code_cell_syntax, strip_ipython_syntax


class TestSyntaxRule(unittest.TestCase):
    def setUp(self) -> None:
        self.dummy_path = pathlib.Path("dummy.ipynb")

    def test_multiline_string_containing_magic_like_lines(self) -> None:
        source = (
            'prompt = """Follow this instruction:\n'
            '! Keep the answer short.\n'
            '% This is a LaTeX comment."""\n'
            'print(prompt)'
        )
        notebook = {"cells": [{"cell_type": "code", "source": source}]}
        violations = check_code_cell_syntax(notebook, self.dummy_path)
        self.assertEqual(violations, [])

    def test_strip_ipython_magics_and_shell_escapes(self) -> None:
        source = (
            "!pip install -q google-genai\n"
            "%matplotlib inline\n"
            "files = !ls -la\n"
            "!echo hello \\\n"
            "  world\n"
            "x = 1"
        )
        notebook = {"cells": [{"cell_type": "code", "source": source}]}
        violations = check_code_cell_syntax(notebook, self.dummy_path)
        self.assertEqual(violations, [])

    def test_unterminated_multiline_string_detected(self) -> None:
        source = (
            'prompt = """Follow this instruction:\n'
            '! Keep the answer short.\n'
            'print(prompt)'
        )
        notebook = {"cells": [{"cell_type": "code", "source": source}]}
        violations = check_code_cell_syntax(notebook, self.dummy_path)
        self.assertEqual(len(violations), 1)
        self.assertIn("unterminated triple-quoted string literal", violations[0])

    def test_real_syntax_error_detected(self) -> None:
        source = "def broken(\n    return 42"
        notebook = {"cells": [{"cell_type": "code", "source": source}]}
        violations = check_code_cell_syntax(notebook, self.dummy_path)
        self.assertEqual(len(violations), 1)
        self.assertIn("Code cell does not compile as Python", violations[0])


if __name__ == "__main__":
    unittest.main()
