#!/usr/bin/env python3
"""Command Line Interface for Gemini API Cookbook Notebook Formatter (`nbfmt`).

This CLI tool formats Jupyter and Colab notebooks (.ipynb) to ensure clean diffs,
standardized metadata, and adherence to repository formatting standards.

Usage Examples:
  # Format a specific notebook
  python tools/nbfmt_cli.py quickstarts/Get_started.ipynb

  # Format all notebooks in the repo
  python tools/nbfmt_cli.py quickstarts/**/*.ipynb examples/**/*.ipynb

  # Test if notebooks are properly formatted (used in CI)
  python tools/nbfmt_cli.py --test quickstarts/Get_started.ipynb

  # Dry-run check without modifying files
  python tools/nbfmt_cli.py --dry-run quickstarts/Get_started.ipynb
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

from tools.nbfmt.formatter import NotebookFormatter, FormatResult

logger = logging.getLogger(__name__)

COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
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
    """Parses command line arguments for nbfmt."""
    parser = argparse.ArgumentParser(
        description="Gemini API Cookbook Notebook Formatter (nbfmt)"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Notebook files or glob patterns to format."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test if notebooks are formatted without making changes. Returns exit code 1 if unformatted."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without modifying files on disk."
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="Number of spaces for JSON indentation (default: 2)."
    )
    parser.add_argument(
        "--remove-outputs",
        action="store_true",
        help="Strip outputs and execution counts from code cells."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging."
    )
    return parser.parse_args()


def resolve_file_paths(file_patterns: List[str]) -> List[pathlib.Path]:
    """Expands file patterns and globs into sorted pathlib.Path objects."""
    matched_files = set()
    for pattern in file_patterns:
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


def main() -> int:
    """Main CLI entrypoint for nbfmt."""
    args = parse_arguments()
    setup_logging(args.verbose)

    if not args.files:
        target_files = resolve_file_paths(["quickstarts/**/*.ipynb", "examples/**/*.ipynb"])
    else:
        target_files = resolve_file_paths(args.files)

    if not target_files:
        print("No .ipynb files found to format.")
        return 0

    mode_str = "Testing" if args.test else ("Checking (dry-run)" if args.dry_run else "Formatting")
    print(f"{mode_str} {len(target_files)} notebook(s)...\n")

    formatter = NotebookFormatter(
        indent=args.indent,
        remove_outputs=args.remove_outputs,
        verbose=args.verbose
    )

    unformatted_files = []
    error_files = []

    for path in target_files:
        res = formatter.format_file(path, dry_run=args.dry_run, test_only=args.test)
        if not res.is_valid_json:
            print(f"{COLOR_RED}[ERROR]{COLOR_RESET} {path}: {res.message}")
            error_files.append(path)
        elif not res.is_formatted:
            print(f"{COLOR_YELLOW}[UNFORMATTED]{COLOR_RESET} {path}")
            unformatted_files.append(path)
        else:
            if not args.test:
                print(f"{COLOR_GREEN}[OK]{COLOR_RESET} {path}: {res.message}")

    if args.test:
        if unformatted_files or error_files:
            print("\n" + "=" * 60)
            print(f"{COLOR_RED}[TEST FAILED]{COLOR_RESET} The following notebook(s) are not formatted:")
            for p in unformatted_files:
                print(f"  - {p}")
            for p in error_files:
                print(f"  - {p} (Corrupted JSON)")
            print("\nPlease format them by running:")
            print(f"  python tools/nbfmt_cli.py {' '.join(str(p) for p in unformatted_files)}")
            print("=" * 60)
            return 1
        else:
            print(f"{COLOR_GREEN}[TEST PASSED]{COLOR_RESET} All notebooks are properly formatted.")
            return 0

    print("\n" + "=" * 60)
    print(f"Formatting Summary:")
    print(f"  Total Processed : {len(target_files)}")
    print(f"  Modified/Needs  : {len(unformatted_files)}")
    print(f"  Errors          : {len(error_files)}")
    print("=" * 60)

    if error_files:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
