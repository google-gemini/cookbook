# Google Antigravity SDK Compliance & Scope Verification with Kakunin

This guide demonstrates how to secure Google Antigravity SDK agents by enforcing cryptographic scope limits and active status validation using **Kakunin X.509 certificates** and lifecycle hooks.

## Key Concepts

AI agents running locally with the Google Antigravity SDK have access to custom Python tool functions (e.g. database querying, local file manipulation, API access). Securing these tools is critical in production.

Kakunin provides a compliance layer to verify agent permissions in real time using lifecycle hooks:
- **Active-Agent Enforcement**: Rejects tool execution attempts if the agent's certificate has been revoked or suspended.
- **Cryptographic Scope Checking**: Verifies that the agent holds the required metadata scopes (e.g. `trade.execute`) before running local tool logic.

## Examples Included

- ** JPlayground Notebook (`google_antigravity_playground.ipynb`)**: An interactive notebook showing agent registration, certificate issuance, hook configuration, and compliance testing.
- **Quickstart (`quickstart.py`)**: A standalone Python script implementation of the compliance integration.

## Prerequisites

- Python 3.10+
- Gemini API Key
- Kakunin API Key

## Setup

```bash
pip install -r requirements.txt

export KAK_API_KEY="your-kakunin-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
```

## Running the Examples

Run the standalone quickstart script:
```bash
python quickstart.py
```
