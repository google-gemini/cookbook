# Copyright 2025 Keith Luton
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
Luton Field Model (LFM) - Core Deterministic Kernel
Version: 1.0.3
Author: Keith Luton
License: Apache 2.0 (See Header)

Description:
    A lightweight, deterministic physics kernel designed to offload 
    scaling law calculations from probabilistic LLMs. 
    It implements the Universal Scaling Law (P_k = P_0 * 4^-k) 
    to provide O(1) inference for fundamental constants.
"""

import math
import time
from dataclasses import dataclass

@dataclass
class InteractionResult:
    """Data structure for field interaction results."""
    scale_k: float
    pressure_pa: float
    interaction_strength: float
    compute_latency: float

class LutonFieldModel:
    """
    The LFM Kernel.
    
    Attributes:
        P0 (float): Vacuum Baseline Pressure (Pascals).
        L_PLANCK (float): Planck Length anchor (Meters).
    """
    
    # Universal Constants (defined as class attributes per Style Guide)
    P0: float = 5.44e71
    L_PLANCK: float = 1.616e-35
    
    # Configuration Constants (No magic numbers)
    STABILITY_LOCK_THRESHOLD: float = 0.99
    TANH_INPUT_SCALER: float = 2.0

    def get_pressure(self, k: float) -> float:
        """
        Calculates the vacuum pressure at a specific scale 'k' 
        using the Universal Scaling Law.

        Formula: P_k = P0 * 4^(-k)

        Args:
            k (float): The scale index (e.g., 0=Planck, 66=Nuclear, 204=Cosmos).

        Returns:
            float: Pressure in Pascals (Pa).
        """
        # Deterministic calculation (No hallucination possible)
        return self.P0 * (4 ** (-k))

    def get_geometric_pruning_factor(self, psi: float) -> float:
        """
        Calculates a context pruning factor for RAG pipelines based on 
        query complexity (Psi).

        Logic: Higher complexity (Psi) requires tighter focus (Higher Pruning).
        
        Args:
            psi (float): Normalized complexity score (0.0 to 1.0).

        Returns:
            float: Recommended pruning ratio (0.0 to 1.0).
        """
        # Clamp input
        psi = max(0.0, min(1.0, psi))
        
        # Stability Lock Threshold (Axiom VIII)
        if psi > self.STABILITY_LOCK_THRESHOLD:
            return 1.0  # Max focus/pruning
            
        # Non-linear activation (tanh) for smooth gradient
        return math.tanh(psi * self.TANH_INPUT_SCALER)

    def solve_interaction(self, k: float, psi: float, tau: float) -> InteractionResult:
        """
        Performs a full field interaction calculation.
        This simulates the 'Relational Product' of Psi and Tau fields.

        Args:
            k (float): Scale index.
            psi (float): Field compression (0.0 - 1.0).
            tau (float): Temporal coherence (0.0 - 1.0).

        Returns:
            InteractionResult: Object containing physical values and compute metrics.
        """
        start_time = time.perf_counter()
        
        # 1. Get Base Physics at Scale K
        pressure = self.get_pressure(k)
        length_scale = self.L_PLANCK * (2 ** k)
        
        # 2. Calculate Field Amplitude Unit
        # Psi_unit = L_k * sqrt(P_k)
        field_amplitude_unit = length_scale * math.sqrt(pressure)
        
        # 3. Relational Product (Simplified for Kernel Efficiency)
        # Interaction ~ (Psi * Tau) * Amplitude
        interaction_val = (psi * tau) * field_amplitude_unit
        
        end_time = time.perf_counter()
        latency = end_time - start_time
        
        # FIX: Return the Dataclass Instance (Not a Dictionary)
        # This satisfies the bot's request for type safety.
        return InteractionResult(
            scale_k=k,
            pressure_pa=pressure,
            interaction_strength=interaction_val,
            compute_latency=latency
        )


