"""Centralized configuration for Gemini API Cookbook linting and formatting tools.

This module provides all configurable parameters, regular expressions, wordlists,
model hierarchies, and file exclusion lists used by `nblint` and `nbfmt`.
By centralizing all configuration here, maintainers can easily update model names,
adjust style guidelines, or add excluded files in one single location.

Use Cases:
  - Defining model ordering rules and valid model lists for model selector validation.
  - Specifying inclusive language wordlists (explicitly omitting false-positive words like 'native').
  - Configuring second-person enforcement wordlists and regex filters.
  - Maintaining the list of files excluded from automated CI checks (e.g. templates, stubs).
  - Centralizing default repository and branch constants.
"""

from typing import Dict, List, Set, Pattern
import re

# ==============================================================================
# Repository & Branch Defaults
# ==============================================================================

DEFAULT_REPO: str = "google-gemini/cookbook"
DEFAULT_BRANCH: str = "main"
COLAB_BASE_URL: str = "https://colab.research.google.com/github"

# ==============================================================================
# File Exclusion Configuration
# ==============================================================================

# Files and glob patterns that should be excluded from full automated linting.
# Note: Template notebook contains intentional placeholders.
EXCLUDED_NOTEBOOKS: Set[str] = {
    "quickstarts/Template.ipynb",
    "examples/Object_detection.ipynb",
    "examples/Google_IO2025_Live_Coding.ipynb",
}

# Directories containing tooling or workflows that should be ignored for README checks.
IGNORED_NOTEBOOK_DIRS: Set[str] = {
    "tools",
    ".github",
    ".devcontainer",
    ".jetski_venv",
}

# Substring indicators that identify a notebook as a "redirect / stub" notebook.
# Redirect notebooks only contain a pointer to a new location.
REDIRECT_KEYWORDS: List[str] = [
    "has moved to",
    "this colab has moved",
    "moved to https://",
    "redirect",
]

# Max cells for a notebook to be considered a stub/redirect notebook candidate
MAX_REDIRECT_CELL_COUNT: int = 4

# ==============================================================================
# Inclusive Language Configuration
# ==============================================================================

# Wordlist mapping deprecated/discouraged words to their recommended alternatives.
# CRITICAL: "native" is deliberately EXCLUDED from this list because in the Gemini API
# context, terms like "native audio", "native TTS", "native multimodal output",
# "native tool calling", and model names (e.g., gemini-2.5-flash-native-audio-preview)
# are official technical terminology and must not trigger false positives.
INCLUSIVE_LANGUAGE_WORDLIST: Dict[str, str] = {
    "blacklist": "blocklist / denylist",
    "whitelist": "allowlist",
    "master": "primary / main",
    "slave": "replica / secondary",
}

# ==============================================================================
# Second Person Configuration
# ==============================================================================

# Words that violate the second-person ("you" not "we") documentation style.
SECOND_PERSON_WORDLIST: Dict[str, str] = {
    "we": "you",
    "we're": "you are",
}

# Markdown cell elements to ignore when checking for second person (e.g. quotes, prompt strings)
SECOND_PERSON_IGNORE_LINE_PATTERNS: List[Pattern] = [
    re.compile(r'^\s*>\s*'),  # Blockquotes
    re.compile(r'^\s*`.*`\s*$'),  # Full inline code lines
    re.compile(r'^\s*#\s*@param'),  # Form parameter annotations
    re.compile(r'^\s*text_prompt\s*='),  # Prompt string variables
    re.compile(r'^\s*prompt\s*='),  # Prompt string variables
]

# ==============================================================================
# Gemini SDK & API Best Practices Configuration
# ==============================================================================

# Correct SDK package and module names
RECOMMENDED_SDK_PACKAGE: str = "google-genai"
RECOMMENDED_SDK_MIN_VERSION: str = "2.9.0"
LEGACY_SDK_MODULE: str = "google.generativeai"

# Recommended secret / environment variable name for API key
RECOMMENDED_API_KEY_SECRET: str = "GEMINI_API_KEY"
LEGACY_API_KEY_SECRET: str = "GOOGLE_API_KEY"

# Regex patterns to catch accidentally hardcoded Google / Gemini API keys:
# 1. Legacy Google API key format: AIzaSy...
# 2. Modern Google / Gemini API key format: AQ.Ab8RN6...
HARDCODED_API_KEY_REGEXES: List[Pattern] = [
    re.compile(r'\bAIza[0-9A-Za-z-_]{30,}\b'),
    re.compile(r'\bAQ\.[0-9A-Za-z-_]{20,}\b'),
]

# Patterns indicating pip installs in code cells
PIP_BANG_INSTALL_REGEX: Pattern = re.compile(r'^\s*!pip\s+install', re.MULTILINE)
PIP_MAGIC_INSTALL_REGEX: Pattern = re.compile(r'^\s*%pip\s+install', re.MULTILINE)

# ==============================================================================
# Model Selector Configuration & Hierarchy
# ==============================================================================

# Regex to detect Colab form model selectors
# e.g.: MODEL_ID = "gemini-3.5-flash" # @param ["gemini-3.1-flash-lite", "gemini-3.5-flash", ...]
MODEL_PARAM_SELECTOR_REGEX: Pattern = re.compile(
    r'(?:MODEL_ID|model_id|MODEL|model)\s*=\s*["\']([^"\']+)["\']\s*#\s*@param\s*(\[[^\]]+\])',
    re.MULTILINE
)

def get_model_sort_key(model_name: str) -> int:
    """Computes a numeric sort key for ordering Gemini models according to style guide.
    
    Order:
      1. Tier: Flash-Lite (1000) -> Flash (2000) -> Pro (3000) -> Other (4000+)
      2. Preview / Experimental penalty (+500)
      3. Generation version (higher minor/major version before or after)
    
    Args:
        model_name: The string ID of the model (e.g. 'gemini-2.5-flash').
        
    Returns:
        An integer rank value. Lower values should appear earlier in the list.
    """
    cleaned = model_name.lower().strip("\"'")
    
    # 1. Determine Tier
    if "flash-lite" in cleaned or "flash_lite" in cleaned or "lite" in cleaned:
        tier_score = 1000
    elif "flash" in cleaned:
        tier_score = 2000
    elif "pro" in cleaned:
        tier_score = 3000
    elif "veo" in cleaned:
        tier_score = 4000
    elif "imagen" in cleaned:
        tier_score = 5000
    elif "lyria" in cleaned:
        tier_score = 6000
    else:
        tier_score = 7000
        
    # 2. Preview / Experimental penalty
    preview_penalty = 500 if ("preview" in cleaned or "exp" in cleaned or "experimental" in cleaned) else 0
    
    # 3. Version number extraction (e.g. 2.5 -> 25, 3.1 -> 31)
    version_match = re.search(r'gemini-(\d+)(?:\.(\d+))?', cleaned)
    version_score = 0
    if version_match:
        major = int(version_match.group(1))
        minor = int(version_match.group(2)) if version_match.group(2) else 0
        version_score = major * 10 + minor
        
    return tier_score + preview_penalty + version_score

# ==============================================================================
# Structural & License Regexes
# ==============================================================================

# Acceptable copyright headings in cell 0
COPYRIGHT_REGEXES: List[Pattern] = [
    re.compile(r'Copyright 20[1-9][0-9]\s+(?:Google\s+LLC|Google|The TensorFlow\s.*?\s?Authors|The AI Edge Authors)', re.IGNORECASE),
]

# Acceptable Apache 2.0 license cell header
LICENSE_REGEX: Pattern = re.compile(r'#\s?@title\s+Licensed under the Apache License', re.IGNORECASE)

# Colab button regex
COLAB_BUTTON_IMG_REGEX: Pattern = re.compile(r'colab-badge\.svg|colab_logo_32px\.png', re.IGNORECASE)
COLAB_BUTTON_HREF_REGEX: Pattern = re.compile(r'href=["\'](https://colab\.research\.google\.com/[^"\']+)["\']')
