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

# Notebooks that should not be required to be referenced in README / Table of Contents files.
EXCLUDED_README_NOTEBOOKS: Set[str] = {
    "quickstarts/Template.ipynb",
    "quickstarts/Authentication_with_OAuth.ipynb",
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
    "has moved",
    "has moved to",
    "this colab has moved",
    "this notebook has moved",
    "moved to https://",
    "redirect",
    "this notebook has moved",
    "has moved",
    "moved!",
]

# Max cells for a notebook to be considered a stub/redirect notebook candidate
MAX_REDIRECT_CELL_COUNT: int = 6

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
# e.g.: MODEL_ID = "gemini-3.7-flash" # @param ["gemini-3.1-pro-preview", "gemini-3.7-flash", "gemini-3.5-flash-lite", "gemini-2.5-pro"]
MODEL_PARAM_SELECTOR_REGEX: Pattern = re.compile(
    r'(?:MODEL_ID|model_id|MODEL|model)\s*=\s*["\']([^"\']+)["\']\s*#\s*@param\s*(\[[^\]]+\])',
    re.MULTILINE
)

def get_model_sort_key(model_name: str) -> tuple:
    """Computes a sort key for ordering Gemini models according to cookbook style guide.
    
    Order:
      1. Family / Media type category (General Gemini -> Live -> TTS -> Omni -> Image -> Embeddings -> Veo -> Imagen -> Lyria -> Other)
      2. Generation version descending (e.g. 3.x before 2.x before 1.x)
      3. Capability tier ascending: Pro (most capable) -> Flash -> Flash-Lite / 8b (least capable)
      4. Specific version descending (e.g. 3.7 before 3.1)
    
    Args:
        model_name: The string ID of the model (e.g. 'gemini-3.7-flash').
        
    Returns:
        A tuple sort key where lower values appear earlier in the list.
    """
    cleaned = model_name.lower().strip("\"'")
    cleaned = cleaned.replace("models/", "")
    
    # 1. Family / Media type category
    if "learnlm" in cleaned:
        family_cat = 9
    elif "veo" in cleaned:
        family_cat = 6
    elif "imagen" in cleaned:
        family_cat = 7
    elif "lyria" in cleaned:
        family_cat = 8
    elif "embedding" in cleaned:
        family_cat = 5
    elif "tts" in cleaned:
        family_cat = 2
    elif "live" in cleaned or "native-audio" in cleaned:
        family_cat = 1
    elif "omni" in cleaned or "translate" in cleaned:
        family_cat = 3
    elif "-image" in cleaned:
        family_cat = 4
    elif "gemini" in cleaned:
        family_cat = 0
    else:
        family_cat = 10

    # 2. Generation / Version extraction
    gen_score = 0
    m = re.search(r"(?:gemini-|veo-|imagen-|lyria-|learnlm-|text-embedding-)?(\d+)(?:\.(\d+))?", cleaned)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) else 0
        gen_score = major * 100 + minor

    # Generation bucket (e.g. 300 for 3.x, 200 for 2.x, 400 for 4.x)
    gen_bucket = (gen_score // 100) * 100 if gen_score >= 100 else gen_score

    # 3. Capability tier ranking
    if "ultra" in cleaned:
        tier_rank = 5
    elif "pro" in cleaned:
        tier_rank = 10
    elif "flash-lite" in cleaned or "flash_lite" in cleaned or "8b" in cleaned or "-lite" in cleaned or "clip" in cleaned:
        tier_rank = 30
    elif "flash" in cleaned:
        tier_rank = 20
    elif "fast" in cleaned:
        tier_rank = 25
    elif "generate" in cleaned:
        tier_rank = 20
    else:
        tier_rank = 20

    return (family_cat, -gen_bucket, tier_rank, -gen_score, cleaned)


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
