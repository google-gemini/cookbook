# 🧪 Gemini API Cookbook Notebook Testing & Regression Suite

An automated, security-gated test runner and semantic regression evaluator designed specifically for the Jupyter/Colab notebooks in the [Gemini API Cookbook](https://github.com/google-gemini/cookbook).

---

## 🌟 Key Features

1. **🔒 Multi-Layer Security Architecture (Preventing RCE & Key Theft)**:
   - **Level 1 (Static AST Scanner)**: Fast, zero-secret AST checks for forbidden system calls, reverse shells, and raw environment dumps.
   - **Level 2 (Gemini AI Security Auditor)**: Semantic code review with structured JSON output before any code execution to detect subtle backdoors, malicious `%pip` dependencies, or data exfiltration.
   - **Zero-Disk-Tampering Colab Mock**: Injects a virtual `google.colab.userdata` module into the kernel namespace in memory, keeping notebooks clean and keys secure.
2. **⚖️ Semantic Output Regression Judging**:
   - Compares newly generated outputs with the saved reference outputs in the repository.
   - Uses Gemini AI Judge to separate normal non-deterministic phrasing differences (`SLIGHT_VARIATION`) from true broken answers or hallucinations (`REGRESSION`).
3. **🌐 Google Search Grounding Verification**:
   - For real-time and time-evolving queries (e.g. sports scores, weather, current events), uses Gemini with the Google Search tool to double-check that new answers are factually true today.
4. **📋 Declarative Rules & Exception Registry (`rules/default_rules.yaml`)**:
   - Easily configure cell-level actions (e.g. skipping interactive `input()` cells) and per-notebook timeouts.
5. **📊 CI & Pull Request Integration**:
   - Generates persistent JSON reports under `reports/` and auto-appends formatted Markdown tables to `$GITHUB_STEP_SUMMARY`.
   - Returns clean exit codes (`0` on pass, `1` on failure) for automated gating.
6. **🔍 Dry-Run Mode**:
   - Test rule configurations, AST checks, and syntax parsing without altering files, spinning up kernels, or consuming API tokens.

---

## 🚀 Quickstart & Usage

### 1. Dry-Run Mode (Safe simulation)
```bash
python3 -m tools.nb_tester.cli --notebook quickstarts/Counting_Tokens.ipynb --dry-run
```

### 2. Security Audit Only (No code execution)
```bash
python3 -m tools.nb_tester.cli --notebook quickstarts/Prompting.ipynb --security-only
```

### 3. Test a Single Notebook with Live Execution & AI Judge
```bash
export GEMINI_API_KEY="your-api-key"
python3 -m tools.nb_tester.cli --notebook quickstarts/Counting_Tokens.ipynb
```

### 4. Test Only Changed Notebooks in a PR / Git Branch
```bash
python3 -m tools.nb_tester.cli --changed
```

### 5. Run Full Suite in Parallel
```bash
python3 -m tools.nb_tester.cli --all --workers 4
```

---

## ⚙️ Configuration & Exception Rules

Rules are declared in `tools/nb_tester/rules/default_rules.yaml`.

```yaml
global_defaults:
  cell_timeout_sec: 90
  notebook_timeout_sec: 600
  default_strategy: "semantic_llm"

notebooks:
  quickstarts/Grounding.ipynb:
    cells:
      - match: "client.models.generate_content"
        strategy: "grounded_factual"
        description: "Verify dynamic search output using Google Search"

  quickstarts/Interactive_Chat.ipynb:
    cells:
      - match: "input("
        action: "skip"
        reason: "Interactive user input not supported in headless CI"
```

---

## 🏗️ Architecture & Modules

```
tools/nb_tester/
├── config.py             # Centralized models, timeouts, and GEMINI_API_KEY resolution
├── logger.py             # Structured logging with complete LLM prompt/response tracking
├── security_scanner.py   # Level 1: Deterministic AST & regex scanner
├── ai_security_auditor.py# Level 2: Gemini AI Semantic Security Auditor
├── rules.py              # Declarative rules engine and matcher
├── executor.py           # nbclient kernel executor with in-memory Colab mock
├── comparator.py         # Output snapshot extractor and strategy router
├── llm_judge.py          # Level 3: Semantic output regression judge
├── grounded_verifier.py  # Real-time fact-checking via Google Search Grounding
├── reporter.py           # Multi-format report builder (JSON, Step Summary, Terminal)
├── cli.py                # Command-line interface entry point
└── rules/
    └── default_rules.yaml# Default rule definitions and exceptions
```
