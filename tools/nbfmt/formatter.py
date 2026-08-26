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

"""Notebook Formatter engine for Gemini API Cookbook.

This module formats Jupyter and Colab notebooks (.ipynb) to ensure clean, consistent diffs:
  - Normalizing JSON indentation and keys.
  - Stripping leading and trailing empty lines from cell sources.
  - Removing empty/blank cells.
  - Cleaning cell metadata and ensuring form display for license cells.
  - Ensuring consistent Colab metadata (ToC visibility, notebook name).
  - Providing testing (--test) and dry-run capabilities to detect unformatted notebooks.

Use Cases:
  - Formatting notebooks locally before committing.
  - Checking formatting compliance in GitHub Actions CI pipelines.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import logging
import os
import pathlib
import re

from tools import config

logger = logging.getLogger(__name__)


def generate_cell_id(source: str, cell_count: int) -> str:
    """Generates a reproducible 12-char SHA-256 cell ID from its source and index."""
    str_to_hash = f"{cell_count} {source}"
    return hashlib.sha256(str_to_hash.encode("utf-8")).hexdigest()[:12]


def del_entries_except(data: Dict[str, Any], keep: List[str]) -> None:
    """Removes keys from a dict that are not in the 'keep' list."""
    to_delete = set(data.keys()) - frozenset(keep)
    for key in to_delete:
        del data[key]


@dataclass
class FormatResult:
    """Outcome of formatting a single notebook file."""
    file_path: pathlib.Path
    is_formatted: bool
    is_valid_json: bool
    is_excluded: bool = False
    message: str = ""


class NotebookFormatter:
    """Coordinates cleaning, formatting, and testing notebook files."""

    def __init__(self, indent: int = 2, remove_outputs: bool = False, verbose: bool = False):
        """Initializes the NotebookFormatter.
        
        Args:
            indent: Number of spaces for JSON formatting (default: 2).
            remove_outputs: Whether to strip code cell outputs (default: False).
            verbose: Enable verbose debug logging.
        """
        self.indent = indent
        self.remove_outputs = remove_outputs
        self.verbose = verbose
        logger.info("Initialized NotebookFormatter (indent=%d, remove_outputs=%s)", indent, remove_outputs)

    def clean_root_metadata(self, data: Dict[str, Any], file_path: pathlib.Path) -> None:
        """Cleans and standardizes top-level notebook fields and metadata."""
        del_entries_except(data, keep=["cells", "metadata", "nbformat_minor", "nbformat"])
        
        metadata = data.get("metadata", {})
        del_entries_except(metadata, keep=["accelerator", "colab", "kernelspec", "google", "language_info"])

        data["nbformat"] = 4
        data["nbformat_minor"] = 0

        # Colab metadata
        colab = metadata.get("colab", {})
        del_entries_except(colab, keep=["collapsed_sections", "name", "toc_visible"])
        colab["name"] = file_path.name
        colab["toc_visible"] = True
        metadata["colab"] = colab

        # Kernelspec metadata
        kernelspec = metadata.get("kernelspec", {})
        del_entries_except(kernelspec, keep=["display_name", "name"])
        kernel_name = kernelspec.get("name", "python3")
        kernelspec["name"] = kernel_name
        kernelspec["display_name"] = "Python 3" if kernel_name == "python3" else kernelspec.get("display_name", "Python 3")
        metadata["kernelspec"] = kernelspec

        data["metadata"] = metadata

    def clean_cells(self, data: Dict[str, Any], file_path: pathlib.Path) -> None:
        """Cleans empty lines, removes empty cells, and ensures valid metadata."""
        cells = data.get("cells", [])
        
        cleaned_cells = []
        cell_count = 0
        for cell in cells:
            source = cell.get("source", [])
            
            # Normalize source to list of strings
            if isinstance(source, str):
                source = source.splitlines(keepends=True)
                
            # Strip leading/trailing blank lines in cell source
            while source and source[0].strip() == "":
                source.pop(0)
            while source and source[-1].strip() == "":
                source.pop()
                
            if not source:
                # Skip empty cells
                continue
                
            # If Colab badge cell, clean accidental literal escaped newlines (e.g. </a>\n)
            if cell.get("cell_type") == "markdown" and any("colab-badge.svg" in line for line in source):
                source = [re.sub(r'</a>\\+n', '</a>', line) for line in source]

            cell["source"] = source
            cell_count += 1
            
            # Clean cell metadata
            metadata = cell.get("metadata", {})
            if "id" not in metadata:
                metadata["id"] = generate_cell_id("".join(source), cell_count)
                
            del_entries_except(metadata, keep=["id", "cellView", "colab", "collapsed"])
            
            # If license cell, set form view
            src_str = "".join(source)
            if config.LICENSE_REGEX.search(src_str):
                metadata["cellView"] = "form"
                
            cell["metadata"] = metadata
            
            if cell.get("cell_type") == "code":
                if self.remove_outputs:
                    cell["outputs"] = []
                    cell["execution_count"] = None
                else:
                    if "outputs" not in cell or cell["outputs"] is None:
                        cell["outputs"] = []
                    if cell.get("execution_count") == 0:
                        cell["execution_count"] = None
                        
            cleaned_cells.append(cell)
            
        data["cells"] = cleaned_cells

    def format_bytes(self, data: Dict[str, Any], file_path: pathlib.Path) -> bytes:
        """Generates clean, formatted JSON bytes for the notebook."""
        self.clean_root_metadata(data, file_path)
        self.clean_cells(data, file_path)
        
        # Serialize to formatted JSON
        formatted_json = json.dumps(
            data,
            sort_keys=True,
            indent=self.indent,
            ensure_ascii=False
        )
        
        # Clean trailing whitespace on each line
        lines = [line.rstrip() for line in formatted_json.splitlines()]
        clean_json_str = "\n".join(lines) + "\n"
        
        # Match standard HTML entity escape conventions
        str_replaces = {"<": r"\u003c", ">": r"\u003e", "&": r"\u0026"}
        for src_char, target_seq in str_replaces.items():
            clean_json_str = clean_json_str.replace(src_char, target_seq)
            
        return clean_json_str.encode("utf-8")

    def format_file(self, file_path: pathlib.Path, dry_run: bool = False, test_only: bool = False) -> FormatResult:
        """Formats or tests a single notebook file.
        
        Args:
            file_path: Path to the notebook file.
            dry_run: If True, do not write changes to disk.
            test_only: If True, check if formatted without modifying.
            
        Returns:
            FormatResult detailing the outcome.
        """
        logger.debug("Processing formatting for %s (test=%s, dry_run=%s)", file_path, test_only, dry_run)
        try:
            raw_bytes = file_path.read_bytes()
            data = json.loads(raw_bytes.decode("utf-8"))
        except Exception as e:
            logger.error("Failed to read/parse notebook %s: %s", file_path, e)
            return FormatResult(
                file_path=file_path,
                is_formatted=False,
                is_valid_json=False,
                message=f"JSON Parse Error: {e}"
            )

        expected_bytes = self.format_bytes(data, file_path)
        is_already_formatted = (raw_bytes == expected_bytes)

        if not is_already_formatted:
            if not dry_run and not test_only:
                file_path.write_bytes(expected_bytes)
                logger.info("Formatted %s", file_path)
                return FormatResult(
                    file_path=file_path,
                    is_formatted=True,
                    is_valid_json=True,
                    message="Formatted successfully."
                )
            else:
                logger.warning("%s requires formatting", file_path)
                return FormatResult(
                    file_path=file_path,
                    is_formatted=False,
                    is_valid_json=True,
                    message="File requires formatting."
                )

        return FormatResult(
            file_path=file_path,
            is_formatted=True,
            is_valid_json=True,
            message="Already formatted."
        )
