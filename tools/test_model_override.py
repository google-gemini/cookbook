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

"""Unit tests for tools/nb_tester/model_override.py transformation logic."""

import unittest

import nbformat

from tools.nb_tester.model_override import ModelOverrideTransformer


class TestModelOverrideTransformer(unittest.TestCase):
    """Test suite for ModelOverrideTransformer."""

    def test_prompt_string_literal_preservation(self) -> None:
        """Test that assignments inside multiline strings are not rewritten (#1447)."""
        source = '''prompt = """Translate this Python example without changing it:
MODEL_ID = 'gemini-2.5-flash'
"""
MODEL_ID = "gemini-2.5-flash"
'''
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 1)
        self.assertIn("MODEL_ID = 'gemini-2.5-flash'", transformed)
        self.assertIn('MODEL_ID = "gemini-3.7-flash"', transformed)

    def test_single_line_prompt_string_literal_preservation(self) -> None:
        """Assignments inside single-line string literals must not be rewritten."""
        source = (
            'prompt = "MODEL_ID = \'gemini-2.5-flash\'"\n'
            'MODEL_ID = "gemini-2.5-flash"\n'
        )
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 1)
        self.assertIn("MODEL_ID = 'gemini-2.5-flash'", transformed)
        self.assertIn('MODEL_ID = "gemini-3.7-flash"', transformed)

    def test_docstring_assignment_preservation(self) -> None:
        """Docstrings containing assignment-like lines must remain untouched."""
        source = '''def setup():
    """Setup helper.
    Example:
    MODEL_ID = 'gemini-1.5-pro'
    """
    pass

MODEL_ID = "gemini-2.5-flash"
'''
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 1)
        self.assertIn("MODEL_ID = 'gemini-1.5-pro'", transformed)
        self.assertIn('MODEL_ID = "gemini-3.7-flash"', transformed)

    def test_fstring_multiline_preservation(self) -> None:
        """F-string multiline literals containing model lines must not be modified."""
        source = '''prompt = f"""Run with:
MODEL_ID = 'gemini-1.5-flash'
"""
MODEL_ID = "gemini-2.5-flash"
'''
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 1)
        self.assertIn("MODEL_ID = 'gemini-1.5-flash'", transformed)
        self.assertIn('MODEL_ID = "gemini-3.7-flash"', transformed)

    def test_standard_model_assignments(self) -> None:
        """Standard model assignments in executable code must be rewritten."""
        test_cases = [
            (
                'MODEL_ID = "gemini-2.5-flash"',
                'MODEL_ID = "gemini-3.7-flash"',
            ),
            (
                "MODEL_NAME = 'gemini-2.5-flash'",
                'MODEL_NAME = "gemini-3.7-flash"',
            ),
            (
                'MODEL_ID: str = "gemini-2.5-flash"',
                'MODEL_ID: str = "gemini-3.7-flash"',
            ),
            (
                'model_id = "gemini-2.5-flash"  # @param ["gemini-2.5-flash"]',
                'model_id = "gemini-3.7-flash"  # @param ["gemini-2.5-flash"]',
            ),
            (
                'EMBEDDING_MODEL_ID = MODEL_ID = "gemini-2.5-flash"',
                'EMBEDDING_MODEL_ID = MODEL_ID = "gemini-3.7-flash"',
            ),
        ]
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        for input_code, expected_code in test_cases:
            transformed, count = transformer.transform_cell_source(input_code)
            self.assertEqual(count, 1, f"Failed for {input_code}")
            self.assertEqual(transformed, expected_code)

    def test_models_prefix_preserved(self) -> None:
        """If original model string had 'models/' prefix, the override preserves it."""
        source = 'MODEL_ID = "models/gemini-2.5-flash"'
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 1)
        self.assertEqual(transformed, 'MODEL_ID = "models/gemini-3.7-flash"')

    def test_family_filtering(self) -> None:
        """Specialized model families must not be overwritten by standard text models."""
        source = 'MODEL_ID = "imagen-3.0-generate-002"'
        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 0)
        self.assertEqual(transformed, source)

    def test_inactive_transformer(self) -> None:
        """Inactive transformer (None or empty model) returns code unchanged."""
        source = 'MODEL_ID = "gemini-2.5-flash"'
        transformer = ModelOverrideTransformer(None)
        transformed, count = transformer.transform_cell_source(source)

        self.assertEqual(count, 0)
        self.assertEqual(transformed, source)

    def test_transform_notebook(self) -> None:
        """Transformations apply properly across NotebookNode code cells."""
        nb = nbformat.v4.new_notebook()
        nb.cells.append(nbformat.v4.new_markdown_cell("# Title\nMODEL_ID = 'gemini-1.5'"))
        cell_source = (
            "prompt = \"\"\"MODEL_ID = 'gemini-1.5'\"\"\"\n"
            'MODEL_ID = "gemini-2.5-flash"'
        )
        nb.cells.append(nbformat.v4.new_code_cell(cell_source))

        transformer = ModelOverrideTransformer("gemini-3.7-flash")
        modified_nb, total = transformer.transform_notebook(nb, "test.ipynb")

        self.assertEqual(total, 1)
        self.assertIn("gemini-3.7-flash", modified_nb.cells[1].source)
        self.assertIn(
            "prompt = \"\"\"MODEL_ID = 'gemini-1.5'\"\"\"",
            modified_nb.cells[1].source,
        )


if __name__ == "__main__":
    unittest.main()
