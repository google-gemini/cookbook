# Gemini API Cookbook Quality Assurance & Linting Tools

This directory contains standalone tools for formatting, linting, and maintaining Jupyter/Colab notebooks in the [Gemini API Cookbook](https://github.com/google-gemini/cookbook).

These tools are natively hosted in this repository to provide fast, zero-dependency validation tailored specifically to the Gemini SDK and cookbook style guidelines.

---

## Tools Overview

| Tool | Script | Description |
| :--- | :--- | :--- |
| **`nblint`** | `tools/nblint_cli.py` | Lints notebooks for licensing, structure, style, SDK best practices, and model selectors. |
| **`nbfmt`** | `tools/nbfmt_cli.py` | Automatically formats notebook JSON, standardizes metadata, strips empty cells, and aligns code formatting. |
| **`readme_links`** | `tools/check_readme_links.py` | Validates that new/modified notebooks are linked in section Table of Contents READMEs. |
| **`config`** | `tools/config.py` | Central configuration file containing model hierarchies, wordlists, exclusions, and URL rules. |

---

## 1. Quickstart Usage

### Linting Notebooks
```bash
# Lint a specific notebook
python tools/nblint_cli.py quickstarts/Get_started.ipynb

# Lint multiple notebooks or directories
python tools/nblint_cli.py quickstarts/**/*.ipynb examples/**/*.ipynb

# Perform a dry-run check
python tools/nblint_cli.py --dry-run quickstarts/Get_started.ipynb

# Specify custom branch or repository
python tools/nblint_cli.py --repo=google-gemini/cookbook --branch=main path/to/notebook.ipynb
```

### Formatting Notebooks
```bash
# Format a specific notebook (modifies file in place)
python tools/nbfmt_cli.py quickstarts/Get_started.ipynb

# Test if notebooks are properly formatted (without modifying, returns non-zero on unformatted)
python tools/nbfmt_cli.py --test quickstarts/**/*.ipynb

# Format all notebooks in the repo
python tools/nbfmt_cli.py quickstarts/**/*.ipynb examples/**/*.ipynb
```

### Checking Table of Contents README Links
```bash
# Check if a specific notebook is linked in its folder/section README.md
python tools/check_readme_links.py quickstarts/Get_started.ipynb

# Audit all notebooks in the repo
python tools/check_readme_links.py --all
```

---

## 2. Lint Rules Reference

### Structure Rules (`tools/nblint/rules/structure.py`)
- **`structure::copyright`**: Verifies that cell 0 contains a valid Google / Gemini copyright statement (`##### Copyright 2026 Google LLC.`).
- **`structure::license`**: Verifies that the notebook contains a collapsed Apache 2.0 license code cell with `# @title Licensed under the Apache License`.
- **`structure::colab_button`**: Checks for the "Open in Colab" badge and verifies that its destination URL matches `https://colab.research.google.com/github/<repo>/blob/<branch>/<path>`. Automatically adjusts for redirect stubs.
- **`structure::next_steps`**: Emits a warning if a concluding "Next Steps" or "What's Next" section is missing.

### Style & Language Rules (`tools/nblint/rules/style.py`)
- **`style::inclusive_language`**: Flags discouraged terminology (`blacklist`, `whitelist`, `master`, `slave`) and suggests modern alternatives. **Note**: The word `"native"` is deliberately allowed because terms like *"native audio"*, *"native TTS"*, and *"native multimodal"* are standard Gemini API features.
- **`style::second_person`**: Ensures narrative explanations in markdown use second person (*you*) rather than first person (*we*). Prompt strings, quoted examples, and code comments are ignored.
- **`style::line_length`**: Warns when code lines exceed 100 characters (ignoring URLs, form annotations, and long multiline strings).

### Gemini SDK & API Best Practices (`tools/nblint/rules/gemini.py`)
- **`gemini::pip_magic`**: Enforces `%pip install` instead of `!pip install` for reliable kernel-level package installation.
- **`gemini::sdk_package`**: Enforces the official `from google import genai` (`google-genai`) SDK, flagging deprecated `google.generativeai`.
- **`gemini::api_key_secret`**: Checks that notebooks retrieve API keys from `userdata.get('GEMINI_API_KEY')` rather than the legacy `GOOGLE_API_KEY` secret.
- **`gemini::hardcoded_api_key`**: Scans all cells for accidental plaintext Google/Gemini API keys (legacy `AIza...` and new `AQ.Ab8...` formats) to prevent credential leakage.

### Model Selector Validation (`tools/nblint/rules/model_selector.py`)
- **`gemini::model_selector`**:
  - Verifies that model selectors use the canonical Colab form pattern:
    ```python
    MODEL_ID = "gemini-3.7-flash" # @param ["gemini-3.1-pro-preview", "gemini-3.7-flash", "gemini-3.5-flash-lite", "gemini-2.5-pro"] {"allow-input":true, isTemplate: true}
    ```
  - Verifies that the default assigned model exists in the option list.
  - Verifies that models in the list are sorted in logical order from most capable to least capable: **current generation (Pro $\rightarrow$ Flash $\rightarrow$ Flash-Lite)**, followed by **previous generation (e.g. Pro 2.5)**.

---

## 3. Configuration & Exclusions

All configurable settings are consolidated in `tools/config.py`:
- **`EXCLUDED_NOTEBOOKS`**: List of files skipped during automated lint runs (e.g. `quickstarts/Template.ipynb`).
- **`REDIRECT_KEYWORDS`**: Keywords used to automatically detect redirection stubs (e.g. `gemini-robotics-er.ipynb`) and apply lenient rules.
- **`get_model_sort_key(model_name)`**: Ranking algorithm for model selector ordering.
- **`INCLUSIVE_LANGUAGE_WORDLIST`**: Mapping of discouraged terms to replacements.
