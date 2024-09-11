# Welcome to the Gemini API Cookbook
This is a collection of guides and examples for the Gemini API, including [quickstart](https://github.com/google-gemini/cookbook/tree/main/quickstarts) tutorials for writing prompts and using different features of the API, and [examples](https://github.com/google-gemini/cookbook/tree/main/examples) of things you can build.

## Get started with the Gemini API
The Gemini API gives you access to Gemini [models](https://ai.google.dev/models/gemini) created by [Google DeepMind](https://deepmind.google/technologies/gemini/#introduction). Gemini models are built from the ground up to be multimodal, so you can reason seamlessly across text, images, code, and audio. You can use these to develop a [range of applications](https://ai.google.dev/examples/).

### Start developing
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Login with your Google account.
3. [Create](https://aistudio.google.com/app/apikey) an API key.
4. Use a [quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Prompting.ipynb) for Python, or call the REST API [using curl](https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/Prompting_REST.ipynb).

## What's New?
We're excited to show you the latest additions to the Gemini API, and new notebooks.
* [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb): Solve complex tasks by generating and running python code based on plain-text instructions. 
* [VectorDB](https://github.com/google-gemini/cookbook/blob/main/examples/chromadb/Vectordb_with_chroma.ipynb): Create a vector database and retrieve answers to questions from the database. 

## Table of contents

Learn about the capabilities of the Gemini API by checking out these quickstart tutorials.
* [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb): Start here to learn how you can set up your API key so you can get access to the Gemini API.
* [Counting Tokens](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Counting_Tokens.ipynb) Tokens are the basic inputs to the Gemini models. Through this notebook, you will gain a better understanding of tokens through an interactive experience.
* [Files](https://github.com/google-gemini/cookbook/blob/main/quickstarts/File_API.ipynb): Use the Gemini API to upload files (text, code, images, audio, video) and write prompts using them.
* [Audio](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Audio.ipynb): Learn how to use the Gemini API with audio files.
* [JSON mode](https://github.com/google-gemini/cookbook/blob/main/quickstarts/JSON_mode.ipynb): Discover how to use JSON mode.
* [Function Calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb): The Gemini API works great with code. Use this quickstart to learn how to write prompts to understand and call functions. Then check out the [function calling config](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling_config.ipynb) tutorial to learn more.
* [System Instructions](https://github.com/google-gemini/cookbook/blob/main/quickstarts/System_instructions.ipynb): Give models additional context on how to respond by setting system instructions.
* [Embeddings](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb): Create high quality and task-specific embeddings.
* [Tuning](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Tuning.ipynb): Learn how to improve model performance on a specific task through tuning. 
* [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb): Solve complex tasks by Generating and runing python code based on plain-text instructions. 

You can find lots more in the [quickstarts folder](https://github.com/google-gemini/cookbook/tree/main/quickstarts), and check out the [examples folder](https://github.com/google-gemini/cookbook/tree/main/examples) for fun examples. We're also maintaining an [Awesome Gemini](Awesome_gemini.md) list of all the cool projects the community is building using Gemini. 

## Official SDKs
The Gemini API is a REST API. You can call the API using a command line tool like `curl` (and you can find REST examples [here](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest)) , or by using one of our official SDKs:
* [Python](https://github.com/google/generative-ai-python) - Note: all the notebooks in this cookbook install the Python SDK for you, and this cookbook is the best place to find Python examples.
* [Node.js](https://github.com/google/generative-ai-js)
* [Dart (Flutter)](https://github.com/google/generative-ai-dart)
* [Android](https://github.com/google/generative-ai-android)
* [Swift](https://github.com/google/generative-ai-swift)
* [Go](https://github.com/google/generative-ai-go)

## Get help
Ask a question on the [Google AI Developer Forum](https://discuss.ai.google.dev/).

## The Gemini API on Google Cloud Vertex AI
If you're an enterprise developer looking to build on a fully-managed platform, you can also use the Gemini API on Google Cloud. Check out this [repo](https://github.com/GoogleCloudPlatform/generative-ai) for lots of cool examples. 

## Contributing
Contributions are welcome. See [contributing](https://github.com/google-gemini/cookbook/blob/main/CONTRIBUTING.md) to learn more.

Thank you for developing with the Gemini API! We’re excited to see what you create.
