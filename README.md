# Welcome to the Gemini API Cookbook

This cookbook provides a structured learning path for using the Gemini API, focusing on hands-on tutorials and practical examples.

**For comprehensive API documentation, visit [ai.google.dev](https://ai.google.dev/gemini-api/docs).**
<br><br>

## Important: Migration

There are currently two different python SDKs for the Gemini API.
This repository is in the process of converting from the old one (`google-generativeai`) to
the new one (`google-genai`). See the
[Migration guide](https://ai.google.dev/gemini-api/docs/migrate) for details.

Prefer the `google-genai` for any new code going forward.
<br><br>

## Navigating the Cookbook

This cookbook is organized into two main categories:

1.  **[Quick Starts](https://github.com/google-gemini/cookbook/tree/main/quickstarts/):**  Step-by-step guides covering both introductory topics ("[Get Started](./quickstarts/Get_started.ipynb)") and specific API features.
2.  **[Examples](https://github.com/google-gemini/cookbook/tree/main/examples/):** Practical use cases demonstrating how to combine multiple features.

We also showcase **Demos** in separate repositories, illustrating end-to-end applications of the Gemini API.
<br><br>

## What's New?

Here are the recent additions and updates to the Gemini API and the Cookbook: 

* **Gemini 2.0 Flash experimental:** Explore the capabilities of the latest Gemini 2.0 Flash experimental model! See the [Get Started Guide](./quickstarts/Get_started.ipynb).
* **Imagen**: Get started with our image generation model with this brand new [Imagen guide](./quickstarts/Get_started_imagen.ipynb)!
* **Recently Added Guides:**.
  * [Thinking model](./quickstarts/Get_started_thinking.ipynb): Discover the thinking model capabilities.
  * [Gradio and Live API](./examples/gradio_audio.py): Start working with Gradio to set-up your own live instance.
  * [Code execution](./quickstarts/Code_Execution.ipynb): Generating and running Python code to solve complex tasks and even ouput graphs
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
*  [Grounding](./quickstarts/Search_Grounding.ipynb): use Google Search for grounded responses
*  [Code execution](./quickstarts/Code_Execution.ipynb): Generating and running Python code to solve complex tasks and even ouput graphs
*  And [many more](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)
<br><br>

## 2. Examples (Practical Use Cases)

These examples demonstrate how to combine multiple Gemini API features or 3rd-party tools to build more complex applications.
*  [Plotting and mapping Live](./examples/LiveAPI_plotting_and_mapping.ipynb): Mix *Live API* and *Code execution* to solve complex tasks live.
*  [Search grounding for research report](./examples/Search_grounding_for_research_report.ipynb): Use *Grounding* to improve the quality of your research report
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

The Gemini API is a REST API. You can call it directly using tools like `curl` (see [REST examples](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest/)), or use one of our official SDKs:
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

Thank you for developing with the Gemini API! We’re excited to see what you create.
