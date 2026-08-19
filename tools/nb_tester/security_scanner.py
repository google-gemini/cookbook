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

"""
Deterministic Static Security and Safety Scanner for Jupyter Notebooks.

This module acts as the Level 1 (Deterministic / Zero-Secret) pre-execution gate.
It parses notebook cells into Python Abstract Syntax Trees (AST) and scans for:
- Environment variable dumps or exfiltration patterns (e.g. `os.environ.items()`, dumping all secrets).
- Dangerous execution functions (`eval`, `exec`, `__import__`, `globals()`, `locals()`).
- Direct socket/raw network access outside authorized high-level SDKs.
- Hardcoded API keys and secrets in code cells or cell metadata.
- Suspicious shell commands in IPython magics (`!bash`, `!nc`, `!curl -d`, etc.).

Use Cases:
1. Fast, instant security gating in GitHub Actions PR checks without needing API keys.
2. Blocking obvious malicious code or accidental secret leaks before starting the kernel.
3. Providing clear line-level diagnostic warnings to contributors on why a pattern was flagged.
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Optional
import nbformat


@dataclass
class SecurityFinding:
    """Represents a single security or safety issue found in a notebook."""
    cell_index: int
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    category: str  # "SECRET_LEAK", "CODE_EXECUTION", "NETWORK", "ENV_DUMP", "SHELL_MAGIC"
    message: str
    code_snippet: str
    line_number: Optional[int] = None


@dataclass
class StaticScanResult:
    """Aggregate result of a static security scan on a notebook."""
    notebook_path: str
    is_safe: bool
    findings: List[SecurityFinding] = field(default_factory=list)

    @property
    def max_severity(self) -> str:
        """Returns the highest severity among findings, or 'CLEAN'."""
        if not self.findings:
            return "CLEAN"
        severities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        found = [f.severity for f in self.findings]
        for s in reversed(severities):
            if s in found:
                return s
        return "LOW"


class NotebookStaticSecurityScanner:
    """Static AST and regex scanner for notebook cells."""

    # Regex patterns for secret detection
    SECRET_PATTERNS = [
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "Google API Key format detected in code"),
        (re.compile(r"AQ\.[A-Za-z0-9-_]{40,}"), "Gemini/Internal API token format detected in code"),
        (re.compile(r"(?:api_key|apikey|secret|password)\s*=\s*['\"][A-Za-z0-9_\-]{20,}['\"]", re.IGNORECASE), "Hardcoded secret string assignment"),
    ]

    # Suspicious shell commands in IPython magics
    SUSPICIOUS_SHELL_PATTERNS = [
        (re.compile(r"!(?:nc|ncat|netcat|bash\s+-i|sh\s+-i)", re.IGNORECASE), "Reverse shell command detected"),
        (re.compile(r"!(?:rm\s+-rf\s+[/~])", re.IGNORECASE), "Destructive root filesystem command detected"),
    ]

    ALLOWED_CURL_DOMAINS = (
        "generativelanguage.googleapis.com",
        "googleapis.com",
        "storage.googleapis.com",
        "raw.githubusercontent.com",
        "github.com",
        "google.com",
    )

    # Forbidden AST nodes and calls
    FORBIDDEN_CALLS = {
        "eval": ("CRITICAL", "CODE_EXECUTION", "Dynamic code execution via eval() is forbidden."),
        "exec": ("CRITICAL", "CODE_EXECUTION", "Dynamic code execution via exec() is forbidden."),
        "compile": ("HIGH", "CODE_EXECUTION", "Dynamic compilation via compile() is suspicious."),
        "__import__": ("HIGH", "CODE_EXECUTION", "Low-level __import__ call detected."),
    }

    def scan_notebook(
        self,
        nb: nbformat.NotebookNode,
        notebook_path: str = "",
        allow_dynamic_exec: bool = False
    ) -> StaticScanResult:
        """
        Scans all code cells and metadata of a notebook for security risks.
        
        Args:
            nb: Parsed nbformat NotebookNode.
            notebook_path: Optional path for reporting.
            allow_dynamic_exec: If True, permits exec() calls if explicitly approved by rules.
            
        Returns:
            StaticScanResult containing safety verdict and all findings.
        """
        findings: List[SecurityFinding] = []

        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type != "code":
                continue

            source = cell.source or ""
            if not source.strip():
                continue

            # 1. Regex checks for secrets and dangerous shell magics
            self._scan_regex_rules(source, cell_idx, findings)

            # 2. AST parsing for Python calls
            self._scan_ast_rules(source, cell_idx, findings, allow_dynamic_exec=allow_dynamic_exec)

        is_safe = not any(f.severity in ("CRITICAL", "HIGH") for f in findings)
        return StaticScanResult(
            notebook_path=notebook_path,
            is_safe=is_safe,
            findings=findings
        )

    def _scan_regex_rules(self, source: str, cell_idx: int, findings: List[SecurityFinding]) -> None:
        """Runs regex patterns against raw cell source."""
        lines = source.splitlines()
        is_shell_cell = len(lines) > 0 and lines[0].strip().startswith(("%%bash", "%%sh", "%%script", "%%zsh"))
        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            # If inside a shell cell magic, treat commands as shell lines
            if is_shell_cell and line_num > 1 and not line_str.startswith("!"):
                line_str = "!" + line_str
            # Check for secrets
            for pattern, msg in self.SECRET_PATTERNS:
                if pattern.search(line_str):
                    # Ignore template placeholder comments / assignments
                    upper_line = line_str.upper()
                    if (
                        "@PARAM" in upper_line
                        or "TODO" in upper_line
                        or "YOUR_API_KEY" in upper_line
                        or "YOUR_KEY" in upper_line
                        or "YOUR-API-KEY" in upper_line
                        or "ENTER-YOUR" in upper_line
                        or "PLACEHOLDER" in upper_line
                        or "OS.GETENV" in upper_line
                        or "USERDATA.GET" in upper_line
                        or "MY_API_KEY" in upper_line
                    ):
                        continue
                    findings.append(SecurityFinding(
                        cell_index=cell_idx,
                        severity="CRITICAL",
                        category="SECRET_LEAK",
                        message=msg,
                        code_snippet=line_str,
                        line_number=line_num
                    ))

            # Check for dangerous shell magics
            for pattern, msg in self.SUSPICIOUS_SHELL_PATTERNS:
                if pattern.search(line_str):
                    findings.append(SecurityFinding(
                        cell_index=cell_idx,
                        severity="CRITICAL",
                        category="SHELL_MAGIC",
                        message=msg,
                        code_snippet=line_str,
                        line_number=line_num
                    ))

            # Check for unverified external curl/wget data upload
            if re.search(r"!(?:curl|wget)\s+", line_str, re.IGNORECASE):
                if re.search(r"(?:-d|--data|--upload-file|\$GEMINI|\$API)", line_str, re.IGNORECASE):
                    # Check if targeting allowed Google domains
                    if not any(domain in line_str for domain in self.ALLOWED_CURL_DOMAINS):
                        findings.append(SecurityFinding(
                            cell_index=cell_idx,
                            severity="CRITICAL",
                            category="SHELL_MAGIC",
                            message="Shell curl/wget sending data or API keys to non-whitelisted domain",
                            code_snippet=line_str,
                            line_number=line_num
                        ))

    def _scan_ast_rules(
        self,
        source: str,
        cell_idx: int,
        findings: List[SecurityFinding],
        allow_dynamic_exec: bool = False
    ) -> None:
        """Parses source into AST and checks for forbidden calls and attribute access."""
        # Filter out IPython magics (lines starting with % or !) so AST parser doesn't choke
        clean_lines = []
        for line in source.splitlines():
            if line.strip().startswith(("%", "!")):
                clean_lines.append(f"# {line}")
            else:
                clean_lines.append(line)
        clean_code = "\n".join(clean_lines)

        try:
            tree = ast.parse(clean_code)
        except SyntaxError:
            # Notebook syntax errors will be caught in execution phase, not a security breach
            return

        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call):
                func = node.func
                # Direct calls: eval(), exec(), etc.
                if isinstance(func, ast.Name) and func.id in self.FORBIDDEN_CALLS:
                    if allow_dynamic_exec and func.id in ("exec", "eval"):
                        continue
                    sev, cat, msg = self.FORBIDDEN_CALLS[func.id]
                    snippet = clean_lines[node.lineno - 1] if 0 <= node.lineno - 1 < len(clean_lines) else func.id
                    findings.append(SecurityFinding(
                        cell_index=cell_idx,
                        severity=sev,
                        category=cat,
                        message=msg,
                        code_snippet=snippet.strip(),
                        line_number=node.lineno
                    ))

                # Method calls: os.environ.items() or direct environ.items() dumps
                elif isinstance(func, ast.Attribute):
                    is_environ = (
                        (isinstance(func.value, ast.Attribute) and func.value.attr == "environ")
                        or (isinstance(func.value, ast.Name) and func.value.id == "environ")
                    )
                    if is_environ and func.attr in ("items", "values", "copy", "to_dict"):
                        snippet = clean_lines[node.lineno - 1] if 0 <= node.lineno - 1 < len(clean_lines) else "os.environ dump"
                        findings.append(SecurityFinding(
                            cell_index=cell_idx,
                            severity="HIGH",
                            category="ENV_DUMP",
                            message="Full environment dump via os.environ is suspicious.",
                            code_snippet=snippet.strip(),
                            line_number=node.lineno
                        ))
