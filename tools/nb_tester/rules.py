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
Rules Engine and Exception Registry for Notebook Execution and Comparison.

This module resolves custom testing behaviors, execution actions, timeouts,
and output comparison strategies on a per-notebook and per-cell level.

Supported Directives:
- `action`:
    * 'run' (default): Execute cell in kernel.
    * 'skip': Skip executing cell (e.g. interactive `input()`, manual OAuth).
- `strategy`:
    * 'semantic_llm': Use Gemini judge to compare saved vs new output.
    * 'grounded_factual': Dynamic query (sports, weather, news); verify freshness and
      accuracy using Google Search Grounding.
    * 'exact_or_fuzzy': Deterministic numbers, token counts, or code output.
    * 'schema_validation': JSON mode or Structured Outputs validation.
    * 'ignore_output': Ignore output changes (timestamps, random IDs).
- `cell_timeout_sec`: Custom timeout override for heavy multi-modal cells.

Use Cases:
1. Handling notebooks with interactive user prompts without failing headless CI.
2. Routing grounded search queries to the factual search verifier.
3. Overriding timeouts for heavy media generation (e.g. Veo, Lyria).
"""

import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import yaml

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger


@dataclass
class CellRule:
    """Represents a rule targeting a specific notebook cell."""
    match_pattern: Optional[str] = None
    target_index: Optional[int] = None
    action: str = "run"  # 'run' or 'skip'
    strategy: str = "semantic_llm"
    timeout_sec: Optional[int] = None
    reason: Optional[str] = None
    description: Optional[str] = None


@dataclass
class NotebookRuleSet:
    """Represents the complete set of rules for a given notebook."""
    notebook_path: str
    skip_notebook: bool = False
    skip_reason: Optional[str] = None
    allow_dynamic_exec: bool = False
    allow_security_demo: bool = False
    cell_timeout_sec: int = 90
    notebook_timeout_sec: int = 600
    default_strategy: str = "semantic_llm"
    cell_rules: List[CellRule] = field(default_factory=list)


class RulesEngine:
    """Loads and evaluates rules against notebooks and cells."""

    def __init__(self, rules_file: Optional[pathlib.Path] = None, config: Optional[TesterConfig] = None):
        """
        Initializes the Rules Engine.
        
        Args:
            rules_file: Path to YAML rules file.
            config: Optional TesterConfig instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.rules_file = rules_file or self.config.DEFAULT_RULES_PATH
        self.raw_rules: Dict[str, Any] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """Loads rules from the YAML file if present."""
        if self.rules_file.exists():
            try:
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    self.raw_rules = yaml.safe_load(f) or {}
                logger.debug(f"Loaded rules from {self.rules_file}")
            except Exception as e:
                logger.error(f"Failed to parse rules file {self.rules_file}: {e}")
                self.raw_rules = {}
        else:
            logger.warning(f"Rules file {self.rules_file} not found; using defaults.")

    def get_notebook_rules(self, relative_path: str) -> NotebookRuleSet:
        """
        Retrieves the rule set for a specific notebook.
        
        Args:
            relative_path: Relative POSIX path of the notebook (e.g. 'quickstarts/Chat.ipynb').
            
        Returns:
            NotebookRuleSet with all notebook-level and cell-level directives.
        """
        global_defs = self.raw_rules.get("global_defaults", {})
        nb_rules_dict = self.raw_rules.get("notebooks", {}).get(relative_path, {})

        cell_timeout = nb_rules_dict.get(
            "cell_timeout_sec",
            global_defs.get("cell_timeout_sec", self.config.DEFAULT_CELL_TIMEOUT_SEC)
        )
        nb_timeout = nb_rules_dict.get(
            "notebook_timeout_sec",
            global_defs.get("notebook_timeout_sec", self.config.DEFAULT_NOTEBOOK_TIMEOUT_SEC)
        )
        default_strat = nb_rules_dict.get(
            "default_strategy",
            global_defs.get("default_strategy", "semantic_llm")
        )

        parsed_cell_rules = []
        for cr in nb_rules_dict.get("cells", []):
            parsed_cell_rules.append(CellRule(
                match_pattern=cr.get("match"),
                target_index=cr.get("index"),
                action=cr.get("action", "run"),
                strategy=cr.get("strategy", default_strat),
                timeout_sec=cr.get("timeout_sec"),
                reason=cr.get("reason"),
                description=cr.get("description")
            ))

        return NotebookRuleSet(
            notebook_path=relative_path,
            skip_notebook=nb_rules_dict.get("skip_notebook", False),
            skip_reason=nb_rules_dict.get("skip_reason"),
            allow_dynamic_exec=nb_rules_dict.get("allow_dynamic_exec", False),
            allow_security_demo=nb_rules_dict.get("allow_security_demo", False),
            cell_timeout_sec=cell_timeout,
            notebook_timeout_sec=nb_timeout,
            default_strategy=default_strat,
            cell_rules=parsed_cell_rules
        )

    def resolve_cell_action_and_strategy(
        self,
        nb_rules: NotebookRuleSet,
        cell_index: int,
        cell_source: str
    ) -> CellRule:
        """
        Resolves the specific rule matching a given cell by index or content pattern.
        
        Args:
            nb_rules: The NotebookRuleSet for the parent notebook.
            cell_index: 0-based cell index.
            cell_source: Raw Python source of the cell.
            
        Returns:
            Resolved CellRule indicating action, strategy, and timeout.
        """
        # 1. Automatic heuristic: cell containing input() should be skipped unless explicitly overridden
        if "input(" in cell_source and not any(r.target_index == cell_index for r in nb_rules.cell_rules):
            return CellRule(
                target_index=cell_index,
                action="skip",
                strategy="ignore_output",
                reason="Automatic heuristic: cell contains interactive input()"
            )

        # 2. Check explicit cell rules in rule set
        for rule in nb_rules.cell_rules:
            if rule.target_index is not None and rule.target_index == cell_index:
                return rule
            if rule.match_pattern and rule.match_pattern in cell_source:
                return rule

        # 3. Fallback to notebook default
        return CellRule(
            target_index=cell_index,
            action="run",
            strategy=nb_rules.default_strategy,
            timeout_sec=nb_rules.cell_timeout_sec
        )
