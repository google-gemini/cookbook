# Gemini API Python SDK sample code

This directory contains sample code for key features of the SDK, organised by high level feature.

These samples are embedded in parts of the [documentation](https://ai.google.dev), most notably in the [API reference](https://ai.google.dev/api).

Each file is structured as a runnable test case, ensuring that samples are executable and functional. Each test demonstrates a single concept, and contains region tags that are used to demarcate the test scaffolding from the spotlight code. If you are contributing, code within region tags should follow sample code best practices - being clear, complete and concise.

## Contents

| File                                                     | Description |
|----------------------------------------------------------| ----------- |
| [cache.py](./cache.py)                                   | Context caching |
| [chat.py](./chat.py)                                     | Multi-turn chat conversations |
| [code_execution.py](./code_execution.py)                 | Executing code |
| [configure_model_parameters.py](./configure_model_parameters.py) | Setting model parameters |
| [controlled_generation.py](./controlled_generation.py)   | Generating content with output constraints (e.g. JSON mode) |
| [count_tokens.py](./count_tokens.py)                     | Counting input and output tokens |
| [embed.py](./embed.py)                                   | Generating embeddings |
| [files.py](./files.py)                                   | Managing files with the File API |
| [function_calling.py](./function_calling.py)             | Using function calling |
| [models.py](./models.py)                                 | Listing models and model metadata |
| [safety_settings.py](./safety_settings.py)               | Setting and using safety controls |
| [system_instruction.py](./system_instruction.py)         | Setting system instructions |
| [text_generation.py](./text_generation.py)               | Generating text |
| [tuned_models.py](./tuned_models.py)                     | Creating and managing tuned models |
