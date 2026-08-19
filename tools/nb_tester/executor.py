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
Notebook Execution Engine with Kernel Isolation and Colab Mocking.

This module is responsible for executing Jupyter Notebooks cell-by-cell in an
isolated IPython kernel using `nbclient`.

Key Features:
- **Zero-Disk-Tampering Colab Mock**: Injects a virtual `google.colab` module directly
  into the kernel's memory space upon startup so that `userdata.get('GEMINI_API_KEY')`
  transparently resolves to `os.environ['GEMINI_API_KEY']` without modifying the original notebook files.
- **Granular Cell Execution & Timeouts**: Executes code cells individually with configurable
  timeouts, capturing execution errors (`ename`, `evalue`, `traceback`) without crashing the test runner.
- **Skip Directive Handling**: Gracefully skips cells flagged by the RulesEngine (e.g. `input()` prompts).
- **Dry-Run Support**: Inspects cell syntax and simulates execution without spinning up kernels or calling APIs.

Use Cases:
1. Running notebooks in headless CI environments with full API authentication.
2. Isolating execution state so failures in one notebook do not pollute subsequent tests.
3. Recording new cell outputs alongside execution timings for downstream regression analysis.
"""

import copy
import os
import pathlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellTimeoutError, CellExecutionError

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger
from .rules import RulesEngine, NotebookRuleSet, CellRule


@dataclass
class CellExecutionRecord:
    """Detailed record of a single cell's execution."""
    cell_index: int
    cell_type: str
    source_code: str
    action_taken: str  # 'executed', 'skipped', 'dry_run'
    strategy: str
    duration_sec: float = 0.0
    error: Optional[Dict[str, Any]] = None
    outputs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class NotebookExecutionResult:
    """Aggregate result of running a notebook."""
    notebook_path: str
    status: str  # 'passed', 'failed', 'skipped', 'dry_run'
    total_duration_sec: float
    total_code_cells: int
    executed_cells_count: int
    skipped_cells_count: int
    first_error_message: Optional[str] = None
    cell_records: List[CellExecutionRecord] = field(default_factory=list)
    executed_nb_copy: Optional[nbformat.NotebookNode] = None


class NotebookExecutor:
    """Handles isolated kernel setup, mock injection, and cell execution."""

    def __init__(self, config: Optional[TesterConfig] = None, rules_engine: Optional[RulesEngine] = None):
        """
        Initializes the Notebook Executor.
        
        Args:
            config: Optional TesterConfig instance.
            rules_engine: Optional RulesEngine instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.rules_engine = rules_engine or RulesEngine(config=self.config)

    def execute_notebook(
        self,
        nb_path: pathlib.Path,
        rule_set: Optional[NotebookRuleSet] = None
    ) -> NotebookExecutionResult:
        """
        Executes a single notebook from disk and returns detailed execution records.
        
        Args:
            nb_path: Absolute or relative Path to the .ipynb file.
            rule_set: Optional pre-resolved NotebookRuleSet.
            
        Returns:
            NotebookExecutionResult with status, timings, and cell snapshots.
        """
        try:
            rel_path = str(nb_path.relative_to(self.config.REPO_ROOT))
        except ValueError:
            rel_path = str(nb_path)
        rule_set = rule_set or self.rules_engine.get_notebook_rules(rel_path)

        if rule_set.skip_notebook:
            logger.info(f"⏭️ Skipping notebook {rel_path}: {rule_set.skip_reason or 'Marked to skip'}")
            return NotebookExecutionResult(
                notebook_path=rel_path,
                status="skipped",
                total_duration_sec=0.0,
                total_code_cells=0,
                executed_cells_count=0,
                skipped_cells_count=0,
                first_error_message=rule_set.skip_reason
            )

        # Read notebook
        try:
            orig_nb = nbformat.read(str(nb_path), as_version=4)
        except Exception as e:
            logger.error(f"Failed to read notebook {rel_path}: {e}")
            return NotebookExecutionResult(
                notebook_path=rel_path,
                status="failed",
                total_duration_sec=0.0,
                total_code_cells=0,
                executed_cells_count=0,
                skipped_cells_count=0,
                first_error_message=f"Failed to parse notebook JSON: {e}"
            )

        # Handle Dry-Run
        if self.config.DRY_RUN:
            logger.info(f"[DRY-RUN] Simulating execution for {rel_path}...")
            return self._dry_run_simulation(orig_nb, rel_path, rule_set)

        # Create working copy of notebook
        exec_nb = copy.deepcopy(orig_nb)
        
        # Inject Colab Mock Preamble
        api_key = self.config.get_api_key() or ""
        mock_source = (
            "import sys, os\n"
            "from unittest.mock import MagicMock\n"
            "_mock_colab = MagicMock()\n"
            f"_mock_colab.userdata.get.side_effect = lambda k: os.getenv(k, {api_key!r} if k in ('GEMINI_API_KEY', 'GOOGLE_API_KEY') else None)\n"
            "sys.modules['google.colab'] = _mock_colab\n"
            "sys.modules['google.colab.userdata'] = _mock_colab.userdata\n"
            f"os.environ['GEMINI_API_KEY'] = {api_key!r}\n"
        )
        mock_cell = nbformat.v4.new_code_cell(source=mock_source)
        exec_nb.cells.insert(0, mock_cell)

        working_dir = str(nb_path.parent.resolve())
        client = NotebookClient(
            exec_nb,
            timeout=rule_set.cell_timeout_sec,
            kernel_name="python3",
            allow_errors=True,  # Capture errors in cell outputs without tearing down kernel early
            resources={"metadata": {"path": working_dir}}
        )

        cell_records: List[CellExecutionRecord] = []
        first_error: Optional[str] = None
        executed_count = 0
        skipped_count = 0
        t_start = time.time()

        code_cells_with_idx = [(i, c) for i, c in enumerate(exec_nb.cells) if c.cell_type == "code"]
        total_code_cells = len(code_cells_with_idx) - 1  # Excluding mock preamble

        logger.info(f"🚀 Starting execution of {rel_path} ({total_code_cells} code cells)...")

        try:
            with client.setup_kernel():
                # Execute preamble
                client.execute_cell(exec_nb.cells[0], 0)

                for orig_idx, (real_idx, cell) in enumerate(code_cells_with_idx[1:], start=1):
                    source = cell.source or ""
                    # 0-based index in original notebook
                    cell_in_orig_nb = real_idx - 1

                    rule = self.rules_engine.resolve_cell_action_and_strategy(
                        rule_set, cell_in_orig_nb, source
                    )

                    if rule.action == "skip":
                        logger.info(f"  ⏭️ Cell {cell_in_orig_nb} SKIPPED: {rule.reason or 'Rule directive'}")
                        skipped_count += 1
                        cell_records.append(CellExecutionRecord(
                            cell_index=cell_in_orig_nb,
                            cell_type="code",
                            source_code=source,
                            action_taken="skipped",
                            strategy="ignore_output",
                            duration_sec=0.0
                        ))
                        continue

                    # Execute cell
                    cell_t0 = time.time()
                    cell_error = None
                    try:
                        client.execute_cell(cell, real_idx)
                    except CellTimeoutError as te:
                        cell_error = {
                            "ename": "CellTimeoutError",
                            "evalue": f"Cell timed out after {rule_set.cell_timeout_sec}s",
                            "traceback": [str(te)]
                        }
                    except Exception as ex:
                        cell_error = {
                            "ename": type(ex).__name__,
                            "evalue": str(ex),
                            "traceback": [str(ex)]
                        }

                    cell_duration = time.time() - cell_t0
                    executed_count += 1

                    # Extract error from cell outputs if not caught above
                    outputs = cell.get("outputs", [])
                    for out in outputs:
                        if out.get("output_type") == "error":
                            cell_error = {
                                "ename": out.get("ename", "Error"),
                                "evalue": out.get("evalue", ""),
                                "traceback": out.get("traceback", [])
                            }
                            break

                    if cell_error and not first_error:
                        first_error = f"Cell {cell_in_orig_nb} failed: {cell_error['ename']}: {cell_error['evalue']}"
                        logger.error(f"  ❌ {first_error}")
                    else:
                        logger.debug(f"  ✅ Cell {cell_in_orig_nb} completed in {cell_duration:.2f}s")

                    cell_records.append(CellExecutionRecord(
                        cell_index=cell_in_orig_nb,
                        cell_type="code",
                        source_code=source,
                        action_taken="executed",
                        strategy=rule.strategy,
                        duration_sec=round(cell_duration, 3),
                        error=cell_error,
                        outputs=copy.deepcopy(outputs)
                    ))

        except Exception as kernel_exc:
            if not first_error:
                first_error = f"Kernel initialization/runtime failure: {kernel_exc}"
            logger.error(f"Kernel failure on {rel_path}: {kernel_exc}")

        # Remove mock cell from executed notebook copy
        exec_nb.cells.pop(0)
        total_duration = time.time() - t_start
        status = "failed" if first_error else "passed"

        logger.info(
            f"🏁 Finished {rel_path} in {total_duration:.1f}s: "
            f"Status={status.upper()} (Executed: {executed_count}, Skipped: {skipped_count})"
        )

        return NotebookExecutionResult(
            notebook_path=rel_path,
            status=status,
            total_duration_sec=round(total_duration, 3),
            total_code_cells=total_code_cells,
            executed_cells_count=executed_count,
            skipped_cells_count=skipped_count,
            first_error_message=first_error,
            cell_records=cell_records,
            executed_nb_copy=exec_nb
        )

    def _dry_run_simulation(
        self,
        nb: nbformat.NotebookNode,
        rel_path: str,
        rule_set: NotebookRuleSet
    ) -> NotebookExecutionResult:
        """Simulates execution for dry-run verification."""
        records = []
        code_count = 0
        skip_count = 0

        for i, cell in enumerate(nb.cells):
            if cell.cell_type == "code":
                code_count += 1
                source = cell.source or ""
                rule = self.rules_engine.resolve_cell_action_and_strategy(rule_set, i, source)
                if rule.action == "skip":
                    skip_count += 1
                    records.append(CellExecutionRecord(
                        cell_index=i,
                        cell_type="code",
                        source_code=source,
                        action_taken="dry_run_skip",
                        strategy="ignore_output",
                        duration_sec=0.0
                    ))
                else:
                    records.append(CellExecutionRecord(
                        cell_index=i,
                        cell_type="code",
                        source_code=source,
                        action_taken="dry_run_run",
                        strategy=rule.strategy,
                        duration_sec=0.0,
                        outputs=copy.deepcopy(cell.get("outputs", []))
                    ))

        return NotebookExecutionResult(
            notebook_path=rel_path,
            status="dry_run",
            total_duration_sec=0.01,
            total_code_cells=code_count,
            executed_cells_count=code_count - skip_count,
            skipped_cells_count=skip_count,
            first_error_message=None,
            cell_records=records,
            executed_nb_copy=nb
        )
