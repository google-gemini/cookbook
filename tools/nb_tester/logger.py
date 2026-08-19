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
Structured Logging and Observability Module for Notebook Testing.

This module provides fine-grained logging for all stages of notebook testing:
- Kernel lifecycle events (startup, cell execution, timeouts, errors).
- Rule resolution and dispatch decisions.
- Security scanner findings and risk assessments.
- **LLM Call Observability**: Every Gemini call (Security Auditor, Output Judge, Grounded Verifier)
  is logged in full detail, capturing:
    * The exact model called.
    * The prompt sent (cleanly truncated for massive inputs, noting original length).
    * Generation parameters (temperature, maxOutputTokens, tools).
    * The response received (raw and parsed).
    * Latency and token usage metadata.

Use Cases:
1. Debugging why an AI judge classified a cell output as a regression.
2. Tracking LLM prompts sent during security review of PRs.
3. Providing clear, readable console output in local development while maintaining
   rich structured logs in persistent file artifacts for CI post-mortems.
"""

import logging
import sys
import json
import time
from typing import Any, Dict, Optional
import pathlib


class LLMCallFormatter:
    """Helper to format and sanitize LLM prompts and responses for logging."""

    @staticmethod
    def truncate_text(text: str, max_chars: int = 1500) -> str:
        """
        Truncates long text while adding metadata on original length.
        
        Args:
            text: The original text to truncate.
            max_chars: Maximum character limit.
            
        Returns:
            Truncated string with character count indicator if truncated.
        """
        if not text:
            return ""
        if len(text) <= max_chars:
            return text
        half = max_chars // 2
        omitted = len(text) - max_chars
        return f"{text[:half]}\n\n[... {omitted} characters omitted ...]\n\n{text[-half:]}"


def setup_logger(
    name: str = "nb_tester",
    level: int = logging.INFO,
    log_file: Optional[pathlib.Path] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Configures and returns a structured logger with both stream and file handlers.
    
    Args:
        name: Name of the logger instance.
        level: Default logging level.
        log_file: Optional path to write persistent log file.
        verbose: If True, sets console output to DEBUG.
        
    Returns:
        Configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else level)
    logger.handlers.clear()

    # Console Handler (Human-readable, no terminal-clear spam)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if verbose else level)
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File Handler (Detailed with file & line numbers)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()


def log_llm_call(
    feature: str,
    model: str,
    prompt: str,
    parameters: Dict[str, Any],
    response: Any,
    duration_sec: float,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logs an LLM call with detailed prompt, parameters, response, and duration.
    
    Per user rule: All LLM calls must be explicitly logged with prompt,
    parameters, and response received. Long payloads are cleanly truncated.
    
    Args:
        feature: The feature making the call (e.g. 'SecurityAuditor', 'OutputJudge', 'GroundedVerifier').
        model: Name of the model invoked.
        prompt: The prompt text sent to the model.
        parameters: Dict of hyper-parameters (temperature, max_output_tokens, etc.).
        response: The response object or text received from the model.
        duration_sec: Execution duration in seconds.
        metadata: Optional extra context (notebook name, cell index).
    """
    meta_str = f" Context: {json.dumps(metadata)}" if metadata else ""
    truncated_prompt = LLMCallFormatter.truncate_text(prompt, max_chars=1500)
    
    # Format response representation
    if isinstance(response, str):
        truncated_response = LLMCallFormatter.truncate_text(response, max_chars=2000)
    elif hasattr(response, "text"):
        truncated_response = LLMCallFormatter.truncate_text(getattr(response, "text", "") or "", max_chars=2000)
    else:
        truncated_response = LLMCallFormatter.truncate_text(str(response), max_chars=2000)

    log_entry = (
        f"\n{'='*70}\n"
        f"🤖 [LLM Call - {feature}] Model: {model} (Elapsed: {duration_sec:.2f}s){meta_str}\n"
        f"⚙️ Parameters: {json.dumps(parameters)}\n"
        f"{'-'*70}\n"
        f"📝 PROMPT ({len(prompt)} chars):\n{truncated_prompt}\n"
        f"{'-'*70}\n"
        f"🎯 RESPONSE:\n{truncated_response}\n"
        f"{'='*70}"
    )
    logger.info(log_entry)
