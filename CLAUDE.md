# CLAUDE.md — Gemini API Cookbook

This file provides AI assistants with context about the repository structure, conventions, and development workflows.

## Repository Overview

The **Gemini API Cookbook** is an educational repository of Jupyter notebooks and code samples demonstrating how to use the Gemini API. It is organized into two main content tiers:

- **`quickstarts/`** — Step-by-step beginner guides, one feature per notebook
- **`examples/`** — Advanced use cases combining multiple features or third-party integrations

The primary audience is developers learning to use the Gemini API. Code clarity and pedagogy take priority over performance or brevity.

---

## Directory Structure

```
cookbook/
├── quickstarts/          # 129+ beginner notebooks and scripts
│   ├── *.ipynb           # Feature-specific Jupyter notebooks
│   ├── *.py              # Standalone Python scripts (e.g., Live API)
│   ├── file-api/         # File API samples (Node.js)
│   ├── rest/             # REST/cURL examples
│   └── websockets/       # WebSocket examples
├── quickstarts-js/       # JavaScript/TypeScript quickstarts
│   └── *.js
├── examples/             # Advanced and integration examples
│   ├── *.ipynb
│   ├── langchain/
│   ├── llamaindex/
│   ├── haystack/
│   ├── qdrant/
│   ├── weaviate/
│   ├── chromadb/
│   ├── mlflow/
│   ├── google-adk/
│   ├── prompting/
│   ├── json_capabilities/
│   └── iot/
├── .gemini/
│   ├── config.yaml       # Gemini Copilot PR review config
│   └── styleguide.md     # Python notebook style guide
├── .github/
│   └── workflows/        # CI/CD: notebook formatting and linting
├── .devcontainer/
│   └── devcontainer.json # VS Code dev container (universal image)
├── CONTRIBUTING.md
└── README.md
```

---

## Key Conventions

### SDK and Imports

Always use the current Python SDK — **never** the deprecated `google.generativeai`:

```python
# Correct
%pip install -U -q 'google-genai>=1.0.0'
from google import genai
from google.genai import types

# WRONG — deprecated since early 2025
import google.generativeai
```

For JavaScript, use `@google/genai`.

### API Key Handling

**Never hardcode API keys.** Keys must come from environment variables or Colab secrets only. If you encounter a hardcoded key anywhere, flag it immediately — the author must revoke the key and create a new one.

```python
# Correct
import os
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
```

### Model Selection

Use Colab form selectors so the model can be changed without editing code:

```python
MODEL_ID = "gemini-3-flash-preview"  # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-3.1-pro-preview"] {"allow-input":true, isTemplate: true}
```

Do not hardcode model metadata (like context window size) in Markdown. Instead, retrieve it via code:

```python
client.models.get('models/gemini-2.5-flash').input_token_limit
```

---

## Notebook Structure

Every notebook should follow this structure:

1. **Collapsed license cell** — Apache 2.0 header hidden with Colab Form mode (`# @title`)
2. **H1 title** — One `#` heading only
3. **"Open in Colab" badge** — Immediately after the title:
   ```html
   <a target="_blank" href="https://colab.research.google.com/github/google-gemini/cookbook/blob/main/PATH.ipynb">
     <img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/>
   </a>
   ```
4. **Overview section** — Before any code
5. **Setup section** — Installs (`%pip`) and imports
6. **Feature demonstration** — Step by step, small pieces before combinations
7. **Outputs preserved** — Save notebook with outputs so readers can see results without running it

---

## Code Style

### Python

- Follow [Google Python Style Guide](http://google.github.io/styleguide/pyguide.html)
- Max line length: **100 characters** (not PEP 8's 79)
- Indentation: **4 spaces**
- Naming: `snake_case` for variables/functions/modules, `UPPER_SNAKE_CASE` for constants, `CapWords` for classes
- Use `%pip` not `!pip` for installs
- Expand multi-parameter function calls across lines:
  ```python
  response = client.models.generate_content(
      model=MODEL_ID,
      contents="prompt here",
      config={
          "response_mime_type": "application/json",
      }
  )
  ```
- Use triple double-quotes for long strings with leading/trailing line breaks
- Docstrings are optional; use Google-style when included

### Helper Functions

Avoid helper functions for single-use logic. Write inline code so readers don't need to look up definitions. When a helper is unavoidable, hide it with `# @title`.

### Outputs

| Output Type | Method |
|---|---|
| Plain text | `print()` |
| Markdown | `display(Markdown(...))` |
| JSON | `print(json.dumps(data, indent=4))` |
| Images | `display(Image(...))` |

### Text / Markdown Cells

- Imperative style: "Run a prompt using the API."
- Sentence case in headings: "Call the API", not "Calling The API"
- Use **second person** ("you", not "we") — linting will fail otherwise
- Short, descriptive headings
- Link to documentation rather than duplicating it

---

## Notebook Quality Checks (CI)

CI runs on all PRs that modify `.ipynb` files. Two jobs run automatically:

### `nbfmt` — Formatting

```bash
pip install -U tensorflow-docs
python -m tensorflow_docs.tools.nbfmt path/to/notebook
# Check only (no write):
python -m tensorflow_docs.tools.nbfmt --test path/to/notebook
```

If `execution_count` in cells is not `null`, the formatting script has not been run. Run `nbfmt` — do **not** manually remove outputs.

### `nblint` — Style Linting

```bash
python -m tensorflow_docs.tools.nblint \
    --styles=google,tensorflow \
    --arg=repo:google-gemini/cookbook \
    --arg=branch:main \
    --exclude_lint=tensorflow::button_download \
    --exclude_lint=tensorflow::button_website \
    --arg=base_url:https://ai.google.dev/ \
    --exclude_lint=tensorflow::button_github \
    path/to/notebook
```

Excluded from linting: `Template.ipynb`, `Object_detection.ipynb`

### Stale Issues

Issues and PRs with `status:awaiting response` or `status:more data needed` are marked stale after 14 days and closed after 27 days. Use the `override-stale` label to prevent this.

---

## Development Workflow

### Contributing New Content

1. File an issue first — discuss before writing
2. Copy `quickstarts/Template.ipynb` as starting point
3. Write the notebook following conventions above
4. Run `nbfmt` then `nblint` locally
5. Add the notebook to the relevant `README.md` (folder-level at minimum)
6. Sign the [Google CLA](https://cla.developers.google.com/) if you haven't already
7. Submit PR with a Colab link to the notebook on your branch:
   `https://colab.research.google.com/github/{USER}/cookbook/blob/{BRANCH}/{PATH}.ipynb`

### Editing Notebooks in Colab

1. Open the notebook in Colab directly from the target GitHub branch
2. Make changes in Colab
3. Use **File → Save a copy in GitHub** to push back to the same branch

### Dev Container

The repo includes a `.devcontainer/devcontainer.json` using `mcr.microsoft.com/devcontainers/universal:2` with Jupyter and Python VS Code extensions pre-configured. Use it for a consistent local environment.

---

## JavaScript Quickstarts

JavaScript examples live in `quickstarts-js/` and use the `@google/genai` SDK. They are run directly with Node.js and use ES modules. Smaller set than Python notebooks but growing.

For File API JavaScript examples, see `quickstarts/file-api/` which uses `googleapis` and `dotenv`.

---

## Third-Party Integrations (examples/)

The `examples/` directory contains integration notebooks for:

| Category | Tools |
|---|---|
| RAG / Vector DBs | LangChain, LlamaIndex, Haystack, Qdrant, Weaviate, ChromaDB |
| UI Frameworks | Gradio, FastRTC |
| Monitoring | MLflow |
| Google Ecosystem | Google ADK, Apps Script, Google Workspace |
| Specialized | IoT (ESP32), Robotics |

---

## Git and PR Conventions

- Small fixes (typos, bugs) can go directly to a PR
- New guides require an issue first
- Keep notebook JSON diffs manageable — use `nbfmt` consistently
- Use [ReviewNB](https://reviewnb.com) for reviewing notebook diffs in PRs
- All commits require a signed [Google CLA](https://cla.developers.google.com/)

---

## Documentation Standards

### Brand Voice and Professional Tone

All documentation — notebooks, READMEs, Markdown cells, comments — must reflect a cohesive brand voice:

- **Clarity first** — every sentence earns its place; cut anything that doesn't add information
- **Second person** ("you"), present tense, imperative mood for instructions
- **Consistent terminology** — use the same term for the same concept throughout; never alternate between "notebook" and "script" for the same artifact
- **No filler phrases** — avoid "simply", "just", "easy", "straightforward", "please note", "it is important"
- **Active voice** — "Call `generate_content()`", not "The method `generate_content()` should be called"
- **Sentence case** in all headings (enforced by `nblint`)

### Strategic Content Architecture

Structure content so readers can orient quickly and execute without re-reading:

1. **Purpose** — one sentence at the top: what the notebook does and why
2. **Prerequisites** — exact SDK versions, required env vars, any quota requirements
3. **Ordered sections** — overview → setup → feature demonstrations (simple → complex) → cleanup
4. **Progressive disclosure** — show the simplest case first, layer complexity only after it's motivated
5. **Navigation anchors** — H2 headings every 300–500 words; no section without a heading
6. **Tables** for comparison data; **numbered lists** for ordered steps; **bullet lists** for unordered sets

### Quality Assurance

Every notebook submitted as a PR must pass all of the following before requesting review:

| Check | Command | Must Pass |
|---|---|---|
| Formatting | `python -m tensorflow_docs.tools.nbfmt --test path/to/notebook` | No diff |
| Style lint | `python -m tensorflow_docs.tools.nblint --styles=google,tensorflow ...` | Zero violations |
| No deprecated SDK | `grep -r "google.generativeai" .` | No matches |
| No hardcoded keys | `grep -rE "AIza[A-Za-z0-9_-]{35}" .` | No matches |
| Second-person | `nblint` `tensorflow::not_second_person` rule | No violations |

Peer reviews must check:
- All outputs are preserved (notebook run with outputs saved)
- No model metadata hardcoded in Markdown — retrieved via `client.models.get()`
- Model selector uses the Colab `# @param` form field pattern

### Advanced Documentation Practices

**User personas** — every notebook implicitly targets one of these readers:

| Persona | Skill level | What they need |
|---|---|---|
| API Explorer | Beginner | Working copy-paste code, minimal explanation |
| Integration Builder | Intermediate | Patterns, edge cases, error handling |
| Production Engineer | Advanced | Performance, quotas, cost optimization |

Write for the API Explorer first. Add callout boxes (inline Markdown bold + blockquote) for concepts that Intermediate or Advanced readers will want.

**Use cases** — state the concrete use case in the Overview section, not just the API feature. "Summarize legal documents with the Gemini API" is a use case; "Using the `generate_content()` API" is a feature.

**Detailed workflows** — for multi-step processes, use a numbered list with sub-steps rather than flowing prose. Readers scan; they don't read linearly on first pass.

### Risk Mitigation and Compliance

- **Never hardcode API keys** — use `os.environ["GEMINI_API_KEY"]` or Colab secrets exclusively
- **Flag deprecated patterns immediately** — if you see `google.generativeai`, stop and flag before continuing
- **No legal, medical, or financial advice** — notebooks may demonstrate AI capabilities in those domains but must include a disclaimer that outputs are for educational purposes only
- **License header required** — every `.ipynb` file must have the collapsed Apache 2.0 cell as cell 0
- **Model deprecation** — do not hardcode deprecated model IDs; use the `# @param` selector so users can switch
- **Rate limits** — notebooks that call the API in a loop must note the relevant quota and include `time.sleep()` where appropriate to avoid 429 errors in CI

### Performance and Delivery

- **Cached outputs** — always save notebooks with cell outputs so readers can see results without running
- **Minimal installs** — only install what is actually used; `%pip install` once in a single cell
- **No redundant API calls** — reuse `response` objects; don't re-fetch the same content in successive cells
- **Streaming where appropriate** — for long responses, show `generate_content_stream()` so the notebook demonstrates responsive UX
- **Continuous improvement** — link to the GitHub Discussions or issue tracker at the end of each notebook so readers can report problems or suggest enhancements

---

## License

All content is Apache 2.0. Every notebook must include the collapsed license header cell at the top.
