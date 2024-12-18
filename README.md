# Welcome to the Gemini API Cookbook
This is a collection of guides and examples for the Gemini API, including [quickstart](https://github.com/google-gemini/cookbook/tree/main/quickstarts) tutorials for writing prompts and using different features of the API, and [examples](https://github.com/google-gemini/cookbook/tree/main/examples) of things you can build.

${\Large \textbf{\color[rgb]{0.12941,0.48235,0.99608}N\color[rgb]{0.57647,0.60392,1}e\color[rgb]{0.91765,0.47843,0.72157}w\color[rgb]{0.93333,0.30196,0.36471}:}}$ Check out the latest Gemini 2.0 capabilities in [the docs](https://ai.google.dev/gemini-api/docs/models/gemini-v2), [Google AI Studio](https://aistudio.google.com/app/live?model=gemini-2.0-flash-exp) and here in the [cookbook](./gemini-2/).

## Get started with the Gemini API
The Gemini API gives you access to Gemini [models](https://ai.google.dev/models/gemini) created by [Google DeepMind](https://deepmind.google/technologies/gemini/#introduction). Gemini models are built from the ground up to be multimodal, so you can reason seamlessly across text, images, code, and audio. You can use these to develop a [range of applications](https://ai.google.dev/examples/).

### Start developing
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Log in with your Google account.
3. [Create](https://aistudio.google.com/app/apikey) an API key.
4. Use a [quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Prompting.ipynb) for Python, or call the REST API [using curl](https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/Prompting_REST.ipynb).

## What's New?
We're excited to show you the latest additions to the Gemini API, and new notebooks.
* [Gemini 2.0](./gemini-2/): Explore the capabilities of the new Gemini 2.0 model, including [multimodal Live API](./gemini-2/live_api_starter.ipynb), [audio streaming applications with tool use](./gemini-2/live_api_tool_use.ipynb) and [Spatial understanding](./gemini-2/spatial_understanding.ipynb). 

## Table of contents

Learn about the capabilities of the Gemini API by checking out these quickstart tutorials.
* [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb): Start here to learn how you can set up your API key so you can get access to the Gemini API.
* [Counting Tokens](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Counting_Tokens.ipynb) Tokens are the basic inputs to the Gemini models. Through this notebook, you will gain a better understanding of tokens through an interactive experience.
* [Files](https://github.com/google-gemini/cookbook/blob/main/quickstarts/File_API.ipynb): Use the Gemini API to upload files (text, code, images, audio, video) and write prompts using them.
* [Audio](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Audio.ipynb): Learn how to use the Gemini API with audio files.
* [JSON mode](https://github.com/google-gemini/cookbook/blob/main/quickstarts/JSON_mode.ipynb): Discover how to use JSON mode.
* [Function Calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb): The Gemini API works great with code. Use this quickstart to learn how to write prompts to understand and call functions. Then check out the [function calling config](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling_config.ipynb) tutorial to learn more.
* [System Instructions](https://github.com/google-gemini/cookbook/blob/main/quickstarts/System_instructions.ipynb): Give models additional context on how to respond by setting system instructions.
* [Embeddings](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb): Create high-quality and task-specific embeddings.
* [Tuning](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Tuning.ipynb): Learn how to improve model performance on a specific task through tuning. 
* [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb): Solve complex tasks by Generating and running Python code based on plain-text instructions. 

You can find lots more in the [quickstarts folder](https://github.com/google-gemini/cookbook/tree/main/quickstarts), and check out the [examples folder](https://github.com/google-gemini/cookbook/tree/main/examples) for fun examples. We're also maintaining an [Awesome Gemini](Awesome_gemini.md) list of all the cool projects the community is building using Gemini. 

## Official SDKs
The Gemini API is a REST API. You can call the API using a command line tool like `curl` (and you can find REST examples [here](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest)), or by using one of our [official SDKs](https://ai.google.dev/gemini-api/docs/downloads):
* Python: [Google GenAI SDKs](https://github.com/googleapis/python-genai) will eventually replace the older [Developer SDK](https://github.com/google/generative-ai-python).
* [Node.js](https://github.com/google/generative-ai-js)
* [Dart (Flutter)](https://github.com/google/generative-ai-dart)
* [Android](https://github.com/google/generative-ai-android)
* [Swift](https://github.com/google/generative-ai-swift)
* [Go](https://github.com/google/generative-ai-go)

## Get help
Ask a question on the [Google AI Developer Forum](https://discuss.ai.google.dev/).

## The Gemini API on Google Cloud Vertex AI
If you're an enterprise developer looking to build on a fully managed platform, you can also use the Gemini API on Google Cloud. Check out this [repo](https://github.com/GoogleCloudPlatform/generative-ai) for lots of cool examples. 

## Contributing
Contributions are welcome. See [contributing](https://github.com/google-gemini/cookbook/blob/main/CONTRIBUTING.md) to learn more.

Thank you for developing with the Gemini API! We’re excited to see what you create.
