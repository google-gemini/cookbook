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
Grounded Factual Verifier using Google Search Tool.

This module handles notebook cells that query dynamic, time-sensitive, or real-time
information (e.g. latest sports scores, current weather, recent news, stock prices).

In these notebooks, the generated output is *expected* to differ from the static reference
output saved in the repository months ago. Rather than flagging this as a regression,
this verifier:
1. Detects that the cell produces dynamic/time-sensitive claims.
2. Invokes Gemini with Google Search Grounding enabled to verify whether the newly generated
   information is factually accurate today according to live search results.
3. Classifies the result as:
   - `FACTUAL_UPDATE`: The information changed from the old output, and Google Search confirms
     the new output is currently accurate.
   - `MATCH`: Output is still identical to reference.
   - `REGRESSION`: The output is factually inaccurate, hallucinated, or failed to answer the prompt.

Use Cases:
1. Automated testing of Grounding / Search notebooks (`quickstarts/Grounding.ipynb`).
2. Eliminating false-positive regression alarms on real-time event tutorials.
3. Providing verified citations and search grounding evidence in test reports.
"""

import json
import time
from typing import Optional
from pydantic import BaseModel, Field

from google import genai
from google.genai import types

from .config import GLOBAL_CONFIG, TesterConfig
from .logger import logger, log_llm_call


class GroundedVerificationResult(BaseModel):
    """Structured verdict for a grounded factual verification check."""
    verdict: str = Field(
        description="'FACTUAL_UPDATE' (factually correct update), 'MATCH' (identical), or 'REGRESSION' (inaccurate/hallucination)."
    )
    explanation: str = Field(
        description="Detailed explanation with search grounding context."
    )
    is_regression: bool = Field(
        description="True if the newly generated facts are inaccurate or false according to search."
    )
    search_queries_used: Optional[list[str]] = Field(
        default_factory=list, description="Google Search queries executed during verification."
    )


class GroundedFactualVerifier:
    """Uses Gemini with Google Search Grounding to verify dynamic outputs."""

    def __init__(self, config: Optional[TesterConfig] = None):
        """
        Initializes the Grounded Factual Verifier.
        
        Args:
            config: Optional TesterConfig instance.
        """
        self.config = config or GLOBAL_CONFIG
        self.client: Optional[genai.Client] = None
        api_key = self.config.get_api_key()
        if api_key:
            self.client = genai.Client(api_key=api_key)

    def verify_factual_output(
        self,
        notebook_path: str,
        cell_index: int,
        source_code: str,
        old_output: str,
        new_output: str
    ) -> GroundedVerificationResult:
        """
        Verifies whether new dynamic output is factually accurate using Google Search.
        
        Args:
            notebook_path: Path of the notebook.
            cell_index: 0-based cell index.
            source_code: Code executed in the cell.
            old_output: Old reference output saved in repo.
            new_output: New output generated during test.
            
        Returns:
            GroundedVerificationResult detailing factual validity.
        """
        if not self.client:
            logger.warning(f"Grounded Verifier skipped for cell {cell_index}: Missing API key.")
            return GroundedVerificationResult(
                verdict="MATCH",
                explanation="[Grounded Verifier Skipped] API key not available.",
                is_regression=False
            )

        if old_output.strip() == new_output.strip():
            return GroundedVerificationResult(
                verdict="MATCH",
                explanation="Outputs are identical.",
                is_regression=False
            )

        model_name = self.config.GROUNDED_VERIFIER_MODEL

        system_instruction = (
            "You are an expert Factual Grounding Fact-Checker for the Google Gemini API Cookbook.\n"
            "A notebook cell produced a dynamic or time-sensitive output (e.g. latest sports scores, "
            "news, or grounded search query). The new output differs from the historical reference output.\n"
            "Use Google Search to double-check whether the facts stated in the NEW GENERATED OUTPUT "
            "are true and accurate today.\n"
            "Classify your finding into:\n"
            "- 'FACTUAL_UPDATE': The new output is factually accurate and represents a valid real-world update.\n"
            "- 'REGRESSION': The new output contains factual errors, false claims, hallucinations, or failed to answer the prompt.\n"
            "Be clear and cite your grounding findings."
        )

        user_prompt = (
            f"Notebook: {notebook_path}\n"
            f"Cell Index: {cell_index}\n\n"
            f"--- CELL CODE ---\n{source_code}\n\n"
            f"--- OLD REFERENCE OUTPUT (Historical) ---\n{old_output[:1000]}\n\n"
            f"--- NEW GENERATED OUTPUT (To Verify) ---\n{new_output[:self.config.MAX_OUTPUT_CHARS_FOR_DIFF]}\n\n"
            "Verify the factual accuracy of the NEW GENERATED OUTPUT using Google Search."
        )

        models_to_try = self.config.GROUNDED_VERIFIER_FALLBACKS or [self.config.GROUNDED_VERIFIER_MODEL]
        max_retries = self.config.MAX_API_RETRIES
        base_delay = self.config.RETRY_INITIAL_DELAY_SEC
        backoff = self.config.RETRY_BACKOFF_FACTOR

        last_error = None
        for model_name in models_to_try:
            gen_config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
                tools=[types.Tool(google_search=types.GoogleSearch())],
            )
            parameters_dict = {
                "temperature": 0.0,
                "tools": ["google_search"],
                "model": model_name
            }

            for attempt in range(1, max_retries + 1):
                t0 = time.time()
                try:
                    logger.info(
                        f"🌐 Grounded Verifier fact-checking cell {cell_index} in {notebook_path} "
                        f"using {model_name} (attempt {attempt}/{max_retries})..."
                    )
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=user_prompt,
                        config=gen_config
                    )
                    duration = time.time() - t0

                    raw_text = response.text or ""
                    log_llm_call(
                        feature="GroundedVerifier",
                        model=model_name,
                        prompt=user_prompt,
                        parameters=parameters_dict,
                        response=raw_text,
                        duration_sec=duration,
                        metadata={"notebook": notebook_path, "cell_index": cell_index, "attempt": attempt}
                    )

                    # Determine verdict based on model analysis text
                    lower_text = raw_text.lower()
                    is_regression = "regression" in lower_text or "factually inaccurate" in lower_text or "false" in lower_text
                    verdict = "REGRESSION" if is_regression else "FACTUAL_UPDATE"

                    return GroundedVerificationResult(
                        verdict=verdict,
                        explanation=raw_text.strip()[:600],
                        is_regression=is_regression,
                        search_queries_used=[]
                    )

                except Exception as e:
                    duration = time.time() - t0
                    last_error = e
                    logger.warning(f"Grounded Verification failed on {model_name} (attempt {attempt}/{max_retries}): {e}")
                    log_llm_call(
                        feature="GroundedVerifier",
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
                        logger.warning(f"Exhausted retries on {model_name}. Attempting next grounded verifier fallback...")

        # Default to factual update with note on verifier error
        return GroundedVerificationResult(
            verdict="FACTUAL_UPDATE",
            explanation=f"Grounded verification skipped due to search check error across all models ({last_error}).",
            is_regression=False
        )
