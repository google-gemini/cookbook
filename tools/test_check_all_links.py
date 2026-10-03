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

"""Unit tests for tools/check_all_links.py link verification logic."""

import json
import pathlib
import tempfile
import unittest

from tools.check_all_links import (
    LinkCheckerConfig,
    extract_anchors_from_content,
    extract_links_from_file,
    slugify_heading,
    validate_internal_link,
)


class TestCheckAllLinks(unittest.TestCase):
    """Test suite for repository link validation tool."""

    def setUp(self) -> None:
        """Create a temporary sandbox repository structure for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = pathlib.Path(self.temp_dir.name).resolve()

        # Create dummy structure:
        # README.md
        # quickstarts/
        #   guide.md
        #   sample.ipynb
        self.quickstarts_dir = self.repo_root / "quickstarts"
        self.quickstarts_dir.mkdir(parents=True)

        self.readme_path = self.repo_root / "README.md"
        self.readme_path.write_text(
            "# Cookbook Overview\n\n"
            "Welcome! See [Guide](./quickstarts/guide.md) or [Guide Anchor](./quickstarts/guide.md#advanced-topics).\n"
            "Check [Placeholder](URL) and [In-page](#cookbook-overview).\n",
            encoding="utf-8",
        )

        self.guide_path = self.quickstarts_dir / "guide.md"
        self.guide_path.write_text(
            "# Developer Guide\n\n"
            "<a name=\"custom_anchor\"></a>\n"
            "## Advanced Topics\n\n"
            "Details here. Back to [Root](../README.md).\n"
            "Broken relative link: [Dead](./does_not_exist.md).\n"
            "Escaping link: [Escape](../../outside.md).\n"
            "Image data: ![diagram](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=)\n",
            encoding="utf-8",
        )

        dummy_ipynb = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "id": "cell-intro-123",
                    "metadata": {},
                    "source": [
                        "# Getting Started with Notebooks\n",
                        "Link to [Guide](guide.md#custom_anchor) and [Missing Anchor](guide.md#nonexistent).\n",
                    ],
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        self.ipynb_path = self.quickstarts_dir / "sample.ipynb"
        self.ipynb_path.write_text(json.dumps(dummy_ipynb), encoding="utf-8")

        self.config = LinkCheckerConfig(repo_root=self.repo_root, internal_only=True)

    def tearDown(self) -> None:
        """Clean up temporary directory."""
        self.temp_dir.cleanup()

    def test_slugify_heading(self) -> None:
        """Verifies GitHub heading slug conversion."""
        self.assertEqual(slugify_heading("Hello World"), "hello-world")
        self.assertEqual(slugify_heading("## Quickstart: Step 1 (Setup)"), "quickstart-step-1-setup")
        self.assertEqual(slugify_heading("Title With <code>Tags</code>"), "title-with-tags")

    def test_extract_anchors_from_content(self) -> None:
        """Verifies anchor extraction from both Markdown headings and HTML anchor tags."""
        content = (
            "# Top Heading\n\n"
            "<a name=\"my_target\"></a>\n"
            "<a id=\"secondary_id\"></a>\n"
            "## Sub-Section (Alpha)\n"
        )
        anchors = extract_anchors_from_content(content)
        self.assertIn("top-heading", anchors)
        self.assertIn("my_target", anchors)
        self.assertIn("secondary_id", anchors)
        self.assertIn("sub-section-alpha", anchors)

    def test_extract_links_skips_data_uris(self) -> None:
        """Verifies that inline base64 image data URIs are not treated as target file links."""
        links = extract_links_from_file(self.guide_path)
        urls = [u for u, _ in links]
        self.assertIn("../README.md", urls)
        self.assertIn("./does_not_exist.md", urls)
        self.assertIn("../../outside.md", urls)
        # Verify base64 data URI is extracted as raw string but ignored by patterns
        self.assertTrue(any(u.startswith("data:image/") for u in urls))

    def test_validate_internal_link_success(self) -> None:
        """Verifies valid local and cross-file anchor links pass validation."""
        ok, err = validate_internal_link(self.readme_path, "./quickstarts/guide.md", self.config)
        self.assertTrue(ok, err)

        ok, err = validate_internal_link(self.readme_path, "./quickstarts/guide.md#advanced-topics", self.config)
        self.assertTrue(ok, err)

        ok, err = validate_internal_link(self.ipynb_path, "guide.md#custom_anchor", self.config)
        self.assertTrue(ok, err)

        # In-page anchor
        ok, err = validate_internal_link(self.readme_path, "#cookbook-overview", self.config)
        self.assertTrue(ok, err)

        # Template placeholder
        ok, err = validate_internal_link(self.readme_path, "URL", self.config)
        self.assertTrue(ok, err)

    def test_validate_internal_link_failures(self) -> None:
        """Verifies dead links, missing anchors, and path escapes are correctly caught."""
        # Nonexistent local file
        ok, err = validate_internal_link(self.guide_path, "./does_not_exist.md", self.config)
        self.assertFalse(ok)
        self.assertIn("File does not exist", err)

        # Escapes repository root
        ok, err = validate_internal_link(self.guide_path, "../../outside.md", self.config)
        self.assertFalse(ok)
        self.assertIn("escapes repository root", err)

        # Missing anchor target
        ok, err = validate_internal_link(self.ipynb_path, "guide.md#nonexistent", self.config)
        self.assertFalse(ok)
        self.assertIn("Anchor '#nonexistent' not found", err)


if __name__ == "__main__":
    unittest.main()
