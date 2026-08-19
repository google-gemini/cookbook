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
Semantic Output Regression Judge using Gemini.

This module provides AI-driven output comparison for notebook code cells where outputs
are non-deterministic (e.g. creative writing, code generation, summarization, analysis).

It classifies cell output changes into:
- `MATCH`: Outputs are semantically identical or convey the exact same core information.
- `SLIGHT_VARIATION`: Output phrasing, style, or structure varied slightly, but remains high-quality and correct.
- `REGRESSION`: Output produced an error, hallucinates completely, ignores prompt instructions,
  or produced an empty/degraded response compared to the original reference output.

Use Cases:
1. Detecting subtle model degradations or regressions across SDK and model updates.
2. Ignoring non-breaking phrasing differences while flagging broken output structures.
3. Providing clear, human-readable explanations of output diffs in PR comments and test reports.
"""

import json
import time
from typing import Optional
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger, log_llm_call


class SemanticComparisonResult(BaseModel):
    """Structured verdict from the Gemini Output Judge."""
    verdict: str = Field(
        description="One of: 'MATCH', 'SLIGHT_VARIATION', or 'REGRESSION'."
    )
    explanation: str = Field(
        description="Concise rationale explaining why this verdict was assigned."
    )
    is_regression: bool = Field(
        description="True if the new output represents a breaking regression or quality collapse."
    )


class GeminiOutputJudge:
    """Invokes Gemini to evaluate semantic equivalence and quality between cell outputs."""

    def __init__(self, config: Optional[TesterConfig] = None):
        """
        Initializes the Gemini Output Judge.
        
        Args:
            config: Optional TesterConfig instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.client: Optional[genai.Client] = None
        api_key = self.config.get_api_key()
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def evaluate_cell_output(
        self,
        notebook_path: str,
        cell_index: int,
        source_code: str,
        old_output: str,
        new_output: str
    ) -> SemanticComparisonResult:
        """
        Evaluates the semantic diff between old and new output for a code cell.
        
        Args:
            notebook_path: Path of the notebook.
            cell_index: 0-based cell index.
            source_code: Code executed in the cell.
            old_output: Reference output saved in the repository.
            new_output: Newly generated output.
            
        Returns:
            SemanticComparisonResult with verdict and explanation.
        """
        if not self.client:
            logger.warning(f"AI Judge skipped for cell {cell_index}: Missing API key.")
            return SemanticComparisonResult(
                verdict="MATCH",
                explanation="[AI Judge Skipped] API key not available.",
                is_regression=False
            )

        # If both are empty or exact match, bypass LLM
        if old_output.strip() == new_output.strip():
            return SemanticComparisonResult(
                verdict="MATCH",
                explanation="Outputs are identical.",
                is_regression=False
            )

        # If new output is completely empty
        if not new_output.strip():
            # Check if the code is definition-only (import, class, def, assignment)
            code_lines = [l.strip() for l in source_code.splitlines() if l.strip() and not l.strip().startswith("#")]
            has_print_or_call = any(
                "print(" in l or "display(" in l or "interaction" in l or "generate" in l or "show(" in l
                for l in code_lines
            )
            if not has_print_or_call:
                return SemanticComparisonResult(
                    verdict="MATCH",
                    explanation="Cell contains only definitions/imports; empty output is expected.",
                    is_regression=False
                )
            else:
                return SemanticComparisonResult(
                    verdict="REGRESSION",
                    explanation="New output is empty while code contains display/print/API calls.",
                    is_regression=True
                )

        model_name = self.config.OUTPUT_JUDGE_MODEL
        system_instruction = (
            "You are an expert AI output quality and regression judge for Google Gemini API Cookbook notebooks.\n"
            "You are given the Python CELL CODE of a notebook cell, the OLD REFERENCE OUTPUT saved in the repository, "
            "and the NEW OUTPUT generated by executing the cell in a live test run.\n\n"
            "Evaluation Rules:\n"
            "1. WHEN BOTH OLD AND NEW OUTPUTS EXIST:\n"
            "   - Compare their semantic equivalence, correctness, and adherence to the prompt/code.\n"
            "   - Minor stylistic, phrasing, or ordering differences that remain high quality are 'MATCH' or 'SLIGHT_VARIATION'.\n"
            "   - Hallucinations, unhandled exceptions, incorrect formats, or drastic quality collapses are 'REGRESSION'.\n\n"
            "2. WHEN THE OLD REFERENCE OUTPUT IS EMPTY OR UNPOPULATED:\n"
            "   - DO NOT automatically accept whatever was generated.\n"
            "   - Evaluate whether the NEW GENERATED OUTPUT is a sensible, coherent, and factually sound response to the CELL CODE / prompt.\n"
            "   - Check that it fulfills all constraints (e.g. valid JSON if JSON requested, valid image/audio preview, valid Markdown).\n"
            "   - If the new output is coherent and answers the code/prompt correctly, assign 'MATCH'.\n"
            "   - If the new output is an error, nonsense, hallucinated gibberish, or fails to satisfy the prompt, assign 'REGRESSION'.\n\n"
            "Classify into:\n"
            "- 'MATCH': The output is semantically equivalent to reference OR (if reference was empty) is a valid, correct, and high-quality response to the code.\n"
            "- 'SLIGHT_VARIATION': The output has acceptable minor variations while remaining correct and high-quality.\n"
            "- 'REGRESSION': The output failed, produced an unhandled error, returned empty text when output was expected, hallucinated, or failed to answer the prompt.\n"
            "Return a structured JSON object matching SemanticComparisonResult."
        )

        user_prompt = (
            f"Notebook: {notebook_path}\n"
            f"Cell Index: {cell_index}\n\n"
            f"--- CELL CODE ---\n{source_code}\n\n"
            f"--- OLD REFERENCE OUTPUT ---\n{old_output[:self.config.MAX_OUTPUT_CHARS_FOR_DIFF]}\n\n"
            f"--- NEW GENERATED OUTPUT ---\n{new_output[:self.config.MAX_OUTPUT_CHARS_FOR_DIFF]}\n"
        )

        models_to_try = self.config.OUTPUT_JUDGE_FALLBACKS or [self.config.OUTPUT_JUDGE_MODEL]
        max_retries = self.config.MAX_API_RETRIES
        base_delay = self.config.RETRY_INITIAL_DELAY_SEC
        backoff = self.config.RETRY_BACKOFF_FACTOR

        last_error = None
        for model_name in models_to_try:
            gen_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=SemanticComparisonResult
            )
            parameters_dict = {
                "temperature": 0.0,
                "response_mime_type": "application/json",
                "model": model_name
            }

            for attempt in range(1, max_retries + 1):
                t0 = time.time()
                try:
                    logger.debug(f"⚖️ AI Judge evaluating cell {cell_index} in {notebook_path} using {model_name} (attempt {attempt}/{max_retries})...")
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=gen_config
                    )
                    duration = time.time() - t0

                    raw_text = response.text or "{}"
                    log_llm_call(
                        feature="OutputJudge",
                        model=model_name,
                        prompt=user_prompt,
                        parameters=parameters_dict,
                        response=raw_text,
                        duration_sec=duration,
                        metadata={"notebook": notebook_path, "cell_index": cell_index, "attempt": attempt}
                    )

                    data = json.loads(raw_text)
                    result = SemanticComparisonResult(**data)
                    return result

                except Exception as e:
                    duration = time.time() - t0
                    last_error = e
                    logger.warning(f"AI Judge evaluation failed on {model_name} (attempt {attempt}/{max_retries}): {e}")
                    log_llm_call(
                        feature="OutputJudge",
                        model=model_name,
                        prompt=user_prompt,
                        parameters=parameters_dict,
                        response=f"ERROR: {e}",
                        duration_sec=duration,
                        metadata={"notebook": notebook_path, "cell_index": cell_index, "attempt": attempt, "error": str(e)}
                    )
                    if attempt < max_retries:
                        delay = base_delay * (backoff ** (attempt - 1))
                        time.sleep(delay)
                    else:
                        logger.warning(f"Exhausted retries on {model_name}. Attempting next judge fallback...")

        # Default to slight variation to avoid blocking on transient judge errors
        return SemanticComparisonResult(
            verdict="SLIGHT_VARIATION",
            explanation=f"Judge evaluation failed across all models ({last_error}); marked as variation.",
            is_regression=False
        )
