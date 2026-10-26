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

"""Unit tests for tools/check_readme_links.py notebook README linking."""

import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from tools import check_readme_links as checker


class TestIsNotebookLinked(unittest.TestCase):
    """Verify README link destinations resolve to the target notebook path."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = pathlib.Path(self.temp_dir.name).resolve()
        self._root_patch = mock.patch.object(checker, "repo_root", self.repo_root)
        self._root_patch.start()

        self.new_nb = self.repo_root / "examples/new/demo.ipynb"
        self.old_nb = self.repo_root / "examples/old/demo.ipynb"
        for notebook in (self.new_nb, self.old_nb):
            notebook.parent.mkdir(parents=True)
            notebook.write_text(
                '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}',
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self._root_patch.stop()
        self.temp_dir.cleanup()

    def test_same_basename_different_path_is_unlinked(self) -> None:
        (self.repo_root / "README.md").write_text(
            "[Old tutorial](examples/old/demo.ipynb)\n",
            encoding="utf-8",
        )
        linked, found = checker.is_notebook_linked(self.new_nb)
        self.assertFalse(linked)
        self.assertEqual(found, [])

    def test_prose_basename_mention_is_unlinked(self) -> None:
        (self.repo_root / "README.md").write_text(
            "Remember to add demo.ipynb to the table of contents.\n",
            encoding="utf-8",
        )
        linked, found = checker.is_notebook_linked(self.new_nb)
        self.assertFalse(linked)
        self.assertEqual(found, [])

    def test_correct_relative_link_is_linked(self) -> None:
        (self.repo_root / "README.md").write_text(
            "[New tutorial](examples/new/demo.ipynb)\n",
            encoding="utf-8",
        )
        linked, found = checker.is_notebook_linked(self.new_nb)
        self.assertTrue(linked)
        self.assertEqual(found, ["README.md"])

    def test_colab_blob_url_counts_as_link(self) -> None:
        (self.repo_root / "README.md").write_text(
            "[![Colab](https://img)]"
            "(https://colab.research.google.com/github/google-gemini/cookbook/"
            "blob/main/examples/new/demo.ipynb)\n",
            encoding="utf-8",
        )
        linked, found = checker.is_notebook_linked(self.new_nb)
        self.assertTrue(linked)
        self.assertEqual(found, ["README.md"])

    def test_section_readme_relative_link(self) -> None:
        examples_readme = self.repo_root / "examples" / "README.md"
        examples_readme.write_text(
            "[Demo](./new/demo.ipynb)\n",
            encoding="utf-8",
        )
        linked, found = checker.is_notebook_linked(self.new_nb)
        self.assertTrue(linked)
        self.assertEqual(found, ["examples/README.md"])


if __name__ == "__main__":
    unittest.main()
