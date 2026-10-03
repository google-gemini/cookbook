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

"""Regression tests for notebook model-selector validation."""

import json
import pathlib
import tempfile
import unittest

from tools.nblint.linter import NotebookLinter
from tools.nblint.rules.model_selector import check_model_selector


def make_notebook(options):
    """Builds a notebook containing a single model selector."""
    return {
        "cells": [
            {
                "cell_type": "code",
                "source": [f'MODEL_ID = "gemini-3.7-flash" # @param {options}\n'],
            }
        ],
    }


class ModelSelectorTest(unittest.TestCase):
    """Checks selector diagnostics and continued multi-notebook linting."""

    def test_empty_option_arrays_are_errors(self):
        for options in ("[]", "[   ]"):
            with self.subTest(options=options):
                violations = check_model_selector(
                    make_notebook(options), pathlib.Path("sample.ipynb")
                )
                self.assertEqual(len(violations), 1)
                self.assertTrue(violations[0][1])
                self.assertIn("non-empty list", violations[0][0])

    def test_non_string_options_are_errors(self):
        for option in (None, 42, True, {}):
            with self.subTest(option=option):
                options = json.dumps(["gemini-3.7-flash", option])
                violations = check_model_selector(
                    make_notebook(options), pathlib.Path("sample.ipynb")
                )
                self.assertEqual(len(violations), 1)
                self.assertTrue(violations[0][1])
                self.assertIn("model names", violations[0][0])

    def test_valid_string_options_remain_supported(self):
        for options in (
            '["gemini-3.7-flash", "gemini-3.5-flash-lite"]',
            "['gemini-3.7-flash', 'gemini-3.5-flash-lite']",
        ):
            with self.subTest(options=options):
                self.assertEqual(
                    check_model_selector(
                        make_notebook(options), pathlib.Path("sample.ipynb")
                    ),
                    [],
                )

    def test_missing_default_is_still_an_error(self):
        violations = check_model_selector(
            make_notebook('["gemini-3.5-flash-lite"]'),
            pathlib.Path("sample.ipynb"),
        )
        self.assertEqual(len(violations), 1)
        self.assertTrue(violations[0][1])
        self.assertIn("not listed", violations[0][0])

    def test_invalid_selector_does_not_abort_linting_other_notebooks(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [
                pathlib.Path(directory) / name
                for name in ("invalid.ipynb", "valid.ipynb")
            ]
            for path, options in zip(
                paths, ('["gemini-3.7-flash", null]', '["gemini-3.7-flash"]')
            ):
                path.write_text(json.dumps(make_notebook(options)), encoding="utf-8")

            results = NotebookLinter().lint_files(paths)

        self.assertEqual(len(results), 2)
        selector_errors = [
            diagnostic
            for diagnostic in results[0].diagnostics
            if diagnostic.rule_name == "gemini::model_selector"
        ]
        self.assertEqual(len(selector_errors), 1)
        self.assertFalse(
            any(
                diagnostic.rule_name == "gemini::model_selector"
                for diagnostic in results[1].diagnostics
            )
        )


if __name__ == "__main__":
    unittest.main()
