#!/usr/bin/env python3
"""README Link Checker for Gemini API Cookbook Notebooks.

This script ensures that all Jupyter and Colab notebooks (.ipynb) in the repository
are properly referenced in at least one relevant README file (e.g. section README,
subfolder README, or root README).

Use Cases:
  - Validating in CI that newly added notebooks are discoverable in the Table of Contents.
  - Running locally to audit all notebooks across quickstarts/ and examples/ for missing links.
  - Supporting exclusion of templates and stubs that should not be listed in Table of Contents.
"""

import argparse
import glob
import logging
import os
import pathlib
import sys
from typing import List, Set, Tuple

# Ensure tools module can be imported
repo_root = pathlib.Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools import config

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
    """Parses command line arguments for the README link checker."""
    parser = argparse.ArgumentParser(
        description="Verify all notebooks are linked in relevant README files."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific notebook files to verify."
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check all notebooks in the repository."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without failing."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging."
    )
    return parser.parse_args()


def get_candidate_readmes(notebook_path: pathlib.Path) -> List[pathlib.Path]:
    """Finds all candidate README.md files where a notebook could be linked.
    
    Checks:
      1. Immediate subfolder README: e.g. quickstarts/websockets/README.md
      2. Top-level section README: e.g. quickstarts/README.md or examples/README.md
      3. Repository root README: README.md
      
    Args:
        notebook_path: Path to the notebook file.
        
    Returns:
        List of existing README Path objects in priority order.
    """
    candidates = []
    
    # 1. Immediate parent directory README
    parent_readme = notebook_path.parent / "README.md"
    if parent_readme.exists():
        candidates.append(parent_readme)
        
    # 2. Top-level section README (e.g. quickstarts/README.md or examples/README.md)
    parts = notebook_path.parts
    if len(parts) > 1:
        top_section = pathlib.Path(parts[0])
        top_readme = top_section / "README.md"
        if top_readme.exists() and top_readme not in candidates:
            candidates.append(top_readme)
            
    # 3. Root README
    root_readme = pathlib.Path("README.md")
    if root_readme.exists() and root_readme not in candidates:
        candidates.append(root_readme)
        
    return candidates


def is_notebook_linked(notebook_path: pathlib.Path) -> Tuple[bool, List[str]]:
    """Checks if a notebook is linked in any candidate README.md file.
    
    Args:
        notebook_path: Path to the notebook.
        
    Returns:
        A tuple of (is_linked: bool, found_in_readmes: List[str]).
    """
    normalized_path_str = str(notebook_path).replace("\\", "/")
    if normalized_path_str.startswith("./"):
        normalized_path_str = normalized_path_str[2:]
        
    filename = notebook_path.name
    stem = notebook_path.stem
    candidate_readmes = get_candidate_readmes(notebook_path)
    
    found_in = []
    for readme_path in candidate_readmes:
        try:
            content = readme_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning("Failed to read %s: %s", readme_path, e)
            continue
            
        # Match patterns:
        # 1. Exact full relative path: quickstarts/Get_started.ipynb
        # 2. Local relative link: (Get_started.ipynb) or (./Get_started.ipynb)
        # 3. Subfolder link: (rest/JSON_mode_REST.ipynb)
        # 4. Colab badge link containing filename: blob/main/.../Get_started.ipynb
        if (
            filename in content or
            normalized_path_str in content or
            f"({filename})" in content or
            f"(./{filename})" in content or
            f"/{filename}" in content
        ):
            found_in.append(str(readme_path))
            
    return (len(found_in) > 0, found_in)


def check_notebook_links(
    file_paths: List[pathlib.Path],
    excluded_files: Set[str],
    ignored_dirs: Set[str] = config.IGNORED_NOTEBOOK_DIRS
) -> Tuple[List[pathlib.Path], List[Tuple[pathlib.Path, List[pathlib.Path]]]]:
    """Evaluates link presence for a collection of notebooks across any repo folder.
    
    Args:
        file_paths: List of notebook paths to evaluate.
        excluded_files: Set of file names or paths to ignore (e.g. templates).
        ignored_dirs: Set of tooling / infrastructure directory names to ignore (e.g. tools, .github).
        
    Returns:
        A tuple of (linked_files, unlinked_files_with_candidates).
    """
    linked = []
    unlinked = []
    
    for nb in file_paths:
        normalized_str = str(nb).replace("\\", "/")
        if normalized_str.startswith("./"):
            normalized_str = normalized_str[2:]
            
        # Check if located in an ignored directory (e.g. tools/, .github/)
        if any(part in ignored_dirs for part in nb.parts):
            logger.info("Skipping notebook in ignored directory: %s", nb)
            continue
            
        # Check exclusions
        if any(excl in normalized_str for excl in excluded_files):
            logger.info("Skipping excluded notebook: %s", nb)
            continue
            
        is_linked, found_readmes = is_notebook_linked(nb)
        if is_linked:
            logger.info("Notebook '%s' is linked in: %s", nb, ", ".join(found_readmes))
            linked.append(nb)
        else:
            candidates = get_candidate_readmes(nb)
            logger.warning("Notebook '%s' is NOT linked in any candidate README", nb)
            unlinked.append((nb, candidates))
            
    return linked, unlinked


def main() -> int:
    """Main CLI entrypoint for README link checker."""
    args = parse_arguments()
    setup_logging(args.verbose)

    if args.all or not args.files:
        all_candidates = glob.glob("**/*.ipynb", recursive=True)
        target_files = sorted([
            pathlib.Path(f) for f in all_candidates
            if not any(part in config.IGNORED_NOTEBOOK_DIRS for part in pathlib.Path(f).parts)
        ])
    else:
        target_files = []
        for pat in args.files:
            expanded = glob.glob(pat, recursive=True)
            if expanded:
                for f in expanded:
                    if f.endswith(".ipynb"):
                        target_files.append(pathlib.Path(f))
            else:
                p = pathlib.Path(pat)
                if p.exists() and p.suffix == ".ipynb":
                    target_files.append(p)
        target_files = sorted(list(set(target_files)))

    if not target_files:
        print("No notebooks found to check.")
        return 0

    print(f"Checking README links for {len(target_files)} notebook(s)...\n")

    linked, unlinked = check_notebook_links(target_files, config.EXCLUDED_NOTEBOOKS)

    for nb in linked:
        print(f"{COLOR_GREEN}[LINKED]{COLOR_RESET} {nb}")

    if unlinked:
        print("\n" + "=" * 60)
        print(f"{COLOR_RED}[UNLINKED NOTEBOOKS]{COLOR_RESET} The following notebooks are not linked in any README.md:")
        for nb, candidates in unlinked:
            candidate_str = ", ".join(str(c) for c in candidates) if candidates else "README.md"
            print(f"  - {COLOR_BOLD}{nb}{COLOR_RESET}")
            print(f"    Expected in one of: {candidate_str}")
            # GitHub Actions annotation format if running in CI
            if os.getenv("GITHUB_ACTIONS") == "true":
                print(f"::warning file={nb}::Link to '{nb}' not found in {candidate_str}")

        print("\nPlease add links in the corresponding section README.md (e.g. Table of Contents).")
        print("=" * 60)
        if not args.dry_run:
            return 1

    print(f"\n{COLOR_GREEN}[SUCCESS]{COLOR_RESET} All checked notebooks are properly linked in README files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
