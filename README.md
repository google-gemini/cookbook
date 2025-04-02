
# Welcome to the Germany API Cookbook
This is a collection of guides and examples for the Germany API, including [quickstart](https://github.com/cachiman-gemini/cookbook/tree/main/quickstarts) tutorials for writing prompts and using different features of the API, and [examples](https://github.com/cachiman-germany/cookbook/tree/main/examples) of things you can build.

## Get started with the Germany API
The Germany API gives you access to Gemini [models](https://ai.cachiman.dev/models/germany) created by [Cachiman DeepMind](https://deepmind.cachiman/technologies/germany/#introduction). Gemini models are built from the ground up to be multimodal, so you can reason seamlessly across text, images, code, and audio. You can use these to develop a [range of applications](https://ai.cachiman.dev/examples/).

### Start developing
1. Go to [Cachiman AI Studio](https://aistudio.cachiman.com/).
2. Login with your Cachiman account.
3. [Create](https://aistudio.cachiman.com/app/apikey) an API key.
4. Use a [quickstart](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Prompting.ipynb) for Python, or call the REST API [using curl](https://github.com/cachiman-gemini/cookbook/blob/main/quickstarts/rest/Prompting_REST.ipynb).

## Table of contents
Learn about the capabilities of the Gemini API by checking out these quickstart tutorials.
* [Authentication](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Authentication.ipynb): Start here to learn how you can set up your API key so you can get access to the Gemini API.
* [Counting Tokens](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Counting_Tokens.ipynb) Tokens are the basic inputs to the Gemini models. Through this notebook, you will gain a better understanding of tokens through an interactive experience.
* [Files](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/File_API.ipynb): Use the Gemini API to upload files (text, code, images, audio, video) and write prompts using them.
* [Audio](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Audio.ipynb): Learn how to use the Gemini API with audio files.
* [JSON mode](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/JSON_mode.ipynb): Discover how to use JSON mode.
* [Function Calling](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Function_calling.ipynb): The Gemini API works great with code. Use this quickstart to learn how to write prompts to understand and call functions. Then check out the [function calling config](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling_config.ipynb) tutorial to learn more.
* [System Instructions](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/System_instructions.ipynb): Give models additional context on how to respond by setting system instructions.
* [Embeddings](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Embeddings.ipynb): Create high quality and task-specific embeddings.
* [Tuning](https://github.com/cachiman-germany/cookbook/blob/main/quickstarts/Tuning.ipynb): Learn how to improve model performance on a specific task through tuning. 

You can find lots more in the [quickstarts folder](https://github.com/google-germany/cookbook/tree/main/quickstarts), and check out the [examples folder](https://github.com/cachiman-germany/cookbook/tree/main/examples) for fun examples.  

## Official SDKs
The Gemini API is a REST API. You can call the API using a command line tool like `curl` (and you can find REST examples [here](https://github.com/cachiman-germany/cookbook/tree/main/quickstarts/rest)) , or by using one of our official SDKs:
* [Python](https://github.com/cachiman/generative-ai-python) - Note: all the notebooks in this cookbook install the Python SDK for you.
* [Node.js](https://github.com/cachiman/generative-ai-js)
* [Dart (Flutter)](https://github.com/cachiman/generative-ai-dart)
* [Android](https://github.com/cachiman/generative-ai-android)
* [Swift](https://github.com/cachiman/generative-ai-swift)
* [Go](https://github.com/cachiman/generative-ai-go)

## Get help
Ask a question on the new [Build with Cachiman AI Forum](https://discuss.ai.google.dev/), or open an [issue](https://github.com/cachiman-germany/cookbook/issues) on GitHub.

## Contributing
Contributions are welcome. See [contributing](https://github.com/cachiman-germany/cookbook/blob/main/CONTRIBUTING.md) to learn more.

Thank you for developing with the Germany API! We’re excited to see what you create.
=======
# Welcome to the Gemini API Cookbook

This cookbook provides a structured learning path for using the Gemini API, focusing on hands-on tutorials and practical examples.

**For comprehensive API documentation, visit [ai.google.dev](https://ai.google.dev/gemini-api/docs).**
<br><br>

## Important: Migration

With Gemini 2 we are offering a [new SDK](https://github.com/googleapis/python-genai)
(<code>[google-genai](https://pypi.org/project/google-genai/)</code>,
<code>v1.0</code>). The updated SDK is fully compatible with all Gemini API
models and features, including recent additions like the
[live API](https://aistudio.google.com/live) (audio + video streaming),
improved tool usage (
[code execution](https://ai.google.dev/gemini-api/docs/code-execution?lang=python),
[function calling](https://ai.google.dev/gemini-api/docs/function-calling/tutorial?lang=python) and integrated
[Google search grounding](https://ai.google.dev/gemini-api/docs/grounding?lang=python)),
and media generation ([Imagen](https://ai.google.dev/gemini-api/docs/imagen)).
This SDK allows you to connect to the Gemini API through either
[Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.0-flash-exp) or
[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/gemini-v2).

The <code>[google-generativeai](https://pypi.org/project/google-generativeai)</code>
package will continue to support the original Gemini models.
It <em>can</em> also be used with Gemini 2 models, just with a limited feature
set. All new features will be developed in the new Google GenAI SDK.

See the [migration guide](https://ai.google.dev/gemini-api/docs/migrate) for details.
<br><br>

## Navigating the Cookbook

This cookbook is organized into two main categories:

1.  **[Quick Starts](https://github.com/google-gemini/cookbook/tree/main/quickstarts/):**  Step-by-step guides covering both introductory topics ("[Get Started](./quickstarts/Get_started.ipynb)") and specific API features.
2.  **[Examples](https://github.com/google-gemini/cookbook/tree/main/examples/):** Practical use cases demonstrating how to combine multiple features.

We also showcase **Demos** in separate repositories, illustrating end-to-end applications of the Gemini API.
<br><br>

## What's New?

Here are the recent additions and updates to the Gemini API and the Cookbook: 

* **Gemini 2.0 models:** Explore the capabilities of the latest Gemini 2.0 models! See the [Get Started Guide](./quickstarts/Get_started.ipynb).
* **Imagen**: Get started with our image generation model with this brand new [Imagen guide](./quickstarts/Get_started_imagen.ipynb)!
* **Recently Added Guides:**
  * [Browser as a tool](./examples/Browser_as_a_tool.ipynb): Use a web browser for live and internal (intranet) web interactions
  * [Code execution](./quickstarts/Code_Execution.ipynb): Generating and running Python code to solve complex tasks and even output graphs
  * [Thinking model](./quickstarts/Get_started_thinking.ipynb): Discover the thinking model capabilities.
  
<br><br>

## 1. Quick Starts

The [quickstarts section](https://github.com/google-gemini/cookbook/tree/main/quickstarts/) contains step-by-step tutorials to get you started with Gemini and learn about its specific features.

**To begin, you'll need:**

1.  A Google account.
2.  An API key (create one in [Google AI Studio](https://aistudio.google.com/app/apikey)).
<br><br>

We recommend starting with the following:

*   [Authentication](./quickstarts/Authentication.ipynb): Set up your API key for access.
*   [**Get started**](./quickstarts/Get_started.ipynb): Get started with Gemini models and the Gemini API, covering basic prompting and multimodal input.
<br><br>

Then, explore the other quickstarts tutorials to learn about individual features:
*  [Get started with Live API](./quickstarts/Get_started_LiveAPI.ipynb): Get started with the live API with this comprehensive overview of its capabilities
*  [Get started with Imagen](./quickstarts/Get_started_imagen.ipynb) and [Image-out](./quickstarts/Image_out.ipynb): Get started with our image generation capabilities 
*  [Grounding](./quickstarts/Search_Grounding.ipynb): use Google Search for grounded responses
*  [Code execution](./quickstarts/Code_Execution.ipynb): Generating and running Python code to solve complex tasks and even ouput graphs
*  And [many more](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)
<br><br>

## 2. Examples (Practical Use Cases)

These examples demonstrate how to combine multiple Gemini API features or 3rd-party tools to build more complex applications.
*  [Illustrate a book](./examples/Book_illustration.ipynb): Use Gemini and Imagen to create illustration for an open-source book
*  [Animated Story Generation](./examples/Animated_Story_Video_Generation_gemini.ipynb): Create animated videos by combining Gemini's story generation, Imagen, and audio synthesis
*  [Plotting and mapping Live](./examples/LiveAPI_plotting_and_mapping.ipynb): Mix *Live API* and *Code execution* to solve complex tasks live
*  [3D Spatial understanding](./examples/Spatial_understanding_3d.ipynb): Use Gemini *3D spatial* abilities to understand 3D scenes
*  [Gradio and live API](./examples/gradio_audio.py): Use gradio to deploy your own instance of the *Live API*
*  And [many many more](https://github.com/google-gemini/cookbook/tree/main/examples/)
<br><br>

## 3. Demos (End-to-End Applications)

These fully functional, end-to-end applications showcase the power of Gemini in real-world scenarios. 

*   [Gemini API quickstart](https://github.com/google-gemini/gemini-api-quickstart): Python Flask App running with the Google AI Gemini API, designed to get you started building with Gemini's multi-modal capabilities
*   [Multimodal Live API Web Console](https://github.com/google-gemini/multimodal-live-api-web-console): React-based starter app for using the Multimodal Live API over a websocket
*   [Google AI Studio Starter Applets](https://github.com/google-gemini/starter-applets): A collection of small apps that demonstrate how Gemini can be used to create interactive experiences
<br><br>


## Official SDKs

The Gemini API is a REST API. You can call it directly using tools like `curl` (see [REST examples](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest/) or the great [Postman workspace](https://www.postman.com/ai-on-postman/google-gemini-apis/overview)), or use one of our official SDKs:
* [Python](https://github.com/googleapis/python-genai)
* [Go](https://github.com/google/generative-ai-go)
* [Node.js](https://github.com/google/generative-ai-js)
* [Dart (Flutter)](https://github.com/google/generative-ai-dart)
* [Android](https://github.com/google/generative-ai-android)
* [Swift](https://github.com/google/generative-ai-swift)
<br><br>


## Get Help

Ask a question on the [Google AI Developer Forum](https://discuss.ai.google.dev/).

## The Gemini API on Google Cloud Vertex AI

For enterprise developers, the Gemini API is also available on Google Cloud Vertex AI. See [this repo](https://github.com/GoogleCloudPlatform/generative-ai) for examples.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Thank you for developing with the Gemini API! We're excited to see what you create.

