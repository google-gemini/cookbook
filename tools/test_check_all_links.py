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

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from tools.check_all_links import (
    LinkCheckerConfig,
    extract_anchors_from_content,
    extract_links_from_file,
    get_changed_files_from_git,
    get_file_anchors,
    main,
    normalize_cell_source,
    run_link_audit,
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

    def test_normalize_cell_source(self) -> None:
        """Verifies cell source normalization across None, str, list, and invalid types."""
        # None source
        self.assertEqual(normalize_cell_source(None), [])
        # Single string
        self.assertEqual(normalize_cell_source("Single line"), ["Single line"])
        # Multiline string
        self.assertEqual(
            normalize_cell_source("Line 1\nLine 2\n"),
            ["Line 1\n", "Line 2\n"],
        )
        # List of strings
        self.assertEqual(
            normalize_cell_source(["# Heading\n", "Content line\n"]),
            ["# Heading\n", "Content line\n"],
        )
        # List with non-string elements filtered out
        self.assertEqual(
            normalize_cell_source(["# Heading\n", None, 42, "Valid\n"]),
            ["# Heading\n", "Valid\n"],
        )
        # Invalid types
        self.assertEqual(normalize_cell_source(123), [])
        self.assertEqual(normalize_cell_source({}), [])

    def test_extract_links_handles_source_variations(self) -> None:
        """Verifies link extraction when notebook cell source is a string or None."""
        nb_str_source = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": "# Intro\nCheck [Docs](https://example.com/docs) and <a href=\"https://example.com/api\">API</a>.\n",
                },
                {
                    "cell_type": "markdown",
                    "source": None,
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        nb_path = self.repo_root / "quickstarts" / "str_source.ipynb"
        nb_path.write_text(json.dumps(nb_str_source), encoding="utf-8")

        links = extract_links_from_file(nb_path)
        urls = [u for u, _ in links]
        self.assertIn("https://example.com/docs", urls)
        self.assertIn("https://example.com/api", urls)
        self.assertEqual(len(links), 2)

    def test_get_file_anchors_handles_source_variations(self) -> None:
        """Verifies anchor extraction when notebook cell source is None or a string."""
        nb_variations = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": "# String Heading\n<a name=\"custom-html-anchor\"></a>\n",
                },
                {
                    "cell_type": "markdown",
                    "source": None,
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        nb_path = self.repo_root / "quickstarts" / "anchor_test.ipynb"
        nb_path.write_text(json.dumps(nb_variations), encoding="utf-8")

        anchors = get_file_anchors(nb_path, self.config)
        self.assertIn("string-heading", anchors)
        self.assertIn("custom-html-anchor", anchors)

    def test_uppercase_scheme_link_handling(self) -> None:
        """Verifies uppercase HTTP(S) schemes are treated as external and not local paths."""
        # In validate_internal_link, external URLs should be skipped
        ok, err = validate_internal_link(self.readme_path, "HTTPS://example.com/resource", self.config)
        self.assertTrue(ok, err)

        ok, err = validate_internal_link(self.readme_path, "Http://google.com/test", self.config)
        self.assertTrue(ok, err)

        # In run_link_audit, an uppercase external URL in a file should not trigger a broken link when internal_only=True
        nb_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "source": ["Link to [External](HTTPS://example.com/docs)\n"],
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4,
        }
        nb_path = self.repo_root / "quickstarts" / "https_test.ipynb"
        nb_path.write_text(json.dumps(nb_content), encoding="utf-8")

        exit_code = run_link_audit(self.config, explicit_files=[str(nb_path)])
        self.assertEqual(exit_code, 0)

    def test_github_blob_url_with_query_params_and_casing(self) -> None:
        """Verifies GitHub blob URL validation strips query parameters and ignores scheme case."""
        # Valid GitHub blob URL with query params
        ok, err = validate_internal_link(
            self.readme_path,
            "https://github.com/google-gemini/cookbook/blob/main/README.md?raw=true",
            self.config,
        )
        self.assertTrue(ok, err)

        # Valid GitHub blob URL with query params, anchor fragment, and uppercase HTTPS
        ok, err = validate_internal_link(
            self.readme_path,
            "HTTPS://github.com/google-gemini/cookbook/blob/main/README.md?plain=1#cookbook-overview",
            self.config,
        )
        self.assertTrue(ok, err)

        # Nonexistent target file with query params returns clean error message
        ok, err = validate_internal_link(
            self.readme_path,
            "https://github.com/google-gemini/cookbook/blob/main/nonexistent.md?raw=true",
            self.config,
        )
        self.assertFalse(ok)
        self.assertIn("nonexistent.md", err)
        self.assertNotIn("?raw=true", err)

    def test_changed_files_stops_at_available_base_without_documents(self) -> None:
        """An empty document diff must not select changes from an older base."""
        for diff in ("", "tools/check_all_links.py\n"):
            with self.subTest(diff=diff):
                with mock.patch(
                    "tools.check_all_links.subprocess.check_output",
                    side_effect=[diff, "quickstarts/guide.md\n"],
                ):
                    self.assertEqual(get_changed_files_from_git(self.repo_root), [])

    def test_changed_files_falls_back_when_base_is_unavailable(self) -> None:
        """An unavailable upstream ref still falls back to origin and filters paths."""
        with mock.patch(
            "tools.check_all_links.subprocess.check_output",
            side_effect=[
                subprocess.CalledProcessError(128, "git diff"),
                "README.md\ntools/check_all_links.py\nquickstarts/sample.ipynb\n",
            ],
        ):
            self.assertEqual(
                get_changed_files_from_git(self.repo_root),
                ["README.md", "quickstarts/sample.ipynb"],
            )

    def test_changed_cli_skips_unrelated_broken_links(self) -> None:
        """No document changes against origin must not audit an older broken guide."""
        for diff in ("", "tools/check_all_links.py\n"):
            with self.subTest(diff=diff):
                output = io.StringIO()
                with (
                    mock.patch(
                        "tools.check_all_links.subprocess.check_output",
                        side_effect=[
                            subprocess.CalledProcessError(128, "git diff"),
                            diff,
                            "quickstarts/guide.md\n",
                        ],
                    ),
                    mock.patch.object(
                        sys,
                        "argv",
                        ["check_all_links.py", "--repo-dir", str(self.repo_root), "--changed"],
                    ),
                    contextlib.redirect_stdout(output),
                    self.assertRaises(SystemExit) as exit_context,
                ):
                    main()
                self.assertEqual(exit_context.exception.code, 0, output.getvalue())
                self.assertIn("No modified .md or .ipynb files detected", output.getvalue())

    def test_changed_files_returns_none_when_no_base_is_available(self) -> None:
        """Unavailable comparison bases must be distinct from an empty diff."""
        with (
            mock.patch(
                "tools.check_all_links.subprocess.check_output",
                side_effect=subprocess.CalledProcessError(128, "git diff"),
            ),
            self.assertLogs("link_checker", level="WARNING"),
        ):
            self.assertIsNone(get_changed_files_from_git(self.repo_root))

    def test_changed_cli_audits_all_files_when_no_base_is_available(self) -> None:
        """A Git repository without commits must still report broken links."""
        subprocess.run(["git", "init", "--quiet"], cwd=self.repo_root, check=True)
        result = subprocess.run(
            [
                sys.executable,
                str(pathlib.Path(__file__).with_name("check_all_links.py")),
                "--repo-dir",
                str(self.repo_root),
                "--changed",
            ],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("Falling back to all files", result.stderr)
        self.assertIn("Scanning 3 file(s)", result.stderr)
        self.assertIn("quickstarts/guide.md", result.stdout)
        self.assertIn("quickstarts/sample.ipynb", result.stdout)
        self.assertNotIn("No modified .md or .ipynb files detected", result.stdout)


if __name__ == "__main__":
    unittest.main()
