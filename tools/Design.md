# Gemini API Cookbook Quality Assurance Tools: Architecture & Design

## 1. Background & Motivation

Previously, the Gemini API Cookbook's CI and developer workflows relied on the external package `tensorflow-docs` (`github.com/tensorflow/docs`) for notebook formatting (`nbfmt`) and linting (`nblint`).

This legacy setup created several critical operational problems:
1. **External Dependency**: CI had to install `git+https://github.com/tensorflow/docs` on every workflow run. Any changes or fixes required modifying a separate repository.
2. **False Positives on "native"**: `tensorflow/docs` included `"native": "built-in"` in its inclusive language wordlist. In the Gemini ecosystem, terms like *"native audio"*, *"native TTS"*, *"native multimodal output"*, and model IDs like `gemini-2.5-flash-native-audio-preview` are official terminology, causing CI to fail on valid PRs.
3. **Overly Strict First-Person Flags**: The legacy linter flagged words like `"we"` inside code comments and string parameters (e.g. `text_prompt = "we can see the stage..."`).
4. **Irrelevant Legacy Rules**: Checks for TensorFlow 1.x `r1/` directories and `tfhub.dev` buttons had to be manually excluded in CI commands.
5. **Lack of Gemini-Specific Checks**: Common review issues—such as using `!pip` instead of `%pip`, legacy `google.generativeai` imports, `GOOGLE_API_KEY` vs `GEMINI_API_KEY`, model selector ordering, and hardcoded API keys—had to be caught manually by maintainers.

## 2. Design Principles & Goals

1. **Zero External Tool Dependencies**: Implemented using standard Python libraries (`json`, `pathlib`, `re`, `logging`, `argparse`, `dataclasses`).
2. **Centralized Configuration**: All configurable parameters, model order ranks, excluded files, and wordlists reside in `tools/config.py`.
3. **Modular Rule Architecture**: Separate rule modules for structure, style, SDK best practices, and model selector formatting.
4. **First-Class Support for Special Notebooks**:
   - **Template Notebook**: Explicitly excluded from full strictness tests.
   - **Redirect Stubs**: Auto-detected via cell count and content keywords, skipping full content and Colab button mismatch failures.
5. **Comprehensive Logging & Dry-Run**: Detailed INFO and DEBUG logs, and full `--dry-run` and `--test` support for safe local and CI testing.

## 3. Directory Layout

```
tools/
├── __init__.py
├── config.py                 # Centralized configuration & model hierarchies
├── nblint/                   # Linter core & rule implementations
│   ├── __init__.py
│   ├── linter.py             # Linter execution engine & result aggregation
│   └── rules/
│       ├── __init__.py
│       ├── structure.py      # Copyright, License, Colab button, Next steps
│       ├── style.py          # Inclusive language (no native), Second person
│       ├── gemini.py         # %pip vs !pip, google-genai SDK, GEMINI_API_KEY, no leaks
│       └── model_selector.py # @param Colab form & model ordering validation
├── nbfmt/                    # Formatter core
│   ├── __init__.py
│   └── formatter.py          # JSON normalization, metadata & cell cleaning
├── nblint_cli.py             # CLI entrypoint for linting
├── nbfmt_cli.py             # CLI entrypoint for formatting
├── README.md                 # User guide and CLI reference
└── Design.md                 # Architecture and design rationale (this document)
```

## 4. Model Hierarchy & Ordering Logic

In `tools/config.py`, the model selector rule sorts models using `get_model_sort_key()`:
- **Capability Tiers**: Models are ordered from most capable to least capable: Pro $\rightarrow$ Flash $\rightarrow$ Flash-Lite $\rightarrow$ Domain-specific (Live/Veo/Imagen/Lyria).
- **Generations**: Current generation models (e.g. Gemini 3.x) precede previous generations (e.g. Gemini 2.5).
- **Stable Fallbacks**: When a current-generation Pro model is in preview (e.g. `gemini-3.1-pro-preview`), the previous generation stable Pro model (`gemini-2.5-pro`) is included as a fallback.
