# Gemini websockets Cookbook

This is a collection of websocket-specific examples and quickstarts for using the Gemini Live model.

Python users should build using the [Google GenAI SDK](https://ai.google.dev/gemini-api/docs/sdks) to access the Multimodal Live API, but as the underlying API is served over secure websockets, the following examples have been provided to help you understand how the protocol works.

To learn about what’s new in the recent Gemini model release and the new [Google GenAI SDKs](https://github.com/googleapis/python-genai), check out the [Gemini model page](https://ai.google.dev/gemini-api/docs/models). To start experimenting with the model now, head to [Google AI Studio](https://aistudio.google.com/prompts/new_chat) for prompting or to the [Multimodal Live API demo](https://aistudio.google.com/live) to try the new Live capabilities.
## Contents

Explore Gemini’s capabilities on your own local machine.

* [Live API starter script](./Get_started_LiveAPI.py) \- A locally runnable Python script using websockets that supports streaming audio in and audio + video out from your machine
* [Bash Websocket example](./shell_websockets.sh) \- A bash script using [`websocat`](https://github.com/vi/websocat) to interact with the Live API in a shell context

Explore Gemini’s capabilities through the following notebooks you can run through Google Colab.

* [Live API starter](./Get_started_LiveAPI.ipynb) \- Overview of the Multimodal Live API using websockets
* [Live API tool use](./Get_started_LiveAPI_tools.ipynb) \- Overview of tool use in the Live API with websockets
