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

"""Model selector formatting and ordering lint rules for Gemini API Cookbook.

This module validates the Colab form model selectors:
  - Form format validation: Verifies `# @param ["gemini-...", ...] {"allow-input":true, isTemplate: true}`.
  - Model ordering verification: Ensures models are sorted logically according to the cookbook styleguide:
    Flash-Lite -> Flash -> Pro, with Stable models preceding Preview/Experimental models.
  - Default selection check: Validates that the default assigned MODEL_ID exists in the selector options.

Use Cases:
  - Enforcing consistent and user-friendly model selection across all quickstarts and examples.
  - Ensuring new models can be batch-updated cleanly without syntax breakages.
"""

from typing import Any, Dict, List
import json
import logging
import pathlib
import re

from tools import config

logger = logging.getLogger(__name__)


def check_model_selector(
    notebook_data: Dict[str, Any],
    file_path: pathlib.Path,
    is_redirect: bool = False
) -> List[str]:
    """Validates that model selectors follow the canonical Colab form pattern and ordering.
    
    Args:
        notebook_data: Parsed JSON content of the notebook.
        file_path: Path to the notebook file.
        is_redirect: Whether the notebook is a stub redirecting elsewhere.
        
    Returns:
        A list of lint violation messages.
    """
    logger.debug("Checking model selector in %s", file_path)
    if is_redirect:
        return []
        
    violations = []
    cells = notebook_data.get("cells", [])
    
    for cell_idx, cell in enumerate(cells):
        if cell.get("cell_type") != "code":
            continue
            
        src = "".join(cell.get("source", []))
        
        # Look for model assignment with @param
        matches = config.MODEL_PARAM_SELECTOR_REGEX.findall(src)
        for default_model, options_json in matches:
            # 1. Parse options array
            try:
                # Convert single quotes if needed for valid JSON parsing
                formatted_json = options_json.replace("'", '"')
                options_list = json.loads(formatted_json)
            except Exception as e:
                violations.append(
                    f"Cell {cell_idx}: Malformed model selector list '{options_json}': {e}"
                )
                continue
                
            if not isinstance(options_list, list) or len(options_list) == 0:
                violations.append(
                    f"Cell {cell_idx}: Model selector @param must contain a non-empty list of model names."
                )
                continue
                
            # 2. Check if default model is present in the list
            clean_default = default_model.strip("\"'")
            clean_options = [opt.strip("\"'") for opt in options_list]
            if clean_default not in clean_options:
                violations.append(
                    f"Cell {cell_idx}: Default model '{clean_default}' is not listed in the selector options: {clean_options}."
                )
                
            # 3. Check model ordering (Lite -> Flash -> Pro, Stable -> Preview)
            sort_keys = [config.get_model_sort_key(opt) for opt in clean_options]
            if sort_keys != sorted(sort_keys):
                # Suggest sorted list
                sorted_options = sorted(clean_options, key=config.get_model_sort_key)
                violations.append(
                    f"Cell {cell_idx}: Model list in selector is not ordered according to styleguide (Lite -> Flash -> Pro, Stable -> Preview).\n"
                    f"  Current order:  {clean_options}\n"
                    f"  Expected order: {sorted_options}"
                )
                
    return violations
