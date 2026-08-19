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
Centralized Configuration Module for Notebook Testing & Regression Suite.

This module centralizes all configurable items across the testing pipeline,
including:
- Model identifiers used for security auditing, output comparison, and factual verification.
- Timeouts (per-cell and per-notebook) and execution limits.
- Security thresholds (maximum acceptable risk score, forbidden domain policies).
- File paths for default rules, reports, logs, and artifacts.
- Environment variable names (with strict enforcement of GEMINI_API_KEY).
- Default execution parameters (concurrency workers, dry-run flags).

Use Cases:
1. Customizing AI Judge or Security Auditor model versions (e.g. testing with pre-release models).
2. Adjusting execution timeouts for heavy multi-modal notebooks.
3. Overriding default directories and log levels in CI vs local development.
"""

import os
import pathlib
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TesterConfig:
    """Central configuration class holding all testing parameters."""

    # Models
    # User rule: If specified, trust model names and centralize all LLM model references.
    SECURITY_AUDITOR_MODEL: str = "gemini-2.5-flash"
    OUTPUT_JUDGE_MODEL: str = "gemini-2.5-flash"
    GROUNDED_VERIFIER_MODEL: str = "gemini-2.5-flash"

    # API Keys & Auth
    # Strictly use GEMINI_API_KEY environment variable.
    API_KEY_ENV_VAR: str = "GEMINI_API_KEY"

    # Execution Timeouts & Limits
    DEFAULT_CELL_TIMEOUT_SEC: int = 90
    DEFAULT_NOTEBOOK_TIMEOUT_SEC: int = 600
    MAX_OUTPUT_CHARS_FOR_DIFF: int = 4000
    MAX_PROMPT_CHARS_FOR_LOG: int = 1500

    # Security Thresholds
    MAX_ALLOWED_RISK_SCORE: int = 3  # Risk scores from 0 (Safe) to 10 (Critical)
    BLOCK_ON_UNSAFE_VERDICT: bool = True

    # Concurrency
    DEFAULT_WORKERS: int = 2

    # Paths & Directories
    REPO_ROOT: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(__file__).resolve().parents[2]
    )
    DEFAULT_RULES_PATH: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(__file__).resolve().parent / "rules" / "default_rules.yaml"
    )
    REPORTS_DIR: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(__file__).resolve().parents[2] / "reports"
    )
    LOGS_DIR: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(__file__).resolve().parents[2] / "reports" / "logs"
    )

    # Runtime Flags
    DRY_RUN: bool = False
    VERBOSE: bool = False
    SKIP_AI_JUDGE: bool = False
    SECURITY_ONLY: bool = False

    def get_api_key(self) -> Optional[str]:
        """
        Retrieves the Gemini API key securely from environment variables.
        
        Returns:
            The API key string if present, or None.
        """
        return os.getenv(self.API_KEY_ENV_VAR)

    def validate(self) -> List[str]:
        """
        Validates the configuration state and returns any warning/error messages.
        
        Returns:
            List of diagnostic string messages.
        """
        issues = []
        if not self.DRY_RUN and not self.SECURITY_ONLY and not self.get_api_key():
            issues.append(
                f"Missing environment variable {self.API_KEY_ENV_VAR}. "
                "Live execution and AI Judge require a valid Gemini API key."
            )
        return issues


# Default global configuration instance
GLOBAL_CONFIG = TesterConfig()
