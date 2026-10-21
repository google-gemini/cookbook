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

"""Offline regression tests for notebook code cell syntax checks."""

import pathlib
import unittest

from tools.nblint.rules import syntax


class CodeCellSyntaxTest(unittest.TestCase):

    def check_source(self, source):
        notebook = {"cells": [{"cell_type": "code", "source": source}]}
        return syntax.check_code_cell_syntax(notebook, pathlib.Path("example.ipynb"))

    def test_invalid_timed_python_reports_original_line(self):
        for header in ("%%time", "%%time --no-raise-error", "\n%%time"):
            with self.subTest(header=header):
                violations = self.check_source(header + "\nvalue = 1\nbroken =")
                self.assertEqual(len(violations), 1)
                expected_line = header.count("\n") + 3
                self.assertIn(f"Cell 0, line {expected_line}:", violations[0])
                self.assertIn("broken =", violations[0])

    def test_valid_timed_python(self):
        self.assertEqual(self.check_source("%%time\nvalue = sum(range(10))\nprint(value)"), [])

    def test_timed_python_with_ipython_syntax(self):
        source = "%%time\n%pip install google-genai\nfiles = !ls\nprint(files)"
        self.assertEqual(self.check_source(source), [])

    def test_timed_python_with_list_source(self):
        violations = self.check_source(["%%time\n", "broken ="])
        self.assertEqual(len(violations), 1)
        self.assertIn("Cell 0, line 2:", violations[0])

    def test_other_cell_magics_remain_skipped(self):
        for header in ("%%bash", "%%writefile data.txt", "%%time_custom"):
            with self.subTest(header=header):
                self.assertEqual(self.check_source(header + "\nnot valid Python!"), [])

    def test_ordinary_python_still_checked(self):
        self.assertEqual(self.check_source("value = 1"), [])
        self.assertEqual(len(self.check_source("broken =")), 1)

    def test_empty_cells(self):
        for source in ("", "\n", []):
            with self.subTest(source=source):
                self.assertEqual(self.check_source(source), [])


if __name__ == "__main__":
    unittest.main()
