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

"""Structural lint rules for Gemini API Cookbook notebooks.

This module implements lint checks verifying essential notebook structure:
  - Copyright statement in cell 0.
  - Collapsed Apache 2.0 license code cell.
  - Colab badge button with the correct relative path and repository URL.
  - 'Next Steps' or 'What's Next' closing section.

Use Cases:
  - Validating that all published notebooks comply with open source licensing requirements.
  - Ensuring the 'Run in Google Colab' badge opens the exact corresponding notebook in GitHub.
  - Flagging missing concluding sections that provide readers with onward learning paths.
"""

from typing import Any, Dict, List, Optional
import logging
import pathlib
import re

from tools import config

logger = logging.getLogger(__name__)


def check_copyright(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Validates the presence of an approved copyright notice in the first cell.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of error messages (empty if check passed).
    """
    logger.debug("Checking copyright header for %s", file_path)
    cells = notebook_data.get("cells", [])
    if not cells:
        return ["Notebook is empty (no cells found)."]
        
    # Check first cell for copyright
    first_cell_src = "".join(cells[0].get("source", []))
    if any(regex.search(first_cell_src) for regex in config.COPYRIGHT_REGEXES):
        return []
        
    # Also check cell 1 if cell 0 was metadata or empty
    if len(cells) > 1:
        second_cell_src = "".join(cells[1].get("source", []))
        if any(regex.search(second_cell_src) for regex in config.COPYRIGHT_REGEXES):
            return []
            
    return [
        f"Missing copyright header in first cell. Expected 'Copyright {config.COPYRIGHT_REGEXES[0].pattern}'"
    ]


def check_license_cell(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Validates that the notebook contains a collapsed Apache 2.0 license code cell.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of error messages (empty if check passed).
    """
    logger.debug("Checking Apache 2.0 license cell for %s", file_path)
    cells = notebook_data.get("cells", [])
    
    for cell in cells[:4]:  # License is expected near the top
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            if config.LICENSE_REGEX.search(src):
                return []
                
    return ["Missing collapsed Apache 2.0 license code cell with '# @title Licensed under the Apache License'"]


def check_colab_button(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    repo: str = config.DEFAULT_REPO,
    branch: str = config.DEFAULT_BRANCH,
    is_redirect: bool = False
) -> List[str]:
    """Validates the Colab button image badge and destination URL.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        repo: Repository slug, e.g. 'google-gemini/cookbook'.
        branch: Target Git branch, e.g. 'main'.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of error messages (empty if check passed).
    """
    logger.debug("Checking Colab button for %s", file_path)
    if is_redirect:
        logger.info("Skipping strict Colab button URL check for redirect stub %s", file_path)
        return []
        
    cells = notebook_data.get("cells", [])
    try:
        repo_root = pathlib.Path(__file__).resolve().parent.parent.parent.parent
        expected_rel_path = pathlib.Path(file_path).resolve().relative_to(repo_root).as_posix()
    except ValueError:
        expected_rel_path = str(file_path).replace("\\", "/")
        if expected_rel_path.startswith("./"):
            expected_rel_path = expected_rel_path[2:]
        
    expected_url = f"{config.COLAB_BASE_URL}/{repo}/blob/{branch}/{expected_rel_path}"
    
    found_button_cell = False
    for cell in cells[:5]:  # Button is usually in the first few cells
        if cell.get("cell_type") == "markdown":
            src = "".join(cell.get("source", []))
            if config.COLAB_BUTTON_IMG_REGEX.search(src):
                found_button_cell = True
                if expected_url in src:
                    return []
                # Check if href URL exists
                href_match = config.COLAB_BUTTON_HREF_REGEX.search(src)
                actual_url = href_match.group(1) if href_match else "URL not found"
                return [
                    f"Colab button URL mismatch.\n"
                    f"  Expected: {expected_url}\n"
                    f"  Found:    {actual_url}"
                ]
                
    if not found_button_cell:
        return ["Missing 'Open In Colab' button badge near the top of the notebook."]
        
    return []


def check_next_steps(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Validates that the notebook concludes with a 'Next Steps' or 'What's Next' section.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of error messages / warnings (empty if check passed).
    """
    if is_redirect:
        return []
        
    cells = notebook_data.get("cells", [])
    if len(cells) < 5:
        return []
        
    # Check the last 3 markdown cells
    md_cells = [c for c in cells if c.get("cell_type") == "markdown"]
    for cell in md_cells[-3:]:
        src = "".join(cell.get("source", [])).lower()
        if re.search(r'#+\s*(?:next\s+steps|what\'?s\s+next|learn\s+more|conclusion)', src):
            return []
            
    return ["Missing recommended 'Next Steps' or 'What's Next' section at the end of the notebook."]
