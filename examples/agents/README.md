# Production Asynchronous Tool Loop & Edge Inference Cascade

This directory contains production-grade recipes and patterns for building advanced agentic workflows and cyber-physical systems using the official **Google GenAI SDK** (`google-genai`).

---

## Recipes & Components

### 1. `multi_turn_async_tool_loop.py`: Async Tool Execution & Thought Signature Preservation
- **Problem**: Passing `async def` coroutines, WebSocket RPCs, or ROS 2 actions directly to the SDK's default Automatic Function Calling (AFC) can trigger `UnsupportedFunctionError` or block the event loop because built-in AFC executes functions synchronously. Furthermore, naively modifying candidate parts or stringifying turns can drop the cryptographic `thought_signature` and thought parts returned by Gemini 3 and thinking models.
- **Solution**:
  1. Sets `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)` inside `GenerateContentConfig`.
  2. Resolves tool calls concurrently using `asyncio.gather` over registered async coroutines.
  3. Appends raw `Candidate.content` directly to turn history, strictly preserving cryptographic `thought_signature` and thought blocks across intermediate turns.
  4. Keeps intermediate turns unconstrained while enforcing structured Pydantic schemas (`response_mime_type="application/json"`, `response_json_schema=Schema`) on the final text generation turn.
  5. Implements `<UNTRUSTED_DATA>` container fencing to prevent prompt injection from untrusted external inputs.

### 2. `timesfm_cascade.py`: 4-Tier Zero-Downtime TimesFM Degradation Cascade
- **Problem**: Deploying foundation time-series forecasting models (e.g. TimesFM 2.5 200M) on edge robotics or safety-critical controllers poses availability risks due to potential GPU OOM, missing dependencies, or strict sub-millisecond real-time deadline requirements.
- **Solution**: A 4-tier zero-downtime fallback cascade:
  - **Tier 1 (PyTorch)**: `timesfm.TimesFM_2p5_200M_torch` with continuous quantile head (Q10, Q25, Q50, Q75, Q90).
  - **Tier 2 (ONNX)**: Quantized ONNX session for low-overhead edge hardware acceleration.
  - **Tier 3 (Statistical)**: Sub-millisecond deterministic Holt-Winters exponential smoothing and Kalman filtering with dynamic expanding variance.
  - **Tier 4 (Physics / Stochastic)**: 2-RC Thevenin battery equivalent circuit model (ECM), Joule heating thermal equilibrium solver, and Geometric Brownian Motion (GBM).

### 3. `concordia_embodied_gm.py`: Embodied 3D Game Master
- **Problem**: Agent-based social simulations (such as DeepMind Concordia) traditionally run in text-only or turn-based sandbox environments disconnected from real-time spatial physics, 3D graphics viewports (Three.js), and physical robotics actuators.
- **Solution**: Bridges Concordia narrative simulations with real-time 3D environments via structured action evaluation schemas, multi-companion banter coordination, dynamic gravity/lighting mutations, and standardized HTTP/WebSocket directive dispatch.

---

## Verification & Tests

Run the comprehensive pytest suite:

```bash
pytest examples/agents/tests/test_gemini_cookbook.py -v
```
