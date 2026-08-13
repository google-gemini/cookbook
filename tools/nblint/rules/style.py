"""Style and language lint rules for Gemini API Cookbook notebooks.

This module implements style rules tailored for Gemini developer documentation:
  - Inclusive language check: Flag terms like 'blacklist', 'whitelist', 'master', 'slave'
    with their approved modern alternatives, while deliberately excluding false-positives
    such as 'native' (which is valid Gemini terminology for native audio, native TTS, etc.).
  - Second-person check: Ensures prose is written in second person ('you' rather than 'we'),
    whilst carefully ignoring prompt examples, quoted strings, code, and parameter annotations.
  - Line length check: Identifies excessively long lines in code cells (> 100 chars).

Use Cases:
  - Maintaining clear, inclusive, and didactic technical prose across all guides.
  - Preventing false-positive lint blocks that frustrate authors during PR submissions.
"""

from typing import Any, Dict, List, Tuple
import logging
import pathlib
import re

from tools import config

logger = logging.getLogger(__name__)


def get_cell_lines(cell: Dict[str, Any]) -> List[str]:
    """Helper to extract discrete text lines from cell source."""
    source = cell.get("source", [])
    if isinstance(source, str):
        return source.splitlines()
    lines = []
    for item in source:
        lines.extend(item.splitlines())
    return lines


def check_inclusive_language(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Scans notebook markdown and comments for discouraged terminology.
    
    CRITICAL: 'native' is not flagged here as it is standard Gemini terminology.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking inclusive language for %s", file_path)
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        src = "".join(cell.get("source", []))
        for word, alt in config.INCLUSIVE_LANGUAGE_WORDLIST.items():
            pattern = rf"[^/]\b{word}\b[^/]"
            if re.search(pattern, src, re.IGNORECASE):
                violations.append(
                    f"Cell {cell_idx} ({cell.get('cell_type')}): "
                    f"Found non-inclusive term '{word}'. Prefer '{alt}'."
                )
                
    return violations


def check_second_person(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Ensures narrative text in markdown cells is written in second person ('you' not 'we').
    
    Ignores blockquotes, prompt definitions, form parameter annotations, and inline code.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking second person usage for %s", file_path)
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "markdown":
            continue
            
        lines = get_cell_lines(cell)
        for line_idx, line in enumerate(lines):
            # Check if line should be skipped (e.g. blockquote, code line, form parameter)
            if any(ign_pat.search(line) for ign_pat in config.SECOND_PERSON_IGNORE_LINE_PATTERNS):
                continue
                
            # Strip markdown links and inline code before testing
            cleaned_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
            cleaned_line = re.sub(r'`[^`]+`', '', cleaned_line)
            
            for word, alt in config.SECOND_PERSON_WORDLIST.items():
                pattern = rf"(?<!\w)\b{word}\b(?!\w)"
                if re.search(pattern, cleaned_line, re.IGNORECASE):
                    # Double check it's not inside quotes
                    if '"' in line or "'" in line:
                        # If the entire line is inside a quote/example prompt, ignore
                        if re.search(rf'["\'].*?\b{word}\b.*?["\']', line, re.IGNORECASE):
                            continue
                            
                    violations.append(
                        f"Cell {cell_idx}, line {line_idx + 1}: "
                        f"Prefer second person ('{alt}') instead of first person ('{word}'). Found: '{line.strip()}'"
                    )
                    
    return violations


def check_code_line_length(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    max_length: int = 100,
    is_redirect: bool = False
) -> List[str]:
    """Flags excessively long lines in code cells (> 100 characters).
    
    Ignores URLs, base64 strings, and model form parameter selector annotations.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        max_length: Maximum allowed line length (default 100).
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
            
        lines = get_cell_lines(cell)
        for line_idx, line in enumerate(lines):
            line_str = line.rstrip("\r\n")
            if len(line_str) > max_length:
                # Ignore lines containing URLs or model parameter annotations
                if "http://" in line_str or "https://" in line_str or "# @param" in line_str:
                    continue
                if "base64" in line_str or '"""' in line_str:
                    continue
                    
                violations.append(
                    f"Cell {cell_idx}, line {line_idx + 1}: "
                    f"Code line exceeds {max_length} characters ({len(line_str)} chars): '{line_str[:60]}...'"
                )
                
    return violations
