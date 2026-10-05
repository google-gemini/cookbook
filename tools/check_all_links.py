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

"""Automated Repository-Wide Link Verification Tool for Gemini API Cookbook.

This script audits Markdown files (`.md`) and Jupyter Notebooks (`.ipynb`)
across the repository to detect dead, broken, or misdirected links before they
reach production.

Features & Capabilities:
1. **Internal Relative Path & Anchor Audit (Fast CI Gate, <2s)**:
   - Extracts all Markdown links `[text](url)` and HTML `<a href="url">` tags.
   - Validates that target relative paths exist on disk.
   - Resolves anchor fragments (`#heading-slug` or HTML `<a name="...">` / `<a id="...">`),
     both within the same file and across cross-notebook links.
   - Ignores Colab UI scroll state fragments (`#scrollTo=...`).
   - Resolves GitHub repository blob links (`https://github.com/google-gemini/cookbook/blob/main/...`)
     directly against local working tree files to catch broken cross-references.
   - Prevents path traversal attacks that escape the repository root.
2. **Selective / Incremental Checking**:
   - Supports passing explicit file paths (e.g. from CI PR changed-files lists).
   - Supports `--changed` to automatically detect modified `.md` and `.ipynb` files via git diff.
   - Defaults to scanning the entire repository if no specific files are provided.
3. **External HTTP Link Health Check (Scheduled / Full Audit)**:
   - Concurrently verifies external HTTP/HTTPS links via HTTP HEAD requests, falling
     back to GET when servers return 405 Method Not Allowed or 403 Forbidden.
   - Centralized ignore-list for local test servers, search engines with bot mitigation,
     and private API endpoints.
4. **Safety & Dry-Run**:
   - Fully read-only, never alters files on disk.
   - Includes `--dry-run` to log extraction actions without firing network requests.

Usage Examples:
  # Fast CI check on specific changed files:
  python3 tools/check_all_links.py quickstarts/Get_started.ipynb README.md

  # Fast CI check on all git-modified files against upstream/main:
  python3 tools/check_all_links.py --changed

  # Full audit of all internal links across the repository:
  python3 tools/check_all_links.py

  # Comprehensive audit including external HTTP links:
  python3 tools/check_all_links.py --all
"""

import argparse
import concurrent.futures
import json
import logging
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Set, Tuple

# Ensure repository root is on sys.path to import centralized tools.config
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from tools import config
except ImportError:
    config = None  # Fallback gracefully if invoked standalone

# Centralized defaults (fallback if tools.config is unavailable)
DEFAULT_TIMEOUT_SEC: float = (
    getattr(config, "LINK_CHECKER_DEFAULT_TIMEOUT", 8.0) if config else 8.0
)
MAX_EXTERNAL_WORKERS: int = (
    getattr(config, "LINK_CHECKER_MAX_EXTERNAL_WORKERS", 16) if config else 16
)
DEFAULT_USER_AGENT: str = (
    getattr(config, "LINK_CHECKER_USER_AGENT", "Mozilla/5.0 (compatible; GeminiCookbookLinkChecker/1.0)")
    if config
    else "Mozilla/5.0 (compatible; GeminiCookbookLinkChecker/1.0)"
)
IGNORED_DOMAINS: Set[str] = (
    getattr(
        config,
        "LINK_CHECKER_IGNORED_DOMAINS",
        {"localhost", "127.0.0.1", "example.com", "generativelanguage.googleapis.com"},
    )
    if config
    else {"localhost", "127.0.0.1", "example.com", "generativelanguage.googleapis.com"}
)
IGNORED_SCHEMES: List[re.Pattern] = (
    getattr(config, "LINK_CHECKER_IGNORED_SCHEMES", [])
    if config
    else [
        re.compile(r"^mailto:", re.IGNORECASE),
        re.compile(r"^tel:", re.IGNORECASE),
        re.compile(r"^javascript:", re.IGNORECASE),
        re.compile(r"^data:", re.IGNORECASE),
        re.compile(r"^#?$", re.IGNORECASE),
    ]
)
EXCLUDED_TARGETS: Set[str] = (
    getattr(config, "LINK_CHECKER_EXCLUDED_TARGETS", {"URL", "TODO"})
    if config
    else {"URL", "TODO"}
)

# Regex patterns for Markdown links [text](url) and HTML <a href="url">
MD_LINK_REGEX = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<url>[^\s\)]+)(?:\s+\"[^\"]*\")?\)")
HTML_LINK_REGEX = re.compile(r"<a\s+(?:[^>]*?\s+)?href=[\"'](?P<url>[^\"'>]+)[\"'][^>]*>", re.IGNORECASE)
HEADING_REGEX = re.compile(r"^(?P<level>#{1,6})\s+(?P<title>.+)$", re.MULTILINE)
ANCHOR_TAG_REGEX = re.compile(r"<a\s+(?:[^>]*?\s+)?(?:name|id)=[\"'](?P<name>[^\"'>]+)[\"'][^>]*>", re.IGNORECASE)

logger = logging.getLogger("link_checker")


class LinkCheckerConfig:
    """Configuration settings for repository link scanning."""

    def __init__(
        self,
        repo_root: pathlib.Path,
        internal_only: bool = True,
        dry_run: bool = False,
        verbose: bool = False,
        timeout: float = DEFAULT_TIMEOUT_SEC,
    ):
        self.repo_root = repo_root.resolve()
        self.internal_only = internal_only
        self.dry_run = dry_run
        self.verbose = verbose
        self.timeout = timeout
        self._anchors_cache: Dict[pathlib.Path, Set[str]] = {}


def slugify_heading(title: str) -> str:
    """Converts a Markdown heading title to a standard GitHub anchor slug.

    Args:
        title: Raw title text of the heading.

    Returns:
        Anchor slug string matching GitHub's Markdown renderer.
    """
    # Strip leading markdown hashes if present
    cleaned = re.sub(r"^#+\s*", "", title.strip())
    slug = cleaned.lower()
    # Strip inline HTML tags
    slug = re.sub(r"<[^>]+>", "", slug)
    # Strip punctuation characters
    slug = re.sub(r"[^\w\s-]", "", slug)
    # Replace whitespace sequences with single hyphens
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


def extract_anchors_from_content(content: str) -> Set[str]:
    """Extracts all possible anchor targets from Markdown or notebook text.

    Args:
        content: Raw text content of file or cell.

    Returns:
        Set of valid anchor slugs and HTML names.
    """
    anchors: Set[str] = set()
    # 1. HTML <a name="..."> or <a id="..."> tags
    for match in ANCHOR_TAG_REGEX.finditer(content):
        name = match.group("name").strip().lower()
        if name:
            anchors.add(name)
    # 2. Markdown headings (# Heading)
    for match in HEADING_REGEX.finditer(content):
        slug = slugify_heading(match.group("title"))
        if slug:
            anchors.add(slug)
    return anchors


def normalize_cell_source(source: Any) -> List[str]:
    """Normalizes notebook cell source content into a list of string lines.

    Handles cases where cell source is None, a single str, or a list of strings/objects.

    Args:
        source: The raw 'source' field from a notebook cell dictionary.

    Returns:
        A list of strings representing the cell lines.
    """
    if isinstance(source, str):
        return source.splitlines(keepends=True)
    if isinstance(source, list):
        return [s for s in source if isinstance(s, str)]
    return []


def get_file_anchors(file_path: pathlib.Path, checker_config: LinkCheckerConfig) -> Set[str]:
    """Retrieves and caches anchor targets for a given file.

    Args:
        file_path: Path to the .md or .ipynb file.
        checker_config: Checker configuration containing the in-memory cache.

    Returns:
        Set of anchor strings available in the file.
    """
    resolved = file_path.resolve()
    if resolved in checker_config._anchors_cache:
        return checker_config._anchors_cache[resolved]

    anchors: Set[str] = set()
    try:
        if resolved.suffix == ".ipynb":
            with open(resolved, "r", encoding="utf-8") as f:
                data = json.load(f)
            for cell in data.get("cells", []):
                if cell.get("cell_type") in ("markdown", "raw"):
                    lines = normalize_cell_source(cell.get("source"))
                    cell_text = "".join(lines)
                    anchors.update(extract_anchors_from_content(cell_text))
                    # Also index Colab cell IDs for scrollTo references
                    cell_id = cell.get("metadata", {}).get("id") or cell.get("id")
                    if cell_id:
                        anchors.add(f"scrollto={cell_id.lower()}")
        elif resolved.suffix == ".md":
            with open(resolved, "r", encoding="utf-8") as f:
                content = f.read()
            anchors.update(extract_anchors_from_content(content))
    except Exception as e:
        logger.debug("Failed to extract anchors from %s: %s", resolved, e)

    checker_config._anchors_cache[resolved] = anchors
    return anchors


def find_files_to_scan(
    repo_root: pathlib.Path, explicit_files: Optional[List[str]] = None
) -> List[pathlib.Path]:
    """Finds all target Markdown and Jupyter Notebook files to scan.

    Args:
        repo_root: Root directory of the repository clone.
        explicit_files: Optional list of explicit paths provided via CLI.

    Returns:
        Sorted list of existing absolute pathlib.Path objects.
    """
    if explicit_files:
        valid_files = []
        for p in explicit_files:
            target = (repo_root / p).resolve() if not os.path.isabs(p) else pathlib.Path(p).resolve()
            if target.exists() and target.suffix in (".md", ".ipynb"):
                valid_files.append(target)
            else:
                logger.debug("Skipping nonexistent or non-target file: %s", p)
        valid_files.sort()
        return valid_files

    files = []
    excluded_dirs = {
        ".git",
        ".jetski_venv",
        ".venv",
        "venv",
        "node_modules",
        "reports",
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
    }
    for root, dirs, filenames in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith(".")]
        for f in filenames:
            if f.endswith((".md", ".ipynb")):
                files.append(pathlib.Path(root) / f)
    files.sort()
    return files


def get_changed_files_from_git(repo_root: pathlib.Path) -> List[str]:
    """Finds files changed relative to upstream/main or origin/main via git diff.

    Args:
        repo_root: Root directory of repository.

    Returns:
        List of changed relative file path strings.
    """
    # Try upstream/main, then origin/main, then HEAD~1
    base_refs = ["upstream/main", "origin/main", "main", "HEAD~1"]
    for base in base_refs:
        try:
            cmd = ["git", "diff", "--name-only", f"{base}...HEAD"]
            out = subprocess.check_output(cmd, cwd=repo_root, text=True, stderr=subprocess.DEVNULL)
            lines = [line.strip() for line in out.splitlines() if line.strip().endswith((".md", ".ipynb"))]
            if lines:
                logger.info("Detected %d changed file(s) against %s", len(lines), base)
                return lines
        except Exception:
            continue
    logger.warning("Could not determine base branch for --changed. Falling back to all files.")
    return []


def extract_links_from_file(file_path: pathlib.Path) -> List[Tuple[str, int]]:
    """Extracts all links and line/cell numbers from a file.

    Args:
        file_path: Absolute path to the file.

    Returns:
        List of (url, line_number) tuples.
    """
    links: List[Tuple[str, int]] = []
    try:
        if file_path.suffix == ".ipynb":
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for cell_idx, cell in enumerate(data.get("cells", [])):
                if cell.get("cell_type") in ("markdown", "raw"):
                    lines = normalize_cell_source(cell.get("source"))
                    in_fence = False
                    for line in lines:
                        stripped = line.strip()
                        if stripped.startswith("```"):
                            in_fence = not in_fence
                            continue
                        if in_fence:
                            continue
                        for m in MD_LINK_REGEX.finditer(line):
                            links.append((m.group("url").strip(), cell_idx))
                        for m in HTML_LINK_REGEX.finditer(line):
                            links.append((m.group("url").strip(), cell_idx))
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                in_fence = False
                for line_idx, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if stripped.startswith("```"):
                        in_fence = not in_fence
                        continue
                    if in_fence:
                        continue
                    for m in MD_LINK_REGEX.finditer(line):
                        links.append((m.group("url").strip(), line_idx))
                    for m in HTML_LINK_REGEX.finditer(line):
                        links.append((m.group("url").strip(), line_idx))
    except Exception as e:
        logger.warning("Failed to parse links from %s: %s", file_path, e)
    return links


def validate_internal_link(
    source_file: pathlib.Path, url: str, checker_config: LinkCheckerConfig
) -> Tuple[bool, str]:
    """Validates an internal relative path, anchor, or GitHub repository blob URL.

    Args:
        source_file: The file containing the link.
        url: The link target.
        checker_config: LinkCheckerConfig instance.

    Returns:
        Tuple of (is_valid, error_message).
    """
    if url in EXCLUDED_TARGETS:
        return True, "Excluded template placeholder"

    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    fragment = parsed.fragment.strip().lower() if parsed.fragment else ""

    # 1. GitHub repository blob URLs (e.g. https://github.com/google-gemini/cookbook/blob/main/...)
    github_blob_path_prefix = "/google-gemini/cookbook/blob/main/"
    if (
        scheme in ("http", "https")
        and netloc == "github.com"
        and parsed.path.startswith(github_blob_path_prefix)
    ):
        rel_subpath = urllib.parse.unquote(parsed.path[len(github_blob_path_prefix):]).rstrip("/")
        target_path = checker_config.repo_root / rel_subpath
        if not target_path.exists():
            return False, f"Target repository path does not exist on disk: {rel_subpath}"
        if fragment and not fragment.startswith("scrollto="):
            anchors = get_file_anchors(target_path, checker_config)
            if anchors and fragment not in anchors:
                return False, f"Anchor '#{fragment}' not found in target file: {rel_subpath}"
        return True, ""

    # Skip external HTTP(S) URLs (checked separately in external phase)
    if scheme in ("http", "https"):
        return True, ""

    # 2. Pure in-page anchor (#heading or #scrollTo=...)
    clean_path = urllib.parse.unquote(parsed.path)
    if not clean_path and fragment:
        if fragment.startswith("scrollto="):
            return True, ""  # Colab UI cell scroll target
        anchors = get_file_anchors(source_file, checker_config)
        if anchors and fragment not in anchors:
            return False, f"In-page anchor '#{fragment}' not found in {source_file.name}"
        return True, ""

    # 3. Relative path on disk
    target_path = (source_file.parent / clean_path).resolve()
    try:
        target_path.relative_to(checker_config.repo_root)
    except ValueError:
        return False, f"Path escapes repository root: {clean_path}"

    if not target_path.exists():
        return False, f"File does not exist: {clean_path} (resolved to {target_path})"

    # If anchor is present on local file, verify it exists
    if fragment and not fragment.startswith("scrollto=") and target_path.is_file():
        anchors = get_file_anchors(target_path, checker_config)
        if anchors and fragment not in anchors:
            return False, f"Anchor '#{fragment}' not found in target file: {clean_path}"

    return True, ""


def check_external_url(url: str, timeout: float = DEFAULT_TIMEOUT_SEC) -> Tuple[bool, str]:
    """Sends HTTP HEAD/GET requests to verify external link reachability.

    Args:
        url: Target HTTP/HTTPS URL.
        timeout: Request timeout in seconds.

    Returns:
        Tuple of (is_reachable, status_or_error_message).
    """
    try:
        parsed = urllib.parse.urlparse(url)
    except Exception as e:
        return False, f"Malformed URL: {e}"

    if parsed.netloc.lower() in IGNORED_DOMAINS:
        return True, "Ignored domain"

    req = urllib.request.Request(
        url,
        headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "*/*"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status < 400:
                return True, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        # Fall back to GET if server denies HEAD
        if e.code in (403, 405):
            try:
                get_req = urllib.request.Request(
                    url,
                    headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "*/*"},
                    method="GET",
                )
                with urllib.request.urlopen(get_req, timeout=timeout) as resp:
                    if resp.status < 400:
                        return True, f"HTTP {resp.status} (GET)"
            except Exception as get_err:
                return False, f"HTTP {e.code} on HEAD, GET failed: {get_err}"
        return False, f"HTTP {e.code}: {e.reason}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"

    return True, "OK"


def run_link_audit(
    config: LinkCheckerConfig, explicit_files: Optional[List[str]] = None
) -> int:
    """Executes link audit across files according to configuration.

    Args:
        config: LinkCheckerConfig instance.
        explicit_files: Optional subset of files to check.

    Returns:
        Exit code: 0 if all links valid, 1 if broken links found.
    """
    files = find_files_to_scan(config.repo_root, explicit_files)
    logger.info("Scanning %d file(s) (.md and .ipynb) for links.", len(files))

    broken_links: List[Tuple[pathlib.Path, int, str, str]] = []
    total_links = 0
    external_urls_to_check: Set[str] = set()

    for f in files:
        links = extract_links_from_file(f)
        for url, line_info in links:
            if any(p.match(url) for p in IGNORED_SCHEMES):
                continue
            total_links += 1

            parsed = urllib.parse.urlparse(url)
            is_http = parsed.scheme.lower() in ("http", "https")

            if is_http:
                is_blob = (
                    parsed.netloc.lower() == "github.com"
                    and parsed.path.startswith("/google-gemini/cookbook/blob/main/")
                )
                if is_blob:
                    ok, err = validate_internal_link(f, url, config)
                    if not ok:
                        rel_file = f.relative_to(config.repo_root)
                        broken_links.append((rel_file, line_info, url, err))
                elif not config.internal_only:
                    external_urls_to_check.add(url)
            else:
                ok, err = validate_internal_link(f, url, config)
                if not ok:
                    rel_file = f.relative_to(config.repo_root)
                    broken_links.append((rel_file, line_info, url, err))

    logger.info("Checked internal links across %d total link instances.", total_links)

    if not config.internal_only and external_urls_to_check:
        if config.dry_run:
            logger.info("[DRY-RUN] Would check %d external URLs.", len(external_urls_to_check))
        else:
            logger.info("Checking %d unique external URLs...", len(external_urls_to_check))
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_EXTERNAL_WORKERS) as executor:
                future_to_url = {
                    executor.submit(check_external_url, u, config.timeout): u
                    for u in external_urls_to_check
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    ok, err = future.result()
                    if not ok:
                        broken_links.append((pathlib.Path("EXTERNAL"), 0, url, err))

    print("\n" + "=" * 70)
    print("GEMINI API COOKBOOK LINK AUDIT RESULTS")
    print("=" * 70)
    if not broken_links:
        print("[SUCCESS] All links are healthy and valid!")
        return 0

    print(f"[FAIL] Found {len(broken_links)} broken or dead link(s):\n")
    for src, line, url, err in broken_links:
        location = f"{src}:{line}" if line > 0 else str(src)
        print(f"  ❌ {location} -> {url}")
        print(f"     Reason: {err}\n")
    return 1


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Audit links across Gemini API Cookbook Markdown files and Notebooks."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files (.md or .ipynb) to scan. If omitted, scans repository.",
    )
    parser.add_argument(
        "--repo-dir",
        default=str(REPO_ROOT),
        help="Repository root directory (defaults to parent of tools/).",
    )
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Automatically detect changed files against upstream/main via git diff.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Also check external HTTP/HTTPS links (default: internal relative and blob paths only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform scanning without executing live external network calls.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SEC,
        help=f"Timeout in seconds for external HTTP checks (default: {DEFAULT_TIMEOUT_SEC}s).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose DEBUG level logging.",
    )
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] %(message)s")

    repo_root = pathlib.Path(args.repo_dir).resolve()
    target_files = args.files

    if args.changed and not target_files:
        target_files = get_changed_files_from_git(repo_root)
        if not target_files:
            print("No modified .md or .ipynb files detected against base branch.")
            sys.exit(0)

    config_obj = LinkCheckerConfig(
        repo_root=repo_root,
        internal_only=not args.all,
        dry_run=args.dry_run,
        verbose=args.verbose,
        timeout=args.timeout,
    )
    sys.exit(run_link_audit(config_obj, target_files))


if __name__ == "__main__":
    main()
