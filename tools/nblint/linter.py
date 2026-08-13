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

"""Notebook Linter engine for Gemini API Cookbook.

This module provides the core lint orchestration logic:
  - Reading and parsing Jupyter / Colab notebooks (.ipynb).
  - Evaluating notebooks against structure, style, SDK best practices, and model selector rules.
  - Automatically identifying redirected / stub notebooks and applying appropriate lenient rules.
  - Filtering out explicitly excluded files.
  - Generating human-readable console reports and machine-actionable exit statuses.

Use Cases:
  - Validating notebooks locally before creating pull requests.
  - Enforcing automated quality checks in GitHub Actions CI pipelines.
  - Checking single or multiple notebooks with customized repository and branch settings.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import json
import logging
import pathlib

from tools import config
from tools.nblint.rules import gemini, model_selector, structure, style

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Severity level of a lint finding."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LintDiagnostic:
    """Represents an individual lint finding on a notebook file."""
    rule_name: str
    message: str
    severity: Severity = Severity.ERROR
    cell_index: Optional[int] = None
    line_index: Optional[int] = None


@dataclass
class LintResult:
    """Represents the complete evaluation outcome of a single notebook."""
    file_path: pathlib.Path
    is_valid_json: bool = True
    is_excluded: bool = False
    is_redirect: bool = False
    diagnostics: List[LintDiagnostic] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        """Returns True if any ERROR-level diagnostics are present."""
        return any(d.severity == Severity.ERROR for d in self.diagnostics)

    @property
    def has_warnings(self) -> bool:
        """Returns True if any WARNING-level diagnostics are present."""
        return any(d.severity == Severity.WARNING for d in self.diagnostics)


class NotebookLinter:
    """Main linter engine that loads and checks notebooks against configured rules."""

    def __init__(
        self,
        repo: str = config.DEFAULT_REPO,
        branch: str = config.DEFAULT_BRANCH,
        excluded_files: Optional[Set[str]] = None,
        verbose: bool = False
    ):
        """Initializes the notebook linter.
        
        Args:
            repo: Repository slug (e.g. 'google-gemini/cookbook').
            branch: Git branch name (e.g. 'main').
            excluded_files: Set of file paths to exclude from linting.
            verbose: Whether to log verbose debug information.
        """
        self.repo = repo
        self.branch = branch
        self.excluded_files = set(config.EXCLUDED_NOTEBOOKS)
        if excluded_files:
            self.excluded_files.update(excluded_files)
        self.verbose = verbose
        logger.info("Initialized NotebookLinter for repo '%s', branch '%s'", repo, branch)

    def is_redirect_notebook(self, data: Dict[str, Any], file_path: pathlib.Path) -> bool:
        """Detects whether a notebook is a stub redirecting to a new location.
        
        Args:
            data: Parsed notebook JSON content.
            file_path: Path to the notebook file.
            
        Returns:
            True if the notebook is identified as a redirect stub.
        """
        cells = data.get("cells", [])
        if len(cells) > config.MAX_REDIRECT_CELL_COUNT:
            return False
            
        full_text = " ".join("".join(c.get("source", [])) for c in cells).lower()
        for kw in config.REDIRECT_KEYWORDS:
            if kw in full_text:
                logger.info("Identified '%s' as a redirect stub notebook (keyword: '%s')", file_path, kw)
                return True
                
        return False

    def is_file_excluded(self, file_path: pathlib.Path) -> bool:
        """Checks if a file path is in the exclusion list.
        
        Args:
            file_path: Path to check.
            
        Returns:
            True if the file is excluded.
        """
        normalized_str = str(file_path).replace("\\", "/")
        if normalized_str.startswith("./"):
            normalized_str = normalized_str[2:]
            
        for excl in self.excluded_files:
            if normalized_str == excl or normalized_str.endswith("/" + excl) or excl in normalized_str:
                logger.info("File '%s' matched exclusion rule '%s'", file_path, excl)
                return True
                
        return False

    def lint_file(self, file_path: pathlib.Path) -> LintResult:
        """Runs all enabled lint rules on a single notebook file.
        
        Args:
            file_path: Path to the notebook file.
            
        Returns:
            A LintResult with all detected diagnostics.
        """
        result = LintResult(file_path=file_path)
        logger.info("Starting lint analysis for %s", file_path)

        # 1. Check exclusion list
        if self.is_file_excluded(file_path):
            result.is_excluded = True
            logger.info("Skipping excluded file: %s", file_path)
            return result

        # 2. Parse notebook JSON
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            result.is_valid_json = False
            result.diagnostics.append(
                LintDiagnostic(
                    rule_name="json_validity",
                    message=f"Corrupted or unparseable JSON file: {e}",
                    severity=Severity.ERROR
                )
            )
            logger.error("Failed to parse JSON for %s: %s", file_path, e)
            return result

        # 3. Check for redirect stub
        result.is_redirect = self.is_redirect_notebook(data, file_path)

        # 4. Execute Rule Suites
        # Structure rules
        for msg in structure.check_copyright(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("structure::copyright", msg, Severity.ERROR))
            
        for msg in structure.check_license_cell(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("structure::license", msg, Severity.ERROR))
            
        for msg in structure.check_colab_button(data, file_path, self.repo, self.branch, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("structure::colab_button", msg, Severity.ERROR))
            
        for msg in structure.check_next_steps(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("structure::next_steps", msg, Severity.WARNING))

        # Style rules
        for msg in style.check_inclusive_language(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("style::inclusive_language", msg, Severity.ERROR))
            
        for msg in style.check_second_person(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("style::second_person", msg, Severity.ERROR))
            
        for msg in style.check_code_line_length(data, file_path, max_length=100, is_redirect=result.is_redirect):
            result.diagnostics.append(LintDiagnostic("style::line_length", msg, Severity.WARNING))

        # Gemini SDK & API Best Practices
        for msg in gemini.check_pip_install_syntax(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("gemini::pip_magic", msg, Severity.ERROR))
            
        for msg in gemini.check_sdk_package(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("gemini::sdk_package", msg, Severity.ERROR))
            
        for msg in gemini.check_api_key_secret_name(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("gemini::api_key_secret", msg, Severity.ERROR))
            
        for msg in gemini.check_no_hardcoded_api_keys(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("gemini::hardcoded_api_key", msg, Severity.ERROR))

        # Model Selector validation
        for msg in model_selector.check_model_selector(data, file_path, result.is_redirect):
            result.diagnostics.append(LintDiagnostic("gemini::model_selector", msg, Severity.ERROR))

        logger.info(
            "Completed lint analysis for %s: %d error(s), %d warning(s)",
            file_path,
            sum(1 for d in result.diagnostics if d.severity == Severity.ERROR),
            sum(1 for d in result.diagnostics if d.severity == Severity.WARNING)
        )
        return result

    def lint_files(self, file_paths: List[pathlib.Path]) -> List[LintResult]:
        """Runs the linter over multiple notebook files.
        
        Args:
            file_paths: List of notebook file paths to evaluate.
            
        Returns:
            List of LintResults for all provided files.
        """
        logger.info("Executing lint across %d file(s)", len(file_paths))
        return [self.lint_file(fp) for fp in file_paths]
