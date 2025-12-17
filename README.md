# Welcome to the Gemini API Cookbook

This cookbook provides a structured learning path for using the Gemini API, focusing on hands-on tutorials and practical examples.

**For comprehensive API documentation, visit [ai.google.dev](https://ai.google.dev/gemini-api/docs).**
<br><br>

---
> **Gemini 3**: For the most recent updates on our latest generation, please check the [Get Started](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#gemini3) and the [thinking](./quickstarts/Get_started_thinking.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb#gemini3) guides who include [migration guides](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#gemini3migration).
> 
> **🍌 Nano-Banana Pro**: Go bananas with our new flagship image generation model with thinking and search grounding and 4K image generation. Get started [here](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb#nano-banana-pro) with a ton of examples!
---

## Navigating the Cookbook

This cookbook is organized into two main categories:

1.  **[Quick Starts](https://github.com/google-gemini/cookbook/tree/main/quickstarts/):**  Step-by-step guides covering both introductory topics ("[Get Started](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb)") and specific API features.
2.  **[Examples](https://github.com/google-gemini/cookbook/tree/main/examples/):** Practical use cases demonstrating how to combine multiple features.

We also showcase **Demos** in separate repositories, illustrating end-to-end applications of the Gemini API.
<br><br>

## What's New?

Here are the recent additions and updates to the Gemini API and the Cookbook: 

* **🍌 Nano-banana Pro:** Use [Gemini's native image generation](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb) capabilities to edit images with high consistency or generate visual stories. Now with thinking, search grounding and 4K output!
* **File Search:** Discover how to ground generations in your own data in a hosted RAG system with the [File Search quickstart](./quickstarts/File_Search.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/File_Search.ipynb). 
* **Grounding with Google Maps:** Get started using factual geographical data from 📍 Google Maps in your apps! See the Google Maps section of the [Grounding Guide](./quickstarts/Grounding.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb).
* **Veo 3.1**: Get started with our video generation model with this [Veo guide](./quickstarts/Get_started_Veo.ipynb), including image-to-videos and video extension! [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb)
* **Gemini Robotics-ER 1.5**: Learn about this new Gemini model specifically for spatial understanding and reasoning for [robotics applications](./quickstarts/gemini-robotics-er.ipynb). [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/gemini-robotics-er.ipynb)
* **Lyria and TTS**: Get started with podcast and music generation with the [TTS](./quickstarts/Get_started_TTS.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb) and [Lyria RealTime](./quickstarts/Get_started_LyriaRealTime.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LyriaRealTime.ipynb) models.
* **LiveAPI**: Get started with the [multimodal Live API](./quickstarts/Get_started_LiveAPI.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.ipynb) and unlock new interactivity with Gemini. 
* **Recently Added Guides:**
  * [Grounding](./quickstarts/Grounding.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb): Discover different ways to ground Gemini's answer using different tools, from Google Search to Youtube and URLs and the new [**Maps grounding**](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb#maps_grounding) tool. 
  * [Batch API](./quickstarts/Batch_mode.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Batch_mode.ipynb): Use Batch API to send large volume of non-time-sensitive requests to the model and get up to 90% discount. 
  * [Logs and datasets](./examples/Datasets.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Datasets.ipynb): Process and evaluate your collected logs using the Batch API.
  
<br><br>

## 1. Quick Starts

The [quickstarts section](https://github.com/google-gemini/cookbook/tree/main/quickstarts/) contains step-by-step tutorials to get you started with Gemini and learn about its specific features.

**To begin, you'll need:**

1.  A Google account.
2.  An API key (create one in [Google AI Studio](https://aistudio.google.com/app/apikey)).
<br><br>

We recommend starting with the following:

*   [Authentication](./quickstarts/Authentication.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb): Set up your API key for access.
*   [**Get started**](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb): Get started with Gemini models and the Gemini API, covering basic prompting and multimodal input.
<br><br>

Then, explore the other quickstarts tutorials to learn about individual features:
*  [Get started with Live API](./quickstarts/Get_started_LiveAPI.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.ipynb): Get started with the live API with this comprehensive overview of its capabilities
*  [Get started with Veo](./quickstarts/Get_started_Veo.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb): Get started with our video generation capabilities 
*  [Get started with Imagen](./quickstarts/Get_started_imagen.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_imagen.ipynb) and [Native image generation](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb): Get started with our image generation capabilities 
*  [Grounding](./quickstarts/Grounding.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb): use Google Search for grounded responses
*  [Code execution](./quickstarts/Code_Execution.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb): Generate and run Python code to solve complex tasks and even output graphs
*  And [many more](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)
<br><br>

## 2. Examples (Practical Use Cases)

These examples demonstrate how to combine multiple Gemini API features or 3rd-party tools to build more complex applications.
*  [Browser as a tool](./examples/Browser_as_a_tool.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Browser_as_a_tool.ipynb): Use a web browser for live and internal (intranet) web interactions
*  [Illustrate a book](./examples/Book_illustration.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb): Use Gemini to create illustration for an open-source book
*  [Animated Story Generation](./examples/Animated_Story_Video_Generation_gemini.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Animated_Story_Video_Generation_gemini.ipynb): Create animated videos by combining Gemini's story generation, Imagen, and audio synthesis
*  [Plotting and mapping Live](./examples/LiveAPI_plotting_and_mapping.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/LiveAPI_plotting_and_mapping.ipynb): Mix *Live API* and *Code execution* to solve complex tasks live
*  [3D Spatial understanding](./examples/Spatial_understanding_3d.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Spatial_understanding_3d.ipynb): Use Gemini *3D spatial* abilities to understand 3D scenes
*  [Gradio and live API](./examples/gradio_audio.py): Use gradio to deploy your own instance of the *Live API*
*  And [many many more](https://github.com/google-gemini/cookbook/tree/main/examples/)
<br><br>

## 3. Demos (End-to-End Applications)

These fully functional, end-to-end applications showcase the power of Gemini in real-world scenarios. 

*   [Gemini CLI](https://github.com/google-gemini/gemini-cli): Open-source AI agent that brings the power of Gemini directly into your terminal
*   [Gemini API quickstart](https://github.com/google-gemini/gemini-api-quickstart): Python Flask App running with the Google AI Gemini API, designed to get you started building with Gemini's multi-modal capabilities
*   [Multimodal Live API Web Console](https://github.com/google-gemini/multimodal-live-api-web-console): React-based starter app for using the Multimodal Live API over a websocket
*   [Fullstack Langgraph Quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart): A fullstack application using a React frontend and a LangGraph-powered backend agent
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




