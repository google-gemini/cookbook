# Gemini 2.0 Cookbook

This is a collection of examples and quickstarts for using the **experimental** [Gemini 2.0 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-v2) model.

To learn about what’s new in the 2.0 model release and the new [Google GenAI SDKs](https://github.com/googleapis/python-genai), check out the [Gemini 2.0 model page](https://ai.google.dev/gemini-api/docs/models/gemini-v2). To start experimenting with the model now, head to [Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.0-flash-exp) for prompting or to the [Multimodal Live API demo](https://aistudio.google.com/live) to try the new Live capabilities.

## Contents

Explore Gemini 2.0’s capabilities through the following notebooks using Google Colab.

* [Getting Started](./get_started.ipynb) \- A comprehensive overview using the GenAI SDK
* [Live API starter](./live_api_starter.ipynb) \- Overview of the Multimodal Live API using the GenAI SDK
* [Live API tool use](./live_api_tool_use.ipynb) \- Overview of tool use in the Live API with the GenAI SDK
* [Plotting and mapping](./plotting_and_mapping.ipynb) \- Demo showing search, code and function calling with the Live API
* [Search tool](./search_tool.ipynb) \- Quick start using the Search tool with the unary and Live APIs in the GenAI SDK
* [Spatial understanding](./spatial_understanding.ipynb) \- Comprehensive overview of 2D spatial understanding capabilities with the GenAI SDK
* [Spatial understanding (3D)](./spatial_understanding_3d.ipynb) \- Comprehensive overview of 3D spatial understanding capabilities with the GenAI SDK

Or explore on your own local machine.

* [Live API starter script](./live_api_starter.py) \- A locally runnable Python script using GenAI SDK that supports streaming audio in and audio + video out from your machine

Also find websocket-specific examples in the [`websockets`](./websockets/) directory.
