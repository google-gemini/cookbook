# 欢迎来到 Gemini API Cookbook

这本 Cookbook 为使用 Gemini API 提供了一个结构化的学习路径，重点是实践教程和实际示例。

**如需完整的 API 文档，请访问 [ai.google.dev](https://ai.google.dev/gemini-api/docs)。**
<br><br>

## 浏览 Cookbook

这本 Cookbook 分为两个主要类别：

1.  **[快速入门](https://github.com/google-gemini/cookbook/tree/main/quickstarts/):**  循序渐进的指南，涵盖入门主题（“[开始使用](./quickstarts/Get_started.ipynb)”）和特定的 API 功能。
2.  **[示例](https://github.com/google-gemini/cookbook/tree/main/examples/):**  演示如何组合多个功能的实际用例。

我们还在单独的存储库中展示了 **演示**，用于说明 Gemini API 的端到端应用程序。
<br><br>

## 最新内容

以下是 Gemini API 和 Cookbook 的最新添加和更新：

* **Gemini 2.5 模型：** 探索最新的 Gemini 2.5 模型（Flash 和 Pro）的功能！请参阅[入门指南](./quickstarts/Get_started.ipynb)和[思维指南](./quickstarts/Get_started_thinking.ipynb)，它们都将是思维模型。
* **Imagen 和 Veo**：通过这个全新的 [Veo 指南](./quickstarts/Get_started_Veo.ipynb) 和 [Imagen 指南](./quickstarts/Get_started_imagen.ipynb) 开始使用我们的媒体生成模型！
* **Lyria 和 TTS**：通过 [TTS](./quickstarts/Get_started_TTS.ipynb) 和 [Lyria RealTime](./quickstarts/Get_started_LyriaRealTime.ipynb) 模型开始播客和音乐生成。
* **LiveAPI**：通过[多模式 Live API](./quickstarts/Get_started_LiveAPI.ipynb) 开始使用，并利用 Gemini 解锁新的交互性。
* **最近添加的指南：**
  * [浏览器即工具](./examples/Browser_as_a_tool.ipynb)：使用 Web 浏览器进行实时和内部（内联网）Web 交互
  * [Grounding](./quickstarts/Grounding.ipynb)：探索使用不同工具（从 Google 搜索到 Youtube 以及新的 URL 上下文工具）来支持 Gemini 回答的不同方法。

<br><br>

## 1. 快速入门

[快速入门部分](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)包含循序渐进的教程，可帮助您开始使用 Gemini 并了解其特定功能。

**首先，您需要：**

1.  一个 Google 帐户。
2.  一个 API 密钥（在 [Google AI Studio](https://aistudio.google.com/app/apikey) 中创建一个）。
<br><br>

我们建议从以下内容开始：

*   [身份验证](./quickstarts/Authentication.ipynb)：设置您的 API 密钥以供访问。
*   [**开始使用**](./quickstarts/Get_started.ipynb)：开始使用 Gemini 模型和 Gemini API，涵盖基本提示和多模式输入。
<br><br>

然后，浏览其他快速入门教程以了解各个功能：
*  [Live API 入门](./quickstarts/Get_started_LiveAPI.ipynb)：通过这份对其功能进行全面概述的指南，开始使用 Live API
*  [Veo 入门](./quickstarts/Get_started_Veo.ipynb)：开始使用我们的视频生成功能
*  [Imagen 入门](./quickstarts/Get_started_imagen.ipynb) 和 [Image-out](./quickstarts/Image_out.ipynb)：开始使用我们的图像生成功能
*  [Grounding](./quickstarts/Search_Grounding.ipynb)：使用 Google 搜索获取有根据的回复
*  [代码执行](./quickstarts/Code_Execution.ipynb)：生成并运行 Python 代码以解决复杂任务，甚至输出图形
*  以及[更多](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)
<br><br>

## 2. 示例（实际用例）

这些示例演示了如何组合多个 Gemini API 功能或第三方工具来构建更复杂的应用程序。
*  [为书籍配图](./examples/Book_illustration.ipynb)：使用 Gemini 和 Imagen 为一本开源书籍创作插图
*  [动画故事生成](./examples/Animated_Story_Video_Generation_gemini.ipynb)：通过结合 Gemini 的故事生成、Imagen 和音频合成来创建动画视频
*  [实时绘图和映射](./examples/LiveAPI_plotting_and_mapping.ipynb)：混合 *Live API* 和 *代码执行* 以实时解决复杂任务
*  [3D 空间理解](./examples/Spatial_understanding_3d.ipynb)：使用 Gemini 的 *3D 空间* 能力来理解 3D 场景
*  [Gradio 和 Live API](./examples/gradio_audio.py)：使用 Gradio 部署您自己的 *Live API* 实例
*  以及[更多更多](https://github.com/google-gemini/cookbook/tree/main/examples/)
<br><br>

## 3. 演示（端到端应用程序）

这些功能齐全的端到端应用程序展示了 Gemini 在实际场景中的强大功能。

*   [Gemini API 快速入门](https://github.com/google-gemini/gemini-api-quickstart)：一个使用 Google AI Gemini API 运行的 Python Flask 应用程序，旨在帮助您开始使用 Gemini 的多模式功能进行构建
*   [多模式 Live API Web 控制台](https://github.com/google-gemini/multimodal-live-api-web-console)：一个基于 React 的入门应用程序，用于通过 Websocket 使用多模式 Live API
*   [Google AI Studio 入门小部件](https://github.com/google-gemini/starter-applets)：一组小型应用程序，演示了如何使用 Gemini 创建交互式体验
<br><br>


## 官方 SDK

Gemini API 是一个 REST API。您可以直接使用 `curl` 等工具调用它（请参阅 [REST 示例](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest/) 或出色的 [Postman 工作区](https://www.postman.com/ai-on-postman/google-gemini-apis/overview)），或使用我们的官方 SDK 之一：
* [Python](https://github.com/googleapis/python-genai)
* [Go](https://github.com/google/generative-ai-go)
* [Node.js](https://github.com/google/generative-ai-js)
* [Dart (Flutter)](https://github.com/google/generative-ai-dart)
* [Android](https://github.com/google/generative-ai-android)
* [Swift](https://github.com/google/generative-ai-swift)
<br><br>


## 重要提示：迁移

对于 Gemini 2，我们提供了一个[新的 SDK](https://github.com/googleapis/python-genai)
(<code>[google-genai](https://pypi.org/project/google-genai/)</code>,
<code>v1.0</code>)。更新后的 SDK 与所有 Gemini API
模型和功能完全兼容，包括最近添加的功能，例如
[Live API](https://aistudio.google.com/live)（音频 + 视频流）、
改进的工具使用（
[代码执行](https://ai.google.dev/gemini-api/docs/code-execution?lang=python)、
[函数调用](https://ai.google.dev/gemini-api/docs/function-calling/tutorial?lang=python)和集成的
[Google 搜索 Grounding](https://ai.google.dev/gemini-api/docs/grounding?lang=python)）
以及媒体生成（[Imagen](https://ai.google.dev/gemini-api/docs/imagen) 和 [Veo](https://ai.google.dev/gemini-api/docs/video)）。
此 SDK 允许您通过
[Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.0-flash-exp) 或
[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/gemini-v2) 连接到 Gemini API。

<code>[google-generativeai](https://pypi.org/project/google-generativeai)</code>
软件包将继续支持原始的 Gemini 模型。
它*也*可以与 Gemini 2 模型一起使用，但功能集有限。
所有新功能都将在新的 Google GenAI SDK 中开发。

有关详细信息，请参阅[迁移指南](https://ai.google.dev/gemini-api/docs/migrate)。
<br><br>

## 获取帮助

在 [Google AI 开发者论坛](https://discuss.ai.google.dev/)上提问。

## Google Cloud Vertex AI 上的 Gemini API

对于企业开发人员，Gemini API 也可在 Google Cloud Vertex AI 上使用。有关示例，请参阅[此存储库](https://github.com/GoogleCloudPlatform/generative-ai)。

## 贡献

欢迎贡献！有关详细信息，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

感谢您使用 Gemini API 进行开发！我们很高兴看到您的创作。
