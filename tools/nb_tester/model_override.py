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
Dynamic Model Identifier Override Module for Notebook Testing Suite.

This module provides in-memory AST and pattern transformation capabilities to
override MODEL_ID (and related model assignment variables) across all code cells
in Jupyter Notebooks during testing without modifying notebook files on disk.

Problem & Motivation:
When validating the Gemini API Cookbook against a specific Gemini model version
(e.g. a newly launched model like gemini-3.7-flash, a flagship preview like
gemini-3.1-pro-preview, or an early-access/canary model), developers and CI
pipelines need to run the entire notebook test suite with that specific model
consistently applied, rather than relying on whatever default model was statically
hardcoded in each individual notebook.

Key Capabilities:
1. In-Memory Transformation: Transforms notebook code cells in kernel memory only,
   leaving repository .ipynb files completely untouched.
2. Comprehensive Pattern Matching: Handles all common Python assignment patterns for
   model constants, including:
   - Simple string assignments: MODEL_ID = "gemini-2.5-flash"
   - Colab @param dropdown forms: MODEL_ID = "gemini-2.5-flash" # @param [...]
   - Single-quoted strings: MODEL_ID = 'gemini-1.5-pro'
   - Chained multi-variable assignments: EMBEDDING_MODEL_ID = MODEL_ID = "..."
   - Type-annotated assignments: MODEL_ID: str = "..."
   - Indented assignments inside setup functions or blocks.
   - Related model constants: MODEL_NAME, model_id.
3. Preamble Injection: Injects MODEL_ID = "<override_model>" and
   os.environ["MODEL_ID"] = "<override_model>" into the isolated kernel
   preamble so that initial environment state and downstream helpers resolve to the
   overridden model immediately.
4. Detailed Audit Logging: Logs every transformed cell index, showing the original
   model string and the newly applied override model for full visibility.

Use Cases:
1. Testing the whole cookbook against a new Gemini release (e.g. nb_tester --all --model gemini-3.7-flash).
2. Testing specific quickstarts with pre-release or experimental models (e.g. nb_tester -n quickstarts/Get_started_thinking.ipynb --model gemini-3.1-pro-preview).
3. Running dry-run audits to inspect which notebooks would be affected by a model migration.
"""

import re
from typing import Optional, Tuple
import nbformat

from .logger import logger


class ModelOverrideTransformer:
    """Transforms notebook cells in-memory to override MODEL_ID assignments when model families match."""

    # Matches assignments to MODEL_ID, MODEL_NAME, MODEL, model_id, model with quoted string literals only
    MODEL_ASSIGNMENT_PATTERN = re.compile(
        r"^(\s*(?:[\w\.]+\s*=\s*)*(?:MODEL_ID|MODEL_NAME|MODEL|model_id|model)(?:\s*:\s*[^=]+)?\s*=\s*)(?:\"([^\"]+)\"|\'([^\']+)\')(.*)$",
        re.MULTILINE
    )

    @staticmethod
    def classify_model_family(model_name: str) -> str:
        """
        Classifies a Gemini/GenAI model identifier into its functional family.
        This prevents overriding specialized models (e.g., -live, -tts, -image, embedding)
        with a standard text model unless the override model belongs to the same family.

        Args:
            model_name: The model identifier string (with or without 'models/' prefix).

        Returns:
            Canonical family string (e.g., 'text', 'live', 'tts', 'image', 'embedding', etc.).
        """
        clean = (model_name or "").strip().lower()
        if clean.startswith("models/"):
            clean = clean[len("models/"):]

        if "live-translate" in clean:
            return "live-translate"
        if "transcribe-live" in clean:
            return "transcribe-live"
        if "-live" in clean or clean.startswith("gemini-live"):
            return "live"
        if "transcribe" in clean:
            return "transcribe"
        if "tts" in clean:
            return "tts"
        if "image" in clean or clean.startswith("imagen") or "nano-banana" in clean:
            return "image"
        if "embedding" in clean or clean == "aqa":
            return "embedding"
        if clean.startswith("veo"):
            return "veo"
        if clean.startswith("lyria"):
            return "lyria"
        if "robotics" in clean:
            return "robotics"
        if "computer-use" in clean:
            return "computer-use"
        if "deep-research" in clean:
            return "deep-research"
        if "omni" in clean:
            return "omni"
        if "learnlm" in clean:
            return "learnlm"
        return "text"

    def __init__(self, override_model: Optional[str] = None):
        """
        Initializes the ModelOverrideTransformer.

        Args:
            override_model: The Gemini model identifier to enforce across compatible notebook cells.
        """
        self.override_model = override_model.strip() if override_model else None
        self.override_family = (
            self.classify_model_family(self.override_model) if self.override_model else None
        )

    def is_active(self) -> bool:
        """
        Checks if model overriding is currently enabled.

        Returns:
            True if an override model string is configured, False otherwise.
        """
        return bool(self.override_model)

    def transform_cell_source(self, source: str, cell_index: int = 0) -> Tuple[str, int]:
        """
        Transforms a single code cell's source string to replace compatible model assignments.
        Only overrides a model assignment if its family matches `self.override_family`.

        Args:
            source: Raw Python source code of the cell.
            cell_index: 0-based cell index for logging context.

        Returns:
            Tuple of (transformed_source_code, number_of_replacements_made).
        """
        if not self.is_active() or not source:
            return source, 0

        replacements = 0

        def _replace_match(match: re.Match) -> str:
            nonlocal replacements
            prefix = match.group(1)
            current_model = match.group(2) or match.group(3) or ""
            suffix = match.group(4)
            original_match = match.group(0).strip()

            current_family = self.classify_model_family(current_model)
            if current_family != self.override_family:
                logger.info(
                    f"  ⏭️ [Model Override Preserved] Cell {cell_index}: "
                    f"keeping '{current_model}' (family='{current_family}') because override "
                    f"'{self.override_model}' is family='{self.override_family}'"
                )
                return match.group(0)

            replacements += 1
            # Preserve 'models/' prefix if original model had it and override doesn't
            target_model = self.override_model
            if current_model.startswith("models/") and not target_model.startswith("models/"):
                target_model = f"models/{target_model}"

            new_line = f'{prefix}"{target_model}"{suffix}'
            logger.info(
                f"  🔄 [Model Override] Cell {cell_index}: "
                f"'{original_match}' -> '{new_line.strip()}'"
            )
            return new_line

        transformed = self.MODEL_ASSIGNMENT_PATTERN.sub(_replace_match, source)
        return transformed, replacements

    def transform_notebook(
        self,
        nb: nbformat.NotebookNode,
        notebook_path: str = ""
    ) -> Tuple[nbformat.NotebookNode, int]:
        """
        Applies model override transformations across all code cells of an in-memory notebook.

        Args:
            nb: In-memory NotebookNode object (will be modified in-place).
            notebook_path: Path/name of the notebook for logging context.

        Returns:
            Tuple of (modified_notebook, total_replacements_applied).
        """
        if not self.is_active():
            return nb, 0

        total_overrides = 0
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type == "code" and cell.source:
                new_source, count = self.transform_cell_source(cell.source, cell_index=idx)
                if count > 0:
                    cell.source = new_source
                    total_overrides += count

        if total_overrides > 0:
            logger.info(
                f"🎯 Applied {total_overrides} model override(s) in '{notebook_path}' -> {self.override_model}"
            )
        else:
            logger.debug(
                f"ℹ️ No compatible '{self.override_family}' MODEL_ID assignments found to override in '{notebook_path}'."
            )

        return nb, total_overrides

    def generate_preamble_code(self) -> str:
        """
        Generates Python code to be injected into the kernel mock preamble for model override.

        Returns:
            Python code snippet declaring MODEL_ID and environment variables.
        """
        if not self.is_active():
            return ""

        return (
            f"# Injected by ModelOverrideTransformer (family={self.override_family!r})\n"
            f"MODEL_ID = {self.override_model!r}\n"
            f"MODEL_NAME = {self.override_model!r}\n"
            f"model_id = {self.override_model!r}\n"
            f"os.environ['MODEL_ID'] = {self.override_model!r}\n"
        )
