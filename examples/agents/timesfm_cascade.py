#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
===============================================================================
TIMESFM 4-TIER ZERO-DOWNTIME CASCADE FORECASTING ENGINE
===============================================================================
Contribution for google-research/timesfm providing a production-grade 4-tier
zero-downtime degradation cascade for foundation time-series forecasting:

1. Tier 1: Google Research TimesFM 2.5 (200M Parameters, PyTorch GPU/CPU)
   - Continuous quantile head (Q10, Q25, Q50, Q75, Q90)
2. Tier 2: ONNX Runtime / DirectML Hardware Accelerated Session
   - Edge and embedded acceleration with low-memory footprint
3. Tier 3: Statistical Damped Holt-Winters & Kalman Filter State-Space
   - Deterministic, sub-millisecond execution with expanding Gaussian uncertainty envelopes
4. Tier 4: Analytical Physics-Based (2-RC Battery ECM, Joule Thermal) & Brownian Simulators
   - Domain-specific physical boundary enforcement for robotics and cyber-physical systems

Designed for high-reliability robotics telemetry, battery sag forecasting,
thermal runaway detection, and financial time-series.

Requirements:
    pip install numpy (Optional: torch timesfm onnxruntime)
===============================================================================
"""

import os
import sys
import time
import math
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TimesFMCascade")

# Standard Normal Distribution Quantile Critical Values (Z-scores)
Z_SCORES = {
    "q10": -1.28155,
    "q25": -0.67449,
    "q50": 0.0,
    "q75": 0.67449,
    "q90": 1.28155,
}


# =============================================================================
# 1. TIER 3: STATISTICAL FORECASTING (HOLT-WINTERS & KALMAN FILTER)
# =============================================================================

class StatisticalFallbackForecaster:
    """
    Tier 3 (Statistical) Forecaster:
    Guarantees deterministic, sub-millisecond continuous quantile forecasts
    with zero external GPU or network dependencies.
    """

    def __init__(
        self,
        alpha_default: float = 0.35,
        beta_default: float = 0.15,
        phi_default: float = 0.95
    ):
        self.alpha_default = alpha_default
        self.beta_default = beta_default
        self.phi_default = phi_default

    def forecast_holt_winters(
        self,
        series: Union[List[float], np.ndarray],
        horizon: int = 24,
        alpha: Optional[float] = None,
        beta: Optional[float] = None,
        phi: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Damped Double Exponential Smoothing (Holt-Winters Trend Model)
        with continuous Gaussian quantile envelope estimation.
        """
        data = np.asarray(series, dtype=np.float64)
        if len(data) == 0:
            zeros = [0.0] * horizon
            return {
                "point_forecast": zeros,
                "quantiles": {k: list(zeros) for k in Z_SCORES},
                "residual_std": 0.0
            }

        if len(data) == 1:
            val = float(data[0])
            vals = [val] * horizon
            return {
                "point_forecast": vals,
                "quantiles": {k: list(vals) for k in Z_SCORES},
                "residual_std": 0.0
            }

        a = alpha if alpha is not None else self.alpha_default
        b = beta if beta is not None else self.beta_default
        damp = phi if phi is not None else self.phi_default

        # Initialize level and trend
        level = float(data[0])
        trend = float(data[1] - data[0]) if len(data) > 1 else 0.0

        fitted = np.zeros(len(data), dtype=np.float64)
        fitted[0] = level

        # In-sample filter pass
        for t in range(1, len(data)):
            val = float(data[t])
            last_level = level
            level = a * val + (1.0 - a) * (last_level + damp * trend)
            trend = b * (level - last_level) + (1.0 - b) * damp * trend
            fitted[t] = last_level + damp * trend

        # Compute empirical residual standard deviation
        residuals = data[1:] - fitted[1:]
        res_std = float(np.std(residuals)) if len(residuals) > 1 else max(1e-4, abs(level) * 0.01)
        if res_std < 1e-6:
            res_std = max(1e-4, abs(level) * 0.005)

        # Multi-step out-of-sample projection
        point_forecast = np.zeros(horizon, dtype=np.float64)
        quantiles: Dict[str, List[float]] = {k: [] for k in Z_SCORES}

        current_trend = trend
        current_level = level

        for h in range(1, horizon + 1):
            damp_sum = sum(damp ** i for i in range(1, h + 1))
            f_val = current_level + current_trend * damp_sum
            point_forecast[h - 1] = f_val

            # Expanding variance envelope over forecast horizon: sigma_h = sigma_e * sqrt(1 + 0.15 * (h - 1))
            horizon_scale = math.sqrt(1.0 + 0.15 * (h - 1))
            step_sigma = res_std * horizon_scale

            for q_name, z in Z_SCORES.items():
                quantiles[q_name].append(round(float(f_val + z * step_sigma), 5))

        return {
            "point_forecast": [round(float(x), 5) for x in point_forecast],
            "quantiles": quantiles,
            "residual_std": round(res_std, 5)
        }

    def forecast_kalman_autoregressive(
        self,
        series: Union[List[float], np.ndarray],
        horizon: int = 24,
        order: int = 2
    ) -> Dict[str, Any]:
        """
        Kalman Filter 1D Auto-regressive State-Space Forecaster with
        recursive covariance propagation.
        """
        data = np.asarray(series, dtype=np.float64)
        n = len(data)
        if n < 4:
            return self.forecast_holt_winters(series, horizon)

        # Estimate AR coefficients via Yule-Walker
        demeaned = data - np.mean(data)
        r = np.correlate(demeaned, demeaned, mode='full')[n - 1:]
        r /= r[0] if r[0] != 0 else 1.0

        p = min(order, n - 2)
        if p >= 2 and (1.0 - r[1] ** 2) != 0:
            phi1 = (r[1] * (1.0 - r[2])) / (1.0 - r[1] ** 2)
            phi2 = (r[2] - r[1] ** 2) / (1.0 - r[1] ** 2)
        else:
            phi1, phi2 = 0.85, 0.0

        # State transition matrix F and State vector x = [y_t, y_{t-1}]
        mean_val = float(np.mean(data))
        state = np.array([data[-1] - mean_val, data[-2] - mean_val if n > 1 else data[-1] - mean_val], dtype=np.float64)
        
        # Estimate process noise covariance
        residuals = []
        for i in range(2, n):
            pred = mean_val + phi1 * (data[i - 1] - mean_val) + phi2 * (data[i - 2] - mean_val)
            residuals.append(data[i] - pred)
        
        noise_var = float(np.var(residuals)) if residuals else 1e-3
        P = np.eye(2, dtype=np.float64) * noise_var

        point_forecast = []
        quantiles: Dict[str, List[float]] = {k: [] for k in Z_SCORES}

        F = np.array([[phi1, phi2], [1.0, 0.0]], dtype=np.float64)
        Q = np.array([[noise_var, 0.0], [0.0, 0.0]], dtype=np.float64)

        for h in range(1, horizon + 1):
            next_val = phi1 * state[0] + phi2 * state[1]
            state = np.array([next_val, state[0]], dtype=np.float64)
            pred_y = float(next_val + mean_val)
            point_forecast.append(round(pred_y, 5))

            # Propagate covariance: P = F P F^T + Q
            P = F @ P @ F.T + Q

            std_h = math.sqrt(max(1e-6, float(P[0, 0])))
            for q_name, z in Z_SCORES.items():
                quantiles[q_name].append(round(pred_y + z * std_h, 5))

        return {
            "point_forecast": point_forecast,
            "quantiles": quantiles,
            "residual_std": round(math.sqrt(noise_var), 5)
        }


# =============================================================================
# 2. TIER 4: ANALYTICAL PHYSICS & STOCHASTIC SIMULATORS
# =============================================================================

class PhysicsAndBrownianForecaster:
    """
    Tier 4 Forecaster:
    Domain-specific analytical physics and stochastic path simulators:
    - 2-RC Thevenin Battery Equivalent Circuit Model (ECM)
    - Joule Heating & MOSFET Thermal Runaway Model
    - Geometric Brownian Motion (GBM) Monte Carlo Path Generator
    """

    def forecast_battery_ecm(
        self,
        voltage_history: Union[List[float], np.ndarray],
        current_history: Union[List[float], np.ndarray],
        horizon_seconds: int = 60,
        dt: float = 1.0,
        nominal_capacity_ah: float = 10.0,
        lvc_cutoff_v: float = 21.0
    ) -> Dict[str, Any]:
        """
        2-RC Thevenin Battery Equivalent Circuit Model (ECM):
        V_term = V_ocv(SoC) - I * R0 - V_rc1 - V_rc2
        Computes dynamic voltage sag under projected motor load.
        """
        v_arr = np.asarray(voltage_history, dtype=np.float64)
        i_arr = np.asarray(current_history, dtype=np.float64)

        current_v = float(v_arr[-1]) if len(v_arr) > 0 else 24.2
        avg_i = float(np.mean(i_arr[-10:])) if len(i_arr) >= 10 else (float(i_arr[-1]) if len(i_arr) > 0 else 2.5)

        # 24V Pack Parameters (7S Li-ion or 8S LiFePO4)
        r0 = 0.045     # Ohmic internal resistance (Ohms)
        r1 = 0.025     # RC1 Polarization resistance
        c1 = 200.0     # RC1 Capacitance (Farads), tau1 = R1*C1 = 5.0s
        r2 = 0.035     # RC2 Polarization resistance
        c2 = 1200.0    # RC2 Capacitance (Farads), tau2 = R2*C2 = 42.0s

        # Estimate Current SoC from Open-Circuit Voltage (Linear 21.0V to 28.5V)
        soc_now = max(0.0, min(100.0, (current_v - lvc_cutoff_v) / (28.5 - lvc_cutoff_v) * 100.0))

        steps = max(1, int(horizon_seconds / dt))
        v_forecast = []
        soc_forecast = []
        tau1 = r1 * c1
        tau2 = r2 * c2

        for step in range(1, steps + 1):
            t = step * dt
            # Coulomb counting SoC depletion
            ah_used = (avg_i * t) / 3600.0
            soc_step = max(0.0, soc_now - (ah_used / nominal_capacity_ah) * 100.0)
            soc_forecast.append(round(soc_step, 2))

            # Update RC polarization voltages
            v_rc1 = avg_i * r1 * (1.0 - math.exp(-t / tau1))
            v_rc2 = avg_i * r2 * (1.0 - math.exp(-t / tau2))

            v_ocv_step = lvc_cutoff_v + (soc_step / 100.0) * (28.5 - lvc_cutoff_v)
            v_term = v_ocv_step - avg_i * r0 - v_rc1 - v_rc2
            v_forecast.append(round(float(v_term), 3))

        # Dynamic load surge quantiles (+/- 25% current surge)
        q10_v = [round(float(v - 0.25 * avg_i * r0 - 0.15), 3) for v in v_forecast]
        q25_v = [round(float(v - 0.12 * avg_i * r0 - 0.08), 3) for v in v_forecast]
        q50_v = [round(float(v), 3) for v in v_forecast]
        q75_v = [round(float(v + 0.08 * avg_i * r0 + 0.05), 3) for v in v_forecast]
        q90_v = [round(float(v + 0.15 * avg_i * r0 + 0.10), 3) for v in v_forecast]

        # Time to Empty (TTE) in minutes
        tte_minutes = (soc_now / 100.0 * nominal_capacity_ah) / max(0.1, avg_i) * 60.0

        # Low-Voltage Cutoff (LVC) breach horizon check
        lvc_breach_sec = None
        for idx, v10 in enumerate(q10_v):
            if v10 <= lvc_cutoff_v:
                lvc_breach_sec = (idx + 1) * dt
                break

        return {
            "soc_percent_current": round(soc_now, 2),
            "soc_percent_forecast": soc_forecast,
            "time_to_empty_minutes": round(tte_minutes, 1),
            "point_forecast": q50_v,
            "quantiles": {
                "q10": q10_v,
                "q25": q25_v,
                "q50": q50_v,
                "q75": q75_v,
                "q90": q90_v
            },
            "lvc_breach_seconds": lvc_breach_sec,
            "lvc_breach_predicted": lvc_breach_sec is not None
        }

    def forecast_joule_thermal(
        self,
        temp_history: Union[List[float], np.ndarray],
        current_history: Union[List[float], np.ndarray],
        horizon_seconds: int = 60,
        dt: float = 1.0,
        ambient_temp_c: float = 25.0
    ) -> Dict[str, Any]:
        """
        MOSFET & Motor Joule Heating Thermal Model:
        C_th * dT/dt = I_rms^2 * R_mosfet * 2 + P_sw - (T - T_amb) / R_th
        """
        t_arr = np.asarray(temp_history, dtype=np.float64)
        i_arr = np.asarray(current_history, dtype=np.float64)

        t_now = float(t_arr[-1]) if len(t_arr) > 0 else 28.5
        i_rms = float(np.mean(np.abs(i_arr[-10:]))) if len(i_arr) > 0 else 3.0

        r_mosfet = 0.008       # 8 mOhm MOSFET on-resistance per bridge leg
        p_switching = 0.85      # 850mW gate switching losses at 20kHz PWM
        c_th = 45.0            # Thermal heat capacity (J/K)
        r_th = 2.2             # Thermal resistance to ambient (K/W)

        p_heat = (i_rms ** 2) * r_mosfet * 2.0 + p_switching
        t_steady = ambient_temp_c + p_heat * r_th
        tau_th = r_th * c_th  # Thermal time constant ~ 99s

        steps = max(1, int(horizon_seconds / dt))
        temp_forecast = []

        for step in range(1, steps + 1):
            t = step * dt
            t_pred = t_steady + (t_now - t_steady) * math.exp(-t / tau_th)
            temp_forecast.append(round(float(t_pred), 2))

        q10_t = [round(float(t - 0.4), 2) for t in temp_forecast]
        q25_t = [round(float(t - 0.2), 2) for t in temp_forecast]
        q50_t = [round(float(t), 2) for t in temp_forecast]
        q75_t = [round(float(t + 0.5 * (step_idx + 1) / steps + 0.2), 2) for step_idx, t in enumerate(temp_forecast)]
        q90_t = [round(float(t + 1.2 * (step_idx + 1) / steps + 0.5), 2) for step_idx, t in enumerate(temp_forecast)]

        thermal_level = "NOMINAL"
        if q90_t[-1] >= 75.0:
            thermal_level = "CRITICAL_RUNAWAY"
        elif q90_t[-1] >= 60.0:
            thermal_level = "WARNING_ELEVATED"

        return {
            "current_temp_c": t_now,
            "steady_state_temp_c": round(t_steady, 2),
            "thermal_level": thermal_level,
            "point_forecast": q50_t,
            "quantiles": {
                "q10": q10_t,
                "q25": q25_t,
                "q50": q50_t,
                "q75": q75_t,
                "q90": q90_t
            }
        }

    def forecast_geometric_brownian_motion(
        self,
        prices: Union[List[float], np.ndarray],
        horizon: int = 24,
        dt: float = 1.0 / 78.0,
        num_simulations: int = 500
    ) -> Dict[str, Any]:
        """
        Simulates forward trajectories via Geometric Brownian Motion (GBM):
        dS(t) = mu * S(t) * dt + sigma * S(t) * dW(t)
        Returns empirical quantile distribution over Monte Carlo sample paths.
        """
        arr = np.asarray(prices, dtype=np.float64)
        if len(arr) < 2:
            base = float(arr[0]) if len(arr) == 1 else 100.0
            return {
                "point_forecast": [base] * horizon,
                "quantiles": {k: [base] * horizon for k in Z_SCORES},
                "volatility_annualized": 0.15,
                "drift_annualized": 0.05
            }

        log_returns = np.diff(np.log(np.maximum(1e-4, arr)))
        mu = float(np.mean(log_returns)) / dt if len(log_returns) > 0 else 0.0
        sigma = float(np.std(log_returns)) / math.sqrt(dt) if len(log_returns) > 1 else 0.20
        sigma = max(0.01, min(2.5, sigma))

        s0 = float(arr[-1])
        paths = np.zeros((num_simulations, horizon), dtype=np.float64)

        for i in range(num_simulations):
            drift = (mu - 0.5 * sigma ** 2) * dt
            diffusion = sigma * math.sqrt(dt) * np.random.normal(0, 1, horizon)
            log_increments = drift + diffusion
            log_path = np.cumsum(log_increments)
            paths[i, :] = s0 * np.exp(log_path)

        point_forecast = np.mean(paths, axis=0)
        q10 = np.percentile(paths, 10, axis=0)
        q25 = np.percentile(paths, 25, axis=0)
        q50 = np.percentile(paths, 50, axis=0)
        q75 = np.percentile(paths, 75, axis=0)
        q90 = np.percentile(paths, 90, axis=0)

        return {
            "point_forecast": [round(float(x), 4) for x in point_forecast],
            "quantiles": {
                "q10": [round(float(x), 4) for x in q10],
                "q25": [round(float(x), 4) for x in q25],
                "q50": [round(float(x), 4) for x in q50],
                "q75": [round(float(x), 4) for x in q75],
                "q90": [round(float(x), 4) for x in q90],
            },
            "volatility_annualized": round(sigma * math.sqrt(252 * 78), 4),
            "drift_annualized": round(mu * 252 * 78, 4)
        }


# =============================================================================
# 3. UNIFIED TIMESFM 4-TIER ENGINE
# =============================================================================

class TimesFMUnifiedEngine:
    """
    Google Research TimesFM Foundation Model Multi-Tier Forecaster.
    Transparently manages zero-downtime degradation across all 4 tiers.
    """

    def __init__(
        self,
        model_name: str = "google/timesfm-2.5-200m-pytorch",
        onnx_path: Optional[str] = None,
        max_context: int = 1024,
        max_horizon: int = 64,
        device: Optional[str] = None
    ):
        self.model_name = model_name
        self.onnx_path = onnx_path
        self.max_context = max_context
        self.max_horizon = max_horizon
        self.device = device or ("cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") != "" else "cpu")

        # Sub-engines
        self.statistical_forecaster = StatisticalFallbackForecaster()
        self.physics_forecaster = PhysicsAndBrownianForecaster()

        # Tier 1 (PyTorch)
        self.tier1_model = None
        self.tier1_ready = False

        # Tier 2 (ONNX)
        self.tier2_session = None
        self.tier2_ready = False

        # Active Tier Tracking
        self.active_tier = "TIER_3_STATISTICAL"

        # Initialize engines
        self._init_tier1()
        self._init_tier2()
        self._resolve_active_tier()

    def _init_tier1(self):
        """Attempts to load Google TimesFM 2.5 PyTorch model."""
        try:
            import torch
            import timesfm

            if hasattr(torch, "set_float32_matmul_precision"):
                torch.set_float32_matmul_precision("high")

            logger.info(f"[Tier 1] Attempting to load Google TimesFM 2.5 from {self.model_name}...")
            self.tier1_model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(self.model_name)
            self.tier1_model.compile(
                timesfm.ForecastConfig(
                    max_context=self.max_context,
                    max_horizon=self.max_horizon,
                    use_continuous_quantile_head=True,
                )
            )
            self.tier1_ready = True
            logger.info("[Tier 1] 🟢 TimesFM 2.5 PyTorch model ready!")
        except Exception as e:
            logger.info(f"[Tier 1 Notice] TimesFM PyTorch engine not active ({type(e).__name__}). Falling back.")
            self.tier1_ready = False

    def _init_tier2(self):
        """Attempts to initialize ONNX Runtime / DirectML session if model exists."""
        try:
            import onnxruntime as ort
            target_path = self.onnx_path or os.path.join(os.path.dirname(__file__), "weights", "timesfm_2p5_quantized.onnx")
            if os.path.exists(target_path):
                providers = ['DmlExecutionProvider', 'CPUExecutionProvider'] if 'DmlExecutionProvider' in ort.get_available_providers() else ['CPUExecutionProvider']
                self.tier2_session = ort.InferenceSession(target_path, providers=providers)
                self.tier2_ready = True
                logger.info("[Tier 2] 🟢 ONNX Runtime DirectML / CPU session initialized!")
            else:
                self.tier2_ready = False
        except Exception as e:
            logger.info(f"[Tier 2 Notice] ONNX Runtime not active ({type(e).__name__}). Falling back.")
            self.tier2_ready = False

    def _resolve_active_tier(self):
        if self.tier1_ready:
            self.active_tier = "TIER_1_TIMESFM_PYTORCH"
        elif self.tier2_ready:
            self.active_tier = "TIER_2_ONNX_DIRECTML"
        else:
            self.active_tier = "TIER_3_STATISTICAL"

    def forecast_series(
        self,
        series: Union[List[float], np.ndarray],
        horizon: int = 24,
        freq: int = 0,
        return_quantiles: bool = True
    ) -> Dict[str, Any]:
        """
        Executes zero-shot multi-step time-series forecasting across the cascade.
        """
        start_time = time.perf_counter()
        data = np.asarray(series, dtype=np.float32)
        horizon = max(1, min(self.max_horizon, int(horizon)))

        # Tier 1: TimesFM PyTorch
        if self.tier1_ready and self.tier1_model is not None:
            try:
                point_fc, quant_fc = self.tier1_model.forecast(
                    horizon=horizon,
                    inputs=[data],
                    freq=[freq]
                )
                pt = point_fc[0, :horizon].tolist()
                
                if quant_fc is not None and len(quant_fc.shape) >= 3:
                    q10 = quant_fc[0, :horizon, 0].tolist()
                    q25 = quant_fc[0, :horizon, 1].tolist() if quant_fc.shape[2] > 1 else [p - 0.5 * (p - q10[i]) for i, p in enumerate(pt)]
                    q50 = quant_fc[0, :horizon, 2].tolist() if quant_fc.shape[2] > 2 else pt
                    q75 = quant_fc[0, :horizon, 3].tolist() if quant_fc.shape[2] > 3 else [p + 0.5 * (q10[i] - p) for i, p in enumerate(pt)]
                    q90 = quant_fc[0, :horizon, -1].tolist()
                else:
                    stat_res = self.statistical_forecaster.forecast_holt_winters(data, horizon)
                    res_std = stat_res["residual_std"]
                    q10 = [round(float(p + Z_SCORES["q10"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                    q25 = [round(float(p + Z_SCORES["q25"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                    q50 = [round(float(p), 5) for p in pt]
                    q75 = [round(float(p + Z_SCORES["q75"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                    q90 = [round(float(p + Z_SCORES["q90"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]

                elapsed = (time.perf_counter() - start_time) * 1000.0
                return {
                    "tier_used": "TIER_1_TIMESFM_PYTORCH",
                    "point_forecast": pt,
                    "quantiles": {"q10": q10, "q25": q25, "q50": q50, "q75": q75, "q90": q90} if return_quantiles else None,
                    "latency_ms": round(elapsed, 2)
                }
            except Exception as e:
                logger.warning(f"[Tier 1 Error] Execution failed: {e}. Degrading to Tier 2/3.")

        # Tier 2: ONNX Runtime
        if self.tier2_ready and self.tier2_session is not None:
            try:
                input_name = self.tier2_session.get_inputs()[0].name
                inp = np.expand_dims(data[-self.max_context:], axis=0)
                ort_outs = self.tier2_session.run(None, {input_name: inp})
                pt = ort_outs[0][0, :horizon].tolist()
                stat_res = self.statistical_forecaster.forecast_holt_winters(data, horizon)
                res_std = stat_res["residual_std"]

                q10 = [round(float(p + Z_SCORES["q10"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                q25 = [round(float(p + Z_SCORES["q25"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                q50 = [round(float(p), 5) for p in pt]
                q75 = [round(float(p + Z_SCORES["q75"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]
                q90 = [round(float(p + Z_SCORES["q90"] * res_std * math.sqrt(1 + 0.15 * i)), 5) for i, p in enumerate(pt)]

                elapsed = (time.perf_counter() - start_time) * 1000.0
                return {
                    "tier_used": "TIER_2_ONNX_DIRECTML",
                    "point_forecast": pt,
                    "quantiles": {"q10": q10, "q25": q25, "q50": q50, "q75": q75, "q90": q90} if return_quantiles else None,
                    "latency_ms": round(elapsed, 2)
                }
            except Exception as e:
                logger.warning(f"[Tier 2 Error] Execution failed: {e}. Degrading to Tier 3.")

        # Tier 3: Statistical Fallback (Holt-Winters / Kalman)
        stat_res = self.statistical_forecaster.forecast_holt_winters(data, horizon)
        elapsed = (time.perf_counter() - start_time) * 1000.0
        return {
            "tier_used": "TIER_3_STATISTICAL",
            "point_forecast": stat_res["point_forecast"],
            "quantiles": stat_res["quantiles"] if return_quantiles else None,
            "residual_std": stat_res["residual_std"],
            "latency_ms": round(elapsed, 2)
        }


# =============================================================================
# 4. RUNNABLE DEMO & BENCHMARK
# =============================================================================

def main():
    print("=" * 80)
    print("TIMESFM 4-TIER ZERO-DOWNTIME CASCADE ENGINE DEMO")
    print("=" * 80)

    engine = TimesFMUnifiedEngine()
    print(f"Active Primary Engine Tier: {engine.active_tier}\n")

    # 1. Telemetry Sine + Noise Data
    t = np.linspace(0, 20, 100)
    synthetic_telemetry = 24.0 + 1.5 * np.sin(t) + np.random.normal(0, 0.1, 100)

    # 2. Run Foundation/Statistical Forecast
    print("[1] Running Multi-Step Telemetry Forecast (Horizon: 24 steps)...")
    fc = engine.forecast_series(synthetic_telemetry, horizon=24)
    print(f"Tier Used: {fc['tier_used']} (Latency: {fc['latency_ms']}ms)")
    print(f"Point Forecast (first 5): {fc['point_forecast'][:5]}")
    print(f"Q10 Lower (first 5):      {fc['quantiles']['q10'][:5]}")
    print(f"Q50 Median (first 5):     {fc['quantiles']['q50'][:5]}")
    print(f"Q90 Upper (first 5):      {fc['quantiles']['q90'][:5]}")

    # 3. Run Tier 4 Battery ECM Simulation
    print("\n[2] Running Tier 4 Battery 2-RC Equivalent Circuit Model (ECM)...")
    voltage_hist = [25.2, 25.1, 24.9, 24.8, 24.6]
    current_hist = [3.2, 3.5, 4.0, 4.2, 3.8]
    battery_res = engine.physics_forecaster.forecast_battery_ecm(voltage_hist, current_hist, horizon_seconds=60)
    print(f"Current SoC: {battery_res['soc_percent_current']}%")
    print(f"Time to Empty: {battery_res['time_to_empty_minutes']} min")
    print(f"LVC Breach Predicted: {battery_res['lvc_breach_predicted']}")
    print(f"Voltage Q10 (first 5s): {battery_res['quantiles']['q10'][:5]}")
    print(f"Voltage Q50 (first 5s): {battery_res['quantiles']['q50'][:5]}")

    # 4. Run Tier 4 Joule Thermal Simulation
    print("\n[3] Running Tier 4 MOSFET Joule Heating Thermal Model...")
    temp_hist = [28.0, 29.5, 31.0, 33.2]
    thermal_res = engine.physics_forecaster.forecast_joule_thermal(temp_hist, current_hist, horizon_seconds=60)
    print(f"Current Temp: {thermal_res['current_temp_c']}°C, Steady State: {thermal_res['steady_state_temp_c']}°C")
    print(f"Thermal Alarm Level: {thermal_res['thermal_level']}")
    print(f"Temp Q90 (first 5s): {thermal_res['quantiles']['q90'][:5]}")


if __name__ == "__main__":
    main()
