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
Notebook Cell Output Extractor and Comparison Router.

This module inspects the outputs saved in the original notebook versus the new
outputs generated during live execution and routes each cell to its designated
comparison strategy:
- `exact_or_fuzzy`: Deterministic numerical/text checks (e.g. token counts, math outputs).
- `semantic_llm`: Evaluation by Gemini AI Judge comparing semantic coherence and detecting regressions.
- `grounded_factual`: Verification of dynamic/time-evolving search queries via Google Search Grounding.
- `schema_validation`: Verification that JSON outputs conform to required structure.
- `ignore_output`: Used for skipped cells or timestamp/random generation cells.

Use Cases:
1. Extracting multi-modal outputs (text, image counts, audio traces, errors) from notebook cells.
2. Preventing false positives on valid model rewrites while catching true semantic regressions.
3. Structuring comparison data for reporting in PR comments and test summaries.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import nbformat

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger
from .llm_judge import GeminiOutputJudge, SemanticComparisonResult
from .grounded_verifier import GroundedFactualVerifier, GroundedVerificationResult


@dataclass
class CellOutputSnapshot:
    """Snapshot representation of cell outputs."""
    text_content: str
    image_count: int
    audio_count: int
    html_present: bool
    error: Optional[Dict[str, Any]] = None


@dataclass
class CellComparisonReport:
    """Detailed evaluation result for a single notebook cell comparison."""
    cell_index: int
    source_code: str
    strategy: str
    verdict: str  # 'MATCH', 'SLIGHT_VARIATION', 'REGRESSION', 'FACTUAL_UPDATE', 'SKIPPED', 'ERROR'
    explanation: str
    old_output_snippet: str
    new_output_snippet: str
    is_regression: bool = False


class OutputComparator:
    """Extracts cell outputs and dispatches comparison strategies."""

    def __init__(self, config: Optional[TesterConfig] = None):
        """
        Initializes the Output Comparator.
        
        Args:
            config: Optional TesterConfig instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.llm_judge = GeminiOutputJudge(config=self.config)
        self.grounded_verifier = GroundedFactualVerifier(config=self.config)

    @staticmethod
    def extract_snapshot(outputs: Optional[List[Dict[str, Any]]]) -> CellOutputSnapshot:
        """
        Extracts structured text, rich media counts, and errors from cell output list.
        
        Args:
            outputs: List of nbformat output dictionaries.
            
        Returns:
            CellOutputSnapshot containing text, media counts, and errors.
        """
        text_parts = []
        image_count = 0
        audio_count = 0
        html_present = False
        error_info = None

        for out in outputs or []:
            out_type = out.get("output_type")
            if out_type == "stream":
                text = out.get("text", "")
                text_parts.append("".join(text) if isinstance(text, list) else str(text))
            elif out_type in ("execute_result", "display_data"):
                data = out.get("data", {})
                for mime_key, mime_val in data.items():
                    if mime_key.startswith("image/"):
                        image_count += 1
                    elif mime_key.startswith("audio/"):
                        audio_count += 1
                    elif mime_key == "text/html":
                        html_present = True
                    elif mime_key == "text/plain":
                        val_str = "".join(mime_val) if isinstance(mime_val, list) else str(mime_val)
                        text_parts.append(val_str)
            elif out_type == "error":
                error_info = {
                    "ename": out.get("ename", "Error"),
                    "evalue": out.get("evalue", ""),
                    "traceback": out.get("traceback", [])
                }

        combined_text = "\n".join(t.strip() for t in text_parts if t.strip()).strip()
        return CellOutputSnapshot(
            text_content=combined_text,
            image_count=image_count,
            audio_count=audio_count,
            html_present=html_present,
            error=error_info
        )

    def compare_cell(
        self,
        cell_index: int,
        source_code: str,
        strategy: str,
        old_outputs: Optional[List[Dict[str, Any]]],
        new_outputs: Optional[List[Dict[str, Any]]],
        notebook_path: str = ""
    ) -> CellComparisonReport:
        """
        Compares old vs new output for a single cell according to the assigned strategy.
        
        Args:
            cell_index: 0-based cell index.
            source_code: Python code of the cell.
            strategy: Evaluation strategy identifier.
            old_outputs: Saved outputs from repository.
            new_outputs: Newly generated outputs from test run.
            notebook_path: Context path for logging.
            
        Returns:
            CellComparisonReport detailing verdict and explanation.
        """
        old_snap = self.extract_snapshot(old_outputs)
        new_snap = self.extract_snapshot(new_outputs)

        old_text_snip = old_snap.text_content[:250]
        new_text_snip = new_snap.text_content[:250]

        # 1. Check for execution errors
        if new_snap.error:
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy=strategy,
                verdict="ERROR",
                explanation=f"Execution error in cell: {new_snap.error.get('ename')}: {new_snap.error.get('evalue')}",
                old_output_snippet=old_text_snip,
                new_output_snippet=new_text_snip,
                is_regression=True
            )

        # 2. Strategy: ignore_output
        if strategy == "ignore_output":
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy=strategy,
                verdict="SKIPPED",
                explanation="Cell output ignored by rule configuration.",
                old_output_snippet=old_text_snip,
                new_output_snippet=new_text_snip,
                is_regression=False
            )

        # 3. Strategy: exact_or_fuzzy
        if strategy == "exact_or_fuzzy":
            return self._compare_exact_or_fuzzy(
                cell_index, source_code, old_snap, new_snap, old_text_snip, new_text_snip
            )

        # 4. Strategy: schema_validation
        if strategy == "schema_validation":
            return self._compare_schema_validation(
                cell_index, source_code, old_snap, new_snap, old_text_snip, new_text_snip
            )

        # 5. Strategy: grounded_factual
        if strategy == "grounded_factual":
            if self.config.SKIP_AI_JUDGE or self.config.DRY_RUN:
                return CellComparisonReport(
                    cell_index=cell_index,
                    source_code=source_code,
                    strategy=strategy,
                    verdict="MATCH",
                    explanation="[AI Judge Skipped] Grounded search output marked OK in dry-run/skip mode.",
                    old_output_snippet=old_text_snip,
                    new_output_snippet=new_text_snip,
                    is_regression=False
                )
            
            # Run Grounded Verifier
            g_res = self.grounded_verifier.verify_factual_output(
                notebook_path=notebook_path,
                cell_index=cell_index,
                source_code=source_code,
                old_output=old_snap.text_content,
                new_output=new_snap.text_content
            )
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy=strategy,
                verdict=g_res.verdict,
                explanation=g_res.explanation,
                old_output_snippet=old_text_snip,
                new_output_snippet=new_text_snip,
                is_regression=g_res.is_regression
            )

        # 6. Default Strategy: semantic_llm
        if self.config.SKIP_AI_JUDGE or self.config.DRY_RUN:
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy=strategy,
                verdict="MATCH",
                explanation="[AI Judge Skipped] Output evaluated in dry-run/skip mode.",
                old_output_snippet=old_text_snip,
                new_output_snippet=new_text_snip,
                is_regression=False
            )

        judge_res = self.llm_judge.evaluate_cell_output(
            notebook_path=notebook_path,
            cell_index=cell_index,
            source_code=source_code,
            old_output=old_snap.text_content,
            new_output=new_snap.text_content
        )
        return CellComparisonReport(
            cell_index=cell_index,
            source_code=source_code,
            strategy=strategy,
            verdict=judge_res.verdict,
            explanation=judge_res.explanation,
            old_output_snippet=old_text_snip,
            new_output_snippet=new_text_snip,
            is_regression=judge_res.is_regression
        )

    def _compare_exact_or_fuzzy(
        self,
        cell_index: int,
        source_code: str,
        old_snap: CellOutputSnapshot,
        new_snap: CellOutputSnapshot,
        old_snip: str,
        new_snip: str
    ) -> CellComparisonReport:
        """Compares deterministic outputs with normalization."""
        # Clean whitespace
        old_clean = re.sub(r"\s+", " ", old_snap.text_content).strip()
        new_clean = re.sub(r"\s+", " ", new_snap.text_content).strip()

        if old_clean == new_clean:
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy="exact_or_fuzzy",
                verdict="MATCH",
                explanation="Exact textual output match.",
                old_output_snippet=old_snip,
                new_output_snippet=new_snip,
                is_regression=False
            )

        # Check for numeric token count or integer drift within 25%
        old_digits = re.findall(r"\b\d+\b", old_clean)
        new_digits = re.findall(r"\b\d+\b", new_clean)
        if old_digits and new_digits and len(old_digits) == len(new_digits):
            differences = [abs(int(a) - int(b)) / (int(a) or 1) for a, b in zip(old_digits, new_digits)]
            if max(differences) <= 0.35:
                return CellComparisonReport(
                    cell_index=cell_index,
                    source_code=source_code,
                    strategy="exact_or_fuzzy",
                    verdict="SLIGHT_VARIATION",
                    explanation=f"Minor numeric variation ({max(differences)*100:.1f}%), within acceptable tolerance.",
                    old_output_snippet=old_snip,
                    new_output_snippet=new_snip,
                    is_regression=False
                )

        return CellComparisonReport(
            cell_index=cell_index,
            source_code=source_code,
            strategy="exact_or_fuzzy",
            verdict="REGRESSION",
            explanation="Deterministic output changed unexpectedly.",
            old_output_snippet=old_snip,
            new_output_snippet=new_snip,
            is_regression=True
        )

    def _compare_schema_validation(
        self,
        cell_index: int,
        source_code: str,
        old_snap: CellOutputSnapshot,
        new_snap: CellOutputSnapshot,
        old_snip: str,
        new_snip: str
    ) -> CellComparisonReport:
        """Validates JSON structure conformance."""
        new_text = new_snap.text_content
        # Try to find JSON in markdown fences or raw text
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", new_text)
        candidate = json_match.group(1) if json_match else new_text

        try:
            parsed = json.loads(candidate.strip())
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy="schema_validation",
                verdict="MATCH",
                explanation=f"Valid JSON schema generated ({type(parsed).__name__} with {len(parsed)} keys/items).",
                old_output_snippet=old_snip,
                new_output_snippet=new_snip,
                is_regression=False
            )
        except Exception as e:
            return CellComparisonReport(
                cell_index=cell_index,
                source_code=source_code,
                strategy="schema_validation",
                verdict="REGRESSION",
                explanation=f"Generated output failed JSON validation: {e}",
                old_output_snippet=old_snip,
                new_output_snippet=new_snip,
                is_regression=True
            )
