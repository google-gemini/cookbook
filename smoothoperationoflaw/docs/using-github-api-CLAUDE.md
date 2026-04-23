# CLAUDE.md — using-the-github-api-in-your-app

> **SmoothOperationofLaw Transformation Kit**
> AI agent governance, compliance automation, and IP registry management.

This file gives AI assistants context about the repository structure, conventions, and workflows.

---

## Repository Overview

This repository implements the **SmoothOperationofLaw™ Agent Governance Framework** — a Ruby/Python/GitHub Actions system for managing AI agent prompts as governed, compliant trust assets. It was adapted from the GitHub developer resources quickstart into a production framework for:

- **Compliance layer** — legal disclaimers, acceptable-use policy, terms of use
- **IP governance** — asset registry, risk classification, release-approval matrix
- **Technical infrastructure** — JSON Schema validation, SHA-256 manifest building, CI/CD gating
- **Ruby server** — webhook-handling Sinatra app (`server.rb`, `template_server.rb`) for GitHub Apps integration

The **Head Trustee** (Lord Ramon De Leon, Trustee Authorization GA‑TR‑RDL2018‑2025) holds final authority over all high-risk agent releases.

---

## Directory Structure

```
using-the-github-api-in-your-app/
├── .github/
│   └── workflows/
│       └── main.yml          # CI: schema validation → manifest build
├── trust/                    # Governance & IP management
│   ├── DISCLAIMER.md
│   ├── ACCEPTABLE_USE_POLICY.md
│   ├── TERMS_OF_USE.md
│   ├── IP_REGISTRY.md        # Asset ID, version, IP status, license class, risk level
│   └── REVIEW_MATRIX.md      # Approval gates by risk level × audience
├── schema/
│   └── agent.schema.json     # JSON Schema for agent YAML frontmatter
├── scripts/
│   ├── validate.py           # YAML frontmatter validator (exits 1 on failure)
│   └── build_manifest.py     # Generates dist/manifest.json with SHA-256 hashes
├── docs/                     # Additional documentation
├── .env-example              # Required environment variables
├── Gemfile / Gemfile.lock    # Ruby dependencies (Sinatra, octokit, etc.)
├── config.ru                 # Rack entry point
├── server.rb                 # Production GitHub App server
├── template_server.rb        # Reference implementation (heavily commented)
└── README.md                 # Transformation Kit guide
```

---

## Brand Voice and Professional Tone

All documentation must reflect SmoothOperationofLaw™ brand values:

- **Authoritative** — assertive, precise legal language; no hedging
- **Strategic** — frame every technical choice in terms of outcome and risk
- **Second person** — address the reader as "you", not "we"
- **Imperative headings** — "Configure the schema", not "Configuring the Schema"
- **Sentence case** — only the first word and proper nouns capitalized in headings
- Keep tone **formal but accessible** — no jargon without definition, no colloquialisms

---

## Strategic Content Architecture

Structure all documentation with:

1. **Purpose statement** — one sentence, what problem this solves
2. **Prerequisites** — exact versions and credentials needed
3. **Numbered steps** — atomic, testable, ordered
4. **Expected output** — show exactly what success looks like (exit codes, file paths, JSON snippets)
5. **Troubleshooting** — one table mapping symptom → cause → fix
6. **Reference** — links to authoritative sources (GitHub API docs, Ruby/Python docs, RFC/statute)

Use tables for comparison data. Use fenced code blocks with language tags for all code. Use `> **Note:**` blockquotes for warnings and callouts.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Server | Ruby / Sinatra | 3.x |
| Dependency management | Bundler | 2.x |
| Validation scripts | Python | 3.10+ |
| YAML parsing | PyYAML | 6.x |
| Schema validation | jsonschema | 4.x |
| Hashing | hashlib (stdlib) | — |
| CI/CD | GitHub Actions | — |
| Webhook handling | Octokit.rb | 6.x |

---

## Agent Schema

Every agent definition (`.md` file with YAML frontmatter) **must** include these required fields:

```yaml
---
id: "unique-kebab-case-id"
name: "Human Readable Name"
version: "1.0.0"         # semver
status: "active"         # active | deprecated | experimental
audience: "internal"     # internal | public | client
risk_level: "low"        # low | medium | high
ip_owner: "SmoothOperationofLaw Irrevocable Trust"
---
```

**Validation rules (enforced by `scripts/validate.py`):**
- All 7 fields are required; script exits with code 1 if any are missing
- `status` must be one of: `active`, `deprecated`, `experimental`
- `audience` must be one of: `internal`, `public`, `client`
- `risk_level` must be one of: `low`, `medium`, `high`
- `id` must be unique across the repository

Run validation locally before committing:

```bash
python scripts/validate.py path/to/agent.md
```

---

## IP Registry and Review Matrix

### IP Registry (`trust/IP_REGISTRY.md`)

Maintain one row per agent:

| Asset ID | Version | IP Status | License Class | Risk Level |
|---|---|---|---|---|
| `design-ui` | 1.0.0 | Public | Apache 2.0 | Low |
| `legal-analyst` | 2.1.0 | Internal | Trade Secret | High |
| `acad-research` | 1.3.0 | Public | MIT | Low |

### Release Approval Matrix (`trust/REVIEW_MATRIX.md`)

| Risk Level | Audience | Approver(s) Required |
|---|---|---|
| Low | Public | Maintainer |
| Medium | Public | Maintainer + Peer Review |
| High | Public | **FORBIDDEN — cannot publish** |
| Low | Internal | Maintainer |
| Medium | Internal | Maintainer + Head Trustee |
| High | Internal | Head Trustee + Legal Counsel |
| Any | Client | Head Trustee |

> **Warning:** Never merge a PR that adds or promotes a `risk_level: high` + `audience: public` agent. The CI will reject it, and manual override is not permitted.

---

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/main.yml`) runs on every push and PR to `main`:

```
push / PR → validate schema → build manifest (main branch only) → upload artifact
```

### Schema validation step

```yaml
- name: Validate agent schemas
  run: python scripts/validate.py
```

Exit code 1 blocks the merge.

### Manifest build step (main branch only)

```yaml
- name: Build manifest
  if: github.ref == 'refs/heads/main'
  run: python scripts/build_manifest.py
```

Outputs `dist/manifest.json` — an indexed list of all agents with SHA-256 hashes for integrity verification.

---

## Ruby Server

### Running locally

```bash
bundle install
cp .env-example .env
# Fill in GITHUB_APP_ID, GITHUB_PRIVATE_KEY, GITHUB_WEBHOOK_SECRET
ruby server.rb
```

Server runs on `http://localhost:3000` by default.

### Key routes (`server.rb`)

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Health check |
| `/event_handler` | POST | Receives GitHub webhook payloads |

### GitHub App configuration

The server acts as a GitHub App. Required secrets in `.env`:

- `GITHUB_APP_ID` — from GitHub App settings
- `GITHUB_PRIVATE_KEY` — PEM-formatted private key (newlines escaped as `\n`)
- `GITHUB_WEBHOOK_SECRET` — random string set in GitHub App webhook config
- `GITHUB_INSTALLATION_ID` — installation ID for the target org/repo

### Webhook payload handling

All webhook events arrive at `/event_handler`. The server authenticates the signature using `GITHUB_WEBHOOK_SECRET` (HMAC-SHA256). Refer to `template_server.rb` for annotated examples of handling `pull_request`, `issues`, and `check_run` events.

---

## Python Scripts

### `scripts/validate.py`

- Reads all `.md` files in the repository
- Extracts YAML frontmatter between `---` delimiters
- Checks each file against required fields and enum values
- Prints `✓ valid` or `✗ FAILED: <reason>` per file
- Exits with code `1` if any file fails

**Do not modify the required field list** without updating `schema/agent.schema.json` and the CI workflow simultaneously.

### `scripts/build_manifest.py`

- Reads all validated agent `.md` files
- Computes SHA-256 hash of each file's content
- Writes `dist/manifest.json` with format:

```json
{
  "generated_at": "ISO-8601 timestamp",
  "agents": [
    {
      "id": "design-ui",
      "path": "agents/design-ui.md",
      "sha256": "abc123...",
      "version": "1.0.0",
      "status": "active",
      "audience": "public",
      "risk_level": "low"
    }
  ]
}
```

---

## Quality Assurance

### Pre-commit checks

Before every commit, run:

```bash
python scripts/validate.py           # Schema validation
python -m json.tool schema/agent.schema.json  # JSON Schema is valid JSON
bundle exec ruby -c server.rb        # Ruby syntax check
```

### Peer review requirements

All PRs require:
- One approving review (from a maintainer for low-risk; from Head Trustee for medium/high)
- CI passing (schema validation green)
- No hardcoded credentials in any file (scan with `git grep -i "secret\|password\|token" -- ':!.env-example'`)

### Documentation review

Before merging new agent definitions:
- Confirm the `DISCLAIMER.md` covers the new use case
- Update `IP_REGISTRY.md` with the new asset row
- Confirm `REVIEW_MATRIX.md` approval requirements were followed

---

## Risk Mitigation and Compliance

- **No legal advice** — all agent outputs must be prefaced with the disclaimer in `trust/DISCLAIMER.md`
- **No unauthorized practice** — agents must not purport to provide legal representation
- **Trade secrets** — agents marked `ip_owner: SmoothOperationofLaw Irrevocable Trust` are proprietary; do not publish or fork without written authorization
- **Binding arbitration** — all disputes regarding use of these assets are subject to binding arbitration in Los Angeles County under AAA Commercial Rules
- **Class action waiver** — class actions are prohibited per `trust/TERMS_OF_USE.md`
- **Export control** — do not deploy to jurisdictions restricted by U.S. export regulations

### Credential security

- Never commit real credentials to the repository
- Rotate `GITHUB_WEBHOOK_SECRET` and `GITHUB_PRIVATE_KEY` if they appear in any commit
- Use GitHub Secrets for all CI environment variables

---

## Development Workflow

### Adding a new agent

1. Create `agents/<id>.md` with valid YAML frontmatter (all 7 required fields)
2. Run `python scripts/validate.py` locally — confirm exit code 0
3. Add a row to `trust/IP_REGISTRY.md`
4. Follow `trust/REVIEW_MATRIX.md` to get the required approvals
5. Open a PR; CI must pass before merge
6. After merge, `dist/manifest.json` is rebuilt automatically

### Promoting an agent from `experimental` to `active`

1. Update `status` field in the agent `.md`
2. Bump `version` (semver minor: `1.0.0` → `1.1.0`)
3. Update `trust/IP_REGISTRY.md`
4. Obtain required approval per `trust/REVIEW_MATRIX.md`
5. Open a PR; merge only after CI passes and review is complete

### Deprecating an agent

1. Set `status: deprecated` in the agent `.md`
2. Add a `deprecated_at` field with ISO-8601 date
3. Leave the file in place — do not delete; the manifest records all versions
4. Update `trust/IP_REGISTRY.md` to reflect deprecation

---

## Performance and Delivery

- **Manifest caching** — consumers should cache `dist/manifest.json` and only re-fetch when the ETag changes
- **SHA-256 verification** — always verify agent file integrity against the manifest hash before use
- **Webhook latency** — the Ruby server must respond to GitHub webhooks within 10 seconds; defer heavy processing to background jobs
- **Rate limiting** — GitHub API rate limit is 5,000 requests/hour for authenticated apps; batch requests and cache responses

---

## License

All content in this repository is proprietary to the SmoothOperationofLaw Irrevocable Trust unless explicitly marked otherwise (e.g., `license_class: MIT`). Do not reproduce, distribute, or sublicense without written authorization from the Head Trustee.

Trustee Authorization: **GA‑TR‑RDL2018‑2025**
