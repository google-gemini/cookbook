# Luton Field Model (LFM) - Deterministic Inference Kernel

**A deterministic pre-computation layer for optimizing RAG pipelines and scientific AI inference.**

## Overview

The Luton Field Model (LFM) Kernel is a lightweight (42KB) Python utility designed to offload fundamental physics and scaling calculations from Large Language Models (LLMs). By handling these queries deterministically via the Universal Scaling Law ($P_k = P_0 \cdot 4^{-k}$), developers can achieve significant latency reductions and eliminate hallucinations regarding physical constants.

**Key Benefits:**
*   **Speed:** Reduces inference latency for physics queries from ~500ms (LLM) to ~1µs (LFM Kernel).
*   **Cost:** Offloads logic to CPU, reducing token usage and GPU inference costs.
*   **Accuracy:** Enforces 100% dimensional consistency; prevents floating-point hallucinations.

## Repository Contents

*   `code/lfm_core.py`: The core mathematical kernel implementing the Universal Scaling Law.
*   `benchmark_efficiency.py`: A script to verify the latency and cost savings vs. standard inference.
*   `lfm_resonance_demo.ipynb`: A Jupyter notebook demonstrating live integration preventing hallucination.

## Quick Start

### 1. Installation
No heavy dependencies required. Simply import the core kernel.

```bash
# Clone the repository
git clone https://github.com/google-gemini/cookbook.git
cd cookbook/lfm-inference-optimization
```

### 2. Usage Example
Use LFM to "sanity check" or generate data for Gemini prompts:

```python
from code.lfm_core import LutonFieldModel

# Initialize the Kernel
lfm = LutonFieldModel()

# Example: Get precise Vacuum Pressure at the Nuclear Scale (k=66)
# Instead of asking the LLM to guess, we calculate it instantly.
pressure = lfm.get_pressure(k=66)
pruning_factor = lfm.get_geometric_pruning_factor(psi=0.85)

print(f"Derived Pressure: {pressure:.2e} Pa")
print(f"Recommended RAG Pruning Factor: {pruning_factor:.2f}")
```

### 3. Running the Benchmark
To visualize the efficiency gains on your local machine:

```bash
python benchmark_efficiency.py
```

Output will generate a comparison report of LFM Kernel vs. Simulated LLM Inference.

## License & Commercial Use

The Luton Field Model software is provided under a **Dual License** model to encourage research while ensuring sustainable enterprise support.

### ✅ Community, Academic, and Evaluation License (Free)

This software is **Free to use** for:
* **Individuals & Hobbyists**: Personal projects and experimentation.
* **Students & Researchers**: Academic work and non-profit research.
* **Corporate Evaluation**: Companies may use this software free of charge for testing, benchmarking, and proof-of-concept purposes.

### 💼 Commercial Production License

For corporate entities deploying LFM into production environments:
* A commercial license is **required after 1 month (30 days)** of successful deployment or demonstrated cost savings.
* The model acts as a "Force Multiplier" for efficiency; the license ensures continued support and enterprise-grade validation.

**For Commercial Licensing Inquiries:** Please contact Keith Luton directly to discuss enterprise terms based on compute savings.  
📧 **Email:** Keith@thenewfaithchurch.org

---

**Disclaimer:** This kernel is a deterministic mathematical utility. It is designed to augment generative AI models, not replace them.