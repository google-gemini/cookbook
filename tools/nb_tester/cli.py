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
Command-Line Interface (CLI) for Notebook Testing and Regression Suite.

This module provides the primary entry point for executing notebook tests both
in local development and in automated GitHub Actions CI workflows.

Supported Options:
- `--notebook <path>`: Run tests on a specific notebook file.
- `--changed`: Automatically detect and test only notebooks modified in the current git branch.
- `--all`: Discover and test all `.ipynb` files across quickstarts and examples.
- `--dry-run`: Validate syntax, scan security rules, and simulate execution without running kernels or calling APIs.
- `--security-only`: Run static AST and Gemini AI security audits without executing code.
- `--skip-ai-judge`: Run kernel execution and error checks, skipping semantic output diffing.
- `--workers <N>`: Run notebook tests in parallel.
- `--rules-file <path>`: Override the default YAML exception rules.

Exit Codes:
- `0`: All tested notebooks passed successfully (or dry-run passed).
- `1`: One or more notebooks failed execution, exhibited regressions, or triggered security blocks.
"""

import argparse
import concurrent.futures
import os
import pathlib
import subprocess
import sys
import time
from typing import List, Optional, Union
import nbformat

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import setup_logger, logger
from .security_scanner import NotebookStaticSecurityScanner, StaticScanResult
from .ai_security_auditor import AISecurityAuditor, SafetyAuditReport
from .rules import RulesEngine
from .executor import NotebookExecutor, NotebookExecutionResult
from .comparator import OutputComparator, CellComparisonReport
from .reporter import TestReporter, SingleNotebookReport, SuiteReport


def discover_notebooks(
    repo_root: pathlib.Path,
    target_notebook: Optional[Union[str, List[str]]] = None,
    changed_only: bool = False,
    all_notebooks: bool = False
) -> List[pathlib.Path]:
    """
    Discovers notebooks to test based on CLI selection mode.
    
    Args:
        repo_root: Root repository path.
        target_notebook: Optional specific path or list of paths.
        changed_only: If True, discover notebooks modified in git diff.
        all_notebooks: If True, discover all notebooks in quickstarts and examples.
        
    Returns:
        List of resolved Path objects for target notebooks.
    """
    if target_notebook:
        raw_list = [target_notebook] if isinstance(target_notebook, str) else target_notebook
        found_list = []
        for nb_path in raw_list:
            p = pathlib.Path(nb_path)
            resolved = p if p.is_absolute() else (repo_root / p).resolve()
            if resolved.exists():
                found_list.append(resolved)
            else:
                logger.error(f"Target notebook not found: {nb_path}")
        return found_list

    if changed_only:
        try:
            # Check git diff against base branch (main)
            res = subprocess.run(
                ["git", "diff", "--name-only", "origin/main...HEAD", "*.ipynb"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode != 0 and res.stderr:
                logger.debug(f"git diff origin/main...HEAD returned code {res.returncode}: {res.stderr.strip()}")
            files = [line.strip() for line in res.stdout.splitlines() if line.strip().endswith(".ipynb")]
            if not files:
                # Fallback to upstream/main
                res_upstream = subprocess.run(
                    ["git", "diff", "--name-only", "upstream/main...HEAD", "*.ipynb"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False
                )
                files = [line.strip() for line in res_upstream.stdout.splitlines() if line.strip().endswith(".ipynb")]
            if not files:
                # Fallback to local uncommitted git diff and untracked files
                res2 = subprocess.run(
                    ["git", "diff", "--name-only", "HEAD", "*.ipynb"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False
                )
                if res2.returncode != 0 and res2.stderr:
                    logger.debug(f"git diff HEAD returned code {res2.returncode}: {res2.stderr.strip()}")
                
                res_untracked = subprocess.run(
                    ["git", "ls-files", "--others", "--exclude-standard", "*.ipynb"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                file_set = set()
                if res2.returncode == 0:
                    file_set.update(line.strip() for line in res2.stdout.splitlines() if line.strip().endswith(".ipynb"))
                if res_untracked.returncode == 0:
                    file_set.update(line.strip() for line in res_untracked.stdout.splitlines() if line.strip().endswith(".ipynb"))
                files = list(file_set)

            resolved_files = [(repo_root / f).resolve() for f in files if (repo_root / f).exists()]
            logger.info(f"Discovered {len(resolved_files)} changed notebook(s) via git diff.")
            return resolved_files
        except Exception as e:
            logger.warning(f"Git diff discovery failed ({e}); falling back to quickstarts.")

    # Default / --all: search quickstarts and examples
    found = []
    for pattern in ["quickstarts/**/*.ipynb", "examples/**/*.ipynb"]:
        for p in repo_root.glob(pattern):
            if ".ipynb_checkpoints" not in str(p) and not p.name.startswith("."):
                found.append(p)
    return sorted(found)


def test_single_notebook(
    nb_path: pathlib.Path,
    config: TesterConfig,
    rules_engine: RulesEngine,
    static_scanner: NotebookStaticSecurityScanner,
    ai_auditor: AISecurityAuditor,
    executor: NotebookExecutor,
    comparator: OutputComparator
) -> SingleNotebookReport:
    """
    Executes the complete test pipeline for a single notebook.
    
    Args:
        nb_path: Path to the notebook file.
        config: TesterConfig instance.
        rules_engine: RulesEngine instance.
        static_scanner: Static security scanner.
        ai_auditor: AI security auditor.
        executor: Notebook execution engine.
        comparator: Output comparator.
        
    Returns:
        SingleNotebookReport instance with complete findings.
    """
    t0 = time.time()
    try:
        rel_path = str(nb_path.relative_to(config.REPO_ROOT))
    except ValueError:
        rel_path = str(nb_path)
    logger.info(f"\n▶️ Testing: {rel_path}")

    # Read original notebook
    try:
        orig_nb = nbformat.read(str(nb_path), as_version=4)
    except Exception as e:
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="FAILED",
            duration_sec=0.0,
            static_security_safe=False,
            ai_security_verdict="ERROR",
            ai_risk_score=10,
            execution_status="failed",
            total_cells=0,
            executed_cells=0,
            skipped_cells=0,
            regressions_count=0,
            failure_reason=f"Cannot parse notebook JSON: {e}"
        )

    # 1. Level 1: Static Security Scan
    rule_set = rules_engine.get_notebook_rules(rel_path)
    static_res: StaticScanResult = static_scanner.scan_notebook(
        orig_nb, rel_path, allow_dynamic_exec=rule_set.allow_dynamic_exec
    )
    if not static_res.is_safe:
        critical_findings = [f.message for f in static_res.findings if f.severity in ("CRITICAL", "HIGH")]
        reason = f"Static Security Block: {'; '.join(critical_findings[:2])}"
        logger.error(f"🚨 {rel_path}: {reason}")
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="SECURITY_BLOCKED",
            duration_sec=round(time.time() - t0, 2),
            static_security_safe=False,
            ai_security_verdict="BLOCKED",
            ai_risk_score=10,
            execution_status="not_run",
            total_cells=len(orig_nb.cells),
            executed_cells=0,
            skipped_cells=0,
            regressions_count=0,
            failure_reason=reason
        )

    # 2. Level 2: Gemini AI Security Audit
    ai_audit: SafetyAuditReport = ai_auditor.audit_notebook(orig_nb, rel_path)
    if (ai_audit.safety_verdict == "UNSAFE" or ai_audit.risk_score > config.MAX_ALLOWED_RISK_SCORE) and not rule_set.allow_security_demo:
        reason = f"AI Security Block (Risk {ai_audit.risk_score}/10): {ai_audit.summary}"
        logger.error(f"🚨 {rel_path}: {reason}")
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="SECURITY_BLOCKED",
            duration_sec=round(time.time() - t0, 2),
            static_security_safe=True,
            ai_security_verdict=ai_audit.safety_verdict,
            ai_risk_score=ai_audit.risk_score,
            execution_status="not_run",
            total_cells=len(orig_nb.cells),
            executed_cells=0,
            skipped_cells=0,
            regressions_count=0,
            failure_reason=reason
        )
    elif rule_set.allow_security_demo and (ai_audit.safety_verdict == "UNSAFE" or ai_audit.risk_score > config.MAX_ALLOWED_RISK_SCORE):
        logger.info(f"🛡️ Security exception allowed by rule for demo: {rel_path} (Risk {ai_audit.risk_score}/10)")

    # If security-only flag is set, stop here
    if config.SECURITY_ONLY:
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="PASSED",
            duration_sec=round(time.time() - t0, 2),
            static_security_safe=True,
            ai_security_verdict=ai_audit.safety_verdict,
            ai_risk_score=ai_audit.risk_score,
            execution_status="security_only",
            total_cells=len(orig_nb.cells),
            executed_cells=0,
            skipped_cells=0,
            regressions_count=0
        )

    # 3. Execution Phase
    rule_set = rules_engine.get_notebook_rules(rel_path)
    exec_res: NotebookExecutionResult = executor.execute_notebook(nb_path, rule_set)

    if exec_res.status == "skipped":
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="SKIPPED",
            duration_sec=round(time.time() - t0, 2),
            static_security_safe=True,
            ai_security_verdict=ai_audit.safety_verdict,
            ai_risk_score=ai_audit.risk_score,
            execution_status="skipped",
            total_cells=len(orig_nb.cells),
            executed_cells=0,
            skipped_cells=0,
            regressions_count=0,
            failure_reason=exec_res.first_error_message
        )

    if exec_res.status == "failed":
        return SingleNotebookReport(
            notebook_path=rel_path,
            overall_status="FAILED",
            duration_sec=round(time.time() - t0, 2),
            static_security_safe=True,
            ai_security_verdict=ai_audit.safety_verdict,
            ai_risk_score=ai_audit.risk_score,
            execution_status="failed",
            total_cells=len(orig_nb.cells),
            executed_cells=exec_res.executed_cells_count,
            skipped_cells=exec_res.skipped_cells_count,
            regressions_count=1,
            failure_reason=exec_res.first_error_message
        )

    # 4. Output Comparison & Regression Judging
    cell_reports: List[CellComparisonReport] = []
    regressions = 0

    if not config.DRY_RUN and exec_res.executed_nb_copy:
        orig_code_cells = [c for c in orig_nb.cells if c.cell_type == "code"]
        exec_code_cells = [c for c in exec_res.executed_nb_copy.cells if c.cell_type == "code"]

        for idx, (orig_c, exec_c) in enumerate(zip(orig_code_cells, exec_code_cells)):
            src = exec_c.source or ""
            cell_rule = rules_engine.resolve_cell_action_and_strategy(rule_set, idx, src)
            if cell_rule.action == "skip":
                continue

            comp_report = comparator.compare_cell(
                cell_index=idx,
                source_code=src,
                strategy=cell_rule.strategy,
                old_outputs=orig_c.get("outputs", []),
                new_outputs=exec_c.get("outputs", []),
                notebook_path=rel_path
            )
            cell_reports.append(comp_report)
            if comp_report.is_regression:
                regressions += 1
                logger.warning(
                    f"⚠️ Regression in {rel_path} Cell {idx} ({comp_report.strategy}): {comp_report.explanation}"
                )

    overall_status = "PASSED"
    failure_msg = None
    if config.DRY_RUN:
        overall_status = "DRY_RUN"
    elif regressions > 0:
        overall_status = "FAILED"
        failure_msg = f"{regressions} output regression(s) detected by comparator/judge."

    return SingleNotebookReport(
        notebook_path=rel_path,
        overall_status=overall_status,
        duration_sec=round(time.time() - t0, 2),
        static_security_safe=True,
        ai_security_verdict=ai_audit.safety_verdict,
        ai_risk_score=ai_audit.risk_score,
        execution_status=exec_res.status,
        total_cells=len(orig_nb.cells),
        executed_cells=exec_res.executed_cells_count,
        skipped_cells=exec_res.skipped_cells_count,
        regressions_count=regressions,
        cell_comparisons=cell_reports,
        failure_reason=failure_msg
    )


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.
    
    Args:
        argv: Optional command line arguments list.
        
    Returns:
        0 on success, 1 on failure.
    """
    parser = argparse.ArgumentParser(
        description="Automated Notebook Security, Execution & Regression Testing Suite"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--notebook", "-n", type=str, nargs="+", help="Specific notebook path(s) to test.")
    group.add_argument("--changed", "-c", action="store_true", help="Test only notebooks modified in git diff.")
    group.add_argument("--all", "-a", action="store_true", help="Test all notebooks in quickstarts and examples.")

    parser.add_argument("--dry-run", action="store_true", help="Simulate tests without altering state or invoking kernel.")
    parser.add_argument("--security-only", action="store_true", help="Run static & AI security audits only.")
    parser.add_argument("--skip-ai-judge", action="store_true", help="Skip semantic AI output diffing.")
    parser.add_argument("--model", "-m", type=str, help="Override MODEL_ID with a specific Gemini model name across all executed notebook cells.")
    parser.add_argument("--override-model", type=str, dest="model", help=argparse.SUPPRESS)
    parser.add_argument("--workers", "-w", type=int, default=1, help="Number of concurrent worker threads.")
    parser.add_argument("--rules-file", type=str, help="Path to custom YAML rules file.")
    parser.add_argument("--output-json", type=str, help="Custom output path for JSON test report.")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging.")

    args = parser.parse_args(argv)

    config = TesterConfig()
    config.DRY_RUN = args.dry_run
    config.SECURITY_ONLY = args.security_only
    config.SKIP_AI_JUDGE = args.skip_ai_judge
    config.VERBOSE = args.verbose
    config.OVERRIDE_MODEL = args.model
    if args.rules_file:
        config.DEFAULT_RULES_PATH = pathlib.Path(args.rules_file).resolve()

    setup_logger(verbose=args.verbose)
    logger.info("🔧 Initializing Notebook Testing & Regression Suite...")
    if config.OVERRIDE_MODEL:
        logger.info(f"🎯 Model Override Active: enforcing MODEL_ID = '{config.OVERRIDE_MODEL}' across all notebooks")

    # Validate configuration
    issues = config.validate()
    for iss in issues:
        logger.warning(f"⚠️ Configuration Warning: {iss}")

    # Discover target notebooks
    notebooks = discover_notebooks(
        repo_root=config.REPO_ROOT,
        target_notebook=args.notebook,
        changed_only=args.changed,
        all_notebooks=args.all
    )

    if not notebooks:
        logger.info("✨ No notebooks found to test.")
        return 0

    logger.info(f"📋 Found {len(notebooks)} notebook(s) to test.\n")

    rules_engine = RulesEngine(rules_file=config.DEFAULT_RULES_PATH, config=config)
    static_scanner = NotebookStaticSecurityScanner()
    ai_auditor = AISecurityAuditor(config=config)
    executor = NotebookExecutor(config=config, rules_engine=rules_engine)
    comparator = OutputComparator(config=config)
    reporter = TestReporter(config=config)

    t_suite_start = time.time()
    reports: List[SingleNotebookReport] = []

    # Run execution (sequential or parallel)
    if args.workers > 1 and len(notebooks) > 1:
        logger.info(f"⚡ Running in parallel with {args.workers} workers...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    test_single_notebook,
                    nb, config, rules_engine, static_scanner, ai_auditor, executor, comparator
                ): nb for nb in notebooks
            }
            for fut in concurrent.futures.as_completed(futures):
                try:
                    rep = fut.result()
                    reports.append(rep)
                except Exception as ex:
                    nb = futures[fut]
                    logger.error(f"Uncaught exception testing {nb}: {ex}")
    else:
        for nb in notebooks:
            rep = test_single_notebook(
                nb, config, rules_engine, static_scanner, ai_auditor, executor, comparator
            )
            reports.append(rep)

    suite_duration = time.time() - t_suite_start
    suite_report = reporter.generate_suite_report(reports, suite_duration)

    # Persist Reports
    json_path = reporter.write_json_report(
        suite_report,
        output_file=pathlib.Path(args.output_json) if args.output_json else None
    )
    reporter.write_github_step_summary(suite_report)
    reporter.print_terminal_summary(suite_report)

    # Exit code
    if suite_report.failed_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
