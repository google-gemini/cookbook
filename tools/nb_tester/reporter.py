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
Test Reporting and CI Step Summary Generator.

This module aggregates security findings, execution metrics, and output comparison
results across all tested notebooks and produces:
- **Persistent JSON Reports**: Full structured metadata saved in `reports/<run_id>.json`.
- **GitHub Actions Step Summaries**: Clean, formatted Markdown tables written to
  `$GITHUB_STEP_SUMMARY` for instant visibility in GitHub pull requests.
- **Terminal Summaries**: High-level console breakdown without terminal clearing.

Use Cases:
1. Publishing automated test reports in GitHub Actions PR comments and workflows.
2. Persisting full test run history for regression trend analysis.
3. Providing clear exit codes (0 for pass, 1 for failure) for CI pipelines.
"""

import json
import os
import pathlib
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger
from .security_scanner import StaticScanResult
from .ai_security_auditor import SafetyAuditReport
from .executor import NotebookExecutionResult
from .comparator import CellComparisonReport


@dataclass
class SingleNotebookReport:
    """Consolidated test report for a single notebook."""
    notebook_path: str
    overall_status: str  # 'PASSED', 'FAILED', 'SKIPPED', 'SECURITY_BLOCKED', 'DRY_RUN'
    duration_sec: float
    static_security_safe: bool
    ai_security_verdict: str
    ai_risk_score: int
    execution_status: str
    total_cells: int
    executed_cells: int
    skipped_cells: int
    regressions_count: int
    cell_comparisons: List[CellComparisonReport] = field(default_factory=list)
    failure_reason: Optional[str] = None


@dataclass
class SuiteReport:
    """Consolidated report across the entire test suite run."""
    run_timestamp: str
    total_notebooks: int
    passed_count: int
    failed_count: int
    skipped_count: int
    dry_run: bool
    total_duration_sec: float
    notebook_reports: List[SingleNotebookReport] = field(default_factory=list)


class TestReporter:
    """Generates and writes test reports across multiple formats."""

    def __init__(self, config: Optional[TesterConfig] = None):
        """
        Initializes the Test Reporter.
        
        Args:
            config: Optional TesterConfig instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def generate_suite_report(
        self,
        notebook_reports: List[SingleNotebookReport],
        total_duration: float
    ) -> SuiteReport:
        """
        Builds a SuiteReport object from individual notebook results.
        
        Args:
            notebook_reports: List of SingleNotebookReport objects.
            total_duration: Total execution time of the suite.
            
        Returns:
            Aggregated SuiteReport instance.
        """
        passed = sum(1 for r in notebook_reports if r.overall_status in ("PASSED", "DRY_RUN"))
        failed = sum(1 for r in notebook_reports if r.overall_status in ("FAILED", "SECURITY_BLOCKED"))
        skipped = sum(1 for r in notebook_reports if r.overall_status == "SKIPPED")

        return SuiteReport(
            run_timestamp=time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
            total_notebooks=len(notebook_reports),
            passed_count=passed,
            failed_count=failed,
            skipped_count=skipped,
            dry_run=self.config.DRY_RUN,
            total_duration_sec=round(total_duration, 2),
            notebook_reports=notebook_reports
        )

    def write_json_report(self, suite_report: SuiteReport, output_file: Optional[pathlib.Path] = None) -> pathlib.Path:
        """
        Writes the structured suite report to a JSON file.
        
        Args:
            suite_report: SuiteReport to save.
            output_file: Optional target file path.
            
        Returns:
            Path of the saved JSON report.
        """
        target = output_file or (self.config.REPORTS_DIR / f"test_run_{int(time.time())}.json")
        try:
            # Custom encoder helper
            def _clean_dict(obj):
                if hasattr(obj, "__dict__"):
                    return obj.__dict__
                return str(obj)

            with open(target, "w", encoding="utf-8") as f:
                json.dump(asdict(suite_report), f, indent=2, default=_clean_dict)
            logger.info(f"💾 Full JSON test report written to: {target}")
            return target
        except Exception as e:
            logger.error(f"Failed to write JSON report to {target}: {e}")
            return target

    def write_github_step_summary(self, suite_report: SuiteReport) -> None:
        """
        Appends a formatted Markdown report to $GITHUB_STEP_SUMMARY if available.
        
        Args:
            suite_report: SuiteReport to format.
        """
        step_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
        if not step_summary_path:
            return

        md_lines = [
            f"# 🧪 Gemini API Cookbook Notebook Test Report",
            f"",
            f"**Status:** {'✅ PASSED' if suite_report.failed_count == 0 else '❌ FAILED'} | "
            f"**Total:** {suite_report.total_notebooks} | "
            f"**Passed:** {suite_report.passed_count} | "
            f"**Failed:** {suite_report.failed_count} | "
            f"**Skipped:** {suite_report.skipped_count} | "
            f"**Duration:** {suite_report.total_duration_sec}s",
            f"",
            f"| Notebook | Status | Security (Risk) | Execution | Regressions | Details |",
            f"| :--- | :---: | :---: | :---: | :---: | :--- |"
        ]

        for rep in suite_report.notebook_reports:
            status_badge = "✅ PASS" if rep.overall_status == "PASSED" else (
                "⏭️ SKIP" if rep.overall_status == "SKIPPED" else (
                    "🔍 DRY-RUN" if rep.overall_status == "DRY_RUN" else "❌ FAIL"
                )
            )
            sec_badge = f"{rep.ai_security_verdict} ({rep.ai_risk_score}/10)" if rep.static_security_safe else "🚨 UNSAFE"
            details = rep.failure_reason or f"{rep.executed_cells} cells executed"
            md_lines.append(
                f"| `{rep.notebook_path}` | {status_badge} | {sec_badge} | {rep.execution_status} | {rep.regressions_count} | {details} |"
            )

        try:
            with open(step_summary_path, "a", encoding="utf-8") as f:
                f.write("\n".join(md_lines) + "\n\n")
            logger.info("📊 Appended report to GITHUB_STEP_SUMMARY")
        except Exception as e:
            logger.error(f"Failed to write GITHUB_STEP_SUMMARY: {e}")

    def print_terminal_summary(self, suite_report: SuiteReport) -> None:
        """
        Prints a clean terminal summary table.
        
        Args:
            suite_report: SuiteReport to display.
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"📊 TEST SUITE SUMMARY (Duration: {suite_report.total_duration_sec}s)")
        logger.info(
            f"Total: {suite_report.total_notebooks} | "
            f"Passed: {suite_report.passed_count} | "
            f"Failed: {suite_report.failed_count} | "
            f"Skipped: {suite_report.skipped_count}"
        )
        logger.info("=" * 80)

        header = f"{'Notebook':<45} {'Status':<10} {'Security':<12} {'Regr.':<6} {'Details'}"
        logger.info(header)
        logger.info("-" * len(header))

        for rep in suite_report.notebook_reports:
            sec_str = f"{rep.ai_security_verdict} ({rep.ai_risk_score})"
            details = (rep.failure_reason or f"OK ({rep.executed_cells} cells)")[:30]
            logger.info(
                f"{rep.notebook_path:<45} {rep.overall_status:<10} {sec_str:<12} {rep.regressions_count:<6} {details}"
            )
        logger.info("=" * 80 + "\n")
