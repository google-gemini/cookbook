# Welcome to the Gemini API Cookbook

This cookbook provides a structured learning path for using the Gemini API, focusing on hands-on tutorials and practical examples.

**For comprehensive API documentation, visit [ai.google.dev](https://ai.google.dev/gemini-api/docs).**
<br><br>

## Navigating the Cookbook

This cookbook is organized into two main categories:

1.  **[Quick Starts](https://github.com/google-gemini/cookbook/tree/main/quickstarts/):**  Step-by-step guides covering both introductory topics ("[Get Started](./quickstarts/Get_started.ipynb)") and specific API features.
2.  **[Examples](https://github.com/google-gemini/cookbook/tree/main/examples/):** Practical use cases demonstrating how to combine multiple features.

We also showcase **Demos** in separate repositories, illustrating end-to-end applications of the Gemini API.
<br><br>

## What's New?

Here are the recent additions and updates to the Gemini API and the Cookbook: 

* **Gemini 2.5 models:** Explore the capabilities of the latest Gemini 2.5 models (Flash and Pro)! See the [Get Started Guide](./quickstarts/Get_started.ipynb) and the [thinking guide](./quickstarts/Get_started_thinking.ipynb) as they'll all be thinking ones.
* **Imagen and Veo**: Get started with our media generation model with this brand new [Veo guide](./quickstarts/Get_started_Veo.ipynb) and [Imagen guide](./quickstarts/Get_started_imagen.ipynb)!
* **LiveAPI**: Get started with the [multimodal Live API](./quickstarts/Get_started_LiveAPI.ipynb) and unlock new interactivity with Gemini.
* **Recently Added Guides:**
  * [Browser as a tool](./examples/Browser_as_a_tool.ipynb): Use a web browser for live and internal (intranet) web interactions
  * [Code execution](./quickstarts/Code_Execution.ipynb): Generating and running Python code to solve complex tasks and even output graphs
  * [Function calling](./quickstarts/Function_calling.ipynb): The function calling guide has been reworked and should better explain how to use that very convient capability.
  
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
*  [Get started with Veo](./quickstarts/Get_started_Veo.ipynb): Get started with our video generation capabilities 
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
and media generation ([Imagen](https://ai.google.dev/gemini-api/docs/imagen) and [Veo](https://ai.google.dev/gemini-api/docs/video)).
This SDK allows you to connect to the Gemini API through either
[Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.0-flash-exp) or
[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/gemini-v2).

The <code>[google-generativeai](https://pypi.org/project/google-generativeai)</code>
package will continue to support the original Gemini models.
It <em>can</em> also be used with Gemini 2 models, just with a limited feature
set. All new features will be developed in the new Google GenAI SDK.

See the [migration guide](https://ai.google.dev/gemini-api/docs/migrate) for details.
<br><br>

## Get Help

Ask a question on the [Google AI Developer Forum](https://discuss.ai.google.dev/).

## The Gemini API on Google Cloud Vertex AI

For enterprise developers, the Gemini API is also available on Google Cloud Vertex AI. See [this repo](https://github.com/GoogleCloudPlatform/generative-ai) for examples.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Thank you for developing with the Gemini API! We're excited to see what you create.
