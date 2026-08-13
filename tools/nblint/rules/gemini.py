"""Gemini SDK, API keys, and environment lint rules for Cookbook notebooks.

This module validates best practices for Gemini API SDK usage:
  - Enforcing `%pip install` instead of `!pip install` for reliable IPython kernel installs.
  - Ensuring the official modern SDK (`google-genai`) is used, flagging obsolete `google.generativeai`.
  - Verifying the use of `GEMINI_API_KEY` rather than the legacy `GOOGLE_API_KEY` Colab secret.
  - Detecting and preventing hardcoded API keys (e.g. `AIza...`) from being committed to the repo.

Use Cases:
  - Guiding contributors towards the modern `google-genai` SDK patterns.
  - Preventing broken dependencies and runtime package resolution errors in Colab.
  - Protecting developers against secret exposure and credential leakage.
"""

from typing import Any, Dict, List
import logging
import pathlib
import re

from tools import config

logger = logging.getLogger(__name__)


def check_pip_install_syntax(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Ensures notebook uses '%pip install' instead of '!pip install'.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking pip install syntax for %s", file_path)
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
            
        src = "".join(cell.get("source", []))
        if config.PIP_BANG_INSTALL_REGEX.search(src):
            violations.append(
                f"Cell {cell_idx}: Use '%pip install' instead of '!pip install' "
                f"to guarantee installation into the active Jupyter kernel."
            )
            
    return violations


def check_sdk_package(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Verifies that the modern google-genai SDK is imported instead of legacy google.generativeai.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking SDK imports for %s", file_path)
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
            
        src = "".join(cell.get("source", []))
        if f"import {config.LEGACY_SDK_MODULE}" in src or f"from {config.LEGACY_SDK_MODULE}" in src:
            violations.append(
                f"Cell {cell_idx}: Uses deprecated SDK '{config.LEGACY_SDK_MODULE}'. "
                f"Please update to the official SDK: 'from google import genai' ('{config.RECOMMENDED_SDK_PACKAGE}')."
            )
            
    return violations


def check_api_key_secret_name(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Checks that the notebook requests 'GEMINI_API_KEY' instead of legacy 'GOOGLE_API_KEY'.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking API key secret name for %s", file_path)
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
            
        src = "".join(cell.get("source", []))
        if re.search(r'userdata\.get\s*\(\s*[\'"]GOOGLE_API_KEY[\'"]\s*\)', src):
            violations.append(
                f"Cell {cell_idx}: Uses legacy secret name 'GOOGLE_API_KEY'. "
                f"Please use 'userdata.get(\"{config.RECOMMENDED_API_KEY_SECRET}\")'."
            )
            
    return violations


def check_no_hardcoded_api_keys(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Scans all cells to ensure no plaintext Google/Gemini API keys (AIza... or AQ.Ab8...) are present.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Scanning for hardcoded API keys in %s", file_path)
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        src = "".join(cell.get("source", []))
        for regex in config.HARDCODED_API_KEY_REGEXES:
            match = regex.search(src)
            if match:
                matched_snippet = match.group(0)[:8] + "..."
                violations.append(
                    f"Cell {cell_idx} ({cell.get('cell_type')}): "
                    f"CRITICAL: Potential hardcoded Google/Gemini API key detected ('{matched_snippet}'). "
                    f"Remove the key immediately and obtain it from Colab secrets or environment variables."
                )
                break
            
    return violations
