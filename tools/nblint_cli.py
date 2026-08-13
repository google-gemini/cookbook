#!/usr/bin/env python3

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

"""Command Line Interface for Gemini API Cookbook Notebook Linter (`nblint`).

This CLI tool evaluates Jupyter and Colab notebooks (.ipynb) against the Gemini API
Cookbook styleguide, structural guidelines, and SDK best practices.

Usage Examples:
  # Lint specific notebooks
  python tools/nblint_cli.py quickstarts/Get_started.ipynb

  # Lint all notebooks in the repo
  python tools/nblint_cli.py quickstarts/**/*.ipynb examples/**/*.ipynb

  # Run in dry-run / test mode
  python tools/nblint_cli.py --dry-run quickstarts/Get_started.ipynb

  # Specify repository and branch for Colab button checks
  python tools/nblint_cli.py --repo=google-gemini/cookbook --branch=main quickstarts/Get_started.ipynb
"""

import argparse
import glob
import logging
import os
import pathlib
import sys
from typing import List

# Ensure tools module can be imported from repo root
repo_root = pathlib.Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools import config
from tools.nblint.linter import NotebookLinter, Severity, LintResult

logger = logging.getLogger(__name__)

# ANSI Color codes for clean output
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"


def setup_logging(verbose: bool) -> None:
    """Configures root logger format and verbosity.
    
    Args:
        verbose: If True, set logging level to DEBUG, else INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )


def parse_arguments() -> argparse.Namespace:
    """Parses command line arguments for the linter.
    
    Returns:
        argparse.Namespace containing parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Gemini API Cookbook Notebook Linter (nblint)"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Notebook files or glob patterns to lint."
    )
    parser.add_argument(
        "--repo",
        default=config.DEFAULT_REPO,
        help=f"Target repository slug for Colab URLs (default: {config.DEFAULT_REPO})."
    )
    parser.add_argument(
        "--branch",
        default=config.DEFAULT_BRANCH,
        help=f"Target branch name for Colab URLs (default: {config.DEFAULT_BRANCH})."
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional file paths or patterns to exclude from linting."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry-run check without making any changes."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging."
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Treat all errors as non-blocking warnings."
    )
    return parser.parse_args()


def resolve_file_paths(file_patterns: List[str]) -> List[pathlib.Path]:
    """Expands file patterns and globs into sorted pathlib.Path objects.
    
    Args:
        file_patterns: List of paths or globs.
        
    Returns:
        Sorted list of existing Path objects matching .ipynb files.
    """
    matched_files = set()
    for pattern in file_patterns:
        # Handle glob expansion if shell didn't expand it
        expanded = glob.glob(pattern, recursive=True)
        if expanded:
            for p in expanded:
                if p.endswith(".ipynb"):
                    matched_files.add(pathlib.Path(p))
        else:
            path_obj = pathlib.Path(pattern)
            if path_obj.exists() and path_obj.suffix == ".ipynb":
                matched_files.add(path_obj)

    return sorted(list(matched_files))


def print_result_report(result: LintResult, warn_only: bool) -> None:
    """Prints formatted diagnostic results for a single notebook.
    
    Args:
        result: The LintResult containing file outcomes and diagnostics.
        warn_only: Whether errors are treated as warnings.
    """
    if result.is_excluded:
        print(f"{COLOR_CYAN}[EXCLUDED]{COLOR_RESET} {result.file_path}")
        return

    errors = [d for d in result.diagnostics if d.severity == Severity.ERROR]
    warnings = [d for d in result.diagnostics if d.severity == Severity.WARNING]

    if not errors and not warnings:
        stub_tag = f" {COLOR_CYAN}(Redirect Stub){COLOR_RESET}" if result.is_redirect else ""
        print(f"{COLOR_GREEN}[PASS]{COLOR_RESET} {result.file_path}{stub_tag}")
        return

    if errors:
        status_tag = f"{COLOR_YELLOW}[WARN]{COLOR_RESET}" if warn_only else f"{COLOR_RED}[FAIL]{COLOR_RESET}"
        print(f"\n{status_tag} {COLOR_BOLD}{result.file_path}{COLOR_RESET}")
        for d in errors:
            prefix = f"{COLOR_YELLOW}WARN{COLOR_RESET}" if warn_only else f"{COLOR_RED}ERROR{COLOR_RESET}"
            print(f"  [{prefix}] {COLOR_BOLD}{d.rule_name}{COLOR_RESET}: {d.message}")
    else:
        print(f"\n{COLOR_YELLOW}[WARN]{COLOR_RESET} {COLOR_BOLD}{result.file_path}{COLOR_RESET}")

    for d in warnings:
        print(f"  [{COLOR_YELLOW}WARNING{COLOR_RESET}] {COLOR_BOLD}{d.rule_name}{COLOR_RESET}: {d.message}")


def main() -> int:
    """Main CLI entrypoint for nblint."""
    args = parse_arguments()
    setup_logging(args.verbose)

    logger.info("Starting nblint execution (dry_run=%s)", args.dry_run)

    # Collect files
    if not args.files:
        # Default: scan quickstarts and examples
        target_files = resolve_file_paths(["quickstarts/**/*.ipynb", "examples/**/*.ipynb"])
    else:
        target_files = resolve_file_paths(args.files)

    if not target_files:
        print("No .ipynb files found to lint.")
        return 0

    print(f"Linting {len(target_files)} notebook(s) against Gemini Cookbook standards...\n")

    # Initialize Linter
    linter = NotebookLinter(
        repo=args.repo,
        branch=args.branch,
        excluded_files=set(args.exclude),
        verbose=args.verbose
    )

    results = linter.lint_files(target_files)

    total_files = len(results)
    excluded_count = sum(1 for r in results if r.is_excluded)
    failed_count = sum(1 for r in results if not r.is_excluded and r.has_errors)
    warn_count = sum(1 for r in results if not r.is_excluded and not r.has_errors and r.has_warnings)
    passed_count = sum(1 for r in results if not r.is_excluded and not r.has_errors and not r.has_warnings)

    for res in results:
        print_result_report(res, args.warn_only)

    print("\n" + "=" * 60)
    print(f"Lint Summary:")
    print(f"  Total Checked : {total_files}")
    print(f"  {COLOR_GREEN}Passed        : {passed_count}{COLOR_RESET}")
    print(f"  {COLOR_CYAN}Excluded      : {excluded_count}{COLOR_RESET}")
    print(f"  {COLOR_YELLOW}Warnings Only : {warn_count}{COLOR_RESET}")
    print(f"  {COLOR_RED}Failed        : {failed_count}{COLOR_RESET}")
    print("=" * 60)

    if failed_count > 0 and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
