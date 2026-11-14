# 欢迎使用 Gemini API Cookbook

[English](README.md) | [简体中文](README.zh.md)

本精选指南（Cookbook）为使用 Gemini API 提供了结构化的学习路径，专注于实践教程与实用示例。

**如需查阅完整的 API 官方文档，请访问 [ai.google.dev](https://ai.google.dev/gemini-api/docs)。**
<br><br>
**如需查阅 Gemma 快速入门与示例，请查看 [Gemma cookbook](https://github.com/google-gemma/cookbook)。**
<br><br>

---
> **Gemini 4 Hydrogen、Carbon 与 Argon**：从 **[Gemini 4 Hydrogen](https://ai.google.dev/gemini-api/docs/models/gemini-4-hydrogen)**（`gemini-4-hydrogen`）开始探索，它是 Gemini 4 系列中全新默认模型，免费与付费层级均可使用，适用于日常高速编码、多模态工作流以及工具调用智能体（提供最高至 `xhigh` 的四级思维链深度）；同时提供具备极致推理深度的 **[Gemini 4 Carbon](https://ai.google.dev/gemini-api/docs/models/gemini-4-carbon)**（`gemini-4-carbon`）与专为前沿高速推理设计的 **[Gemini 4 Argon](https://ai.google.dev/gemini-api/docs/models/gemini-4-argon)**（`gemini-4-argon`）——全系列均支持统一的 1M 上下文窗口与长达 1M 输出 Token 的长解码。欢迎探索[快速入门（Get Started）](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb) 与[深度思考（Thinking）](./quickstarts/Get_started_thinking.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb#gemini4) 指南，包括[迁移指南（Migration Guide）](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#gemini4migration)。
>
> **Gemini 3.8 Flash**：我们最智能的 Flash 模型，专为长程软件工程、自主智能体以及企业级复杂工作流打造。欢迎从[快速入门](./quickstarts/Get_started.ipynb#choosing_gemini4) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#choosing_gemini4) 与[深度思考](./quickstarts/Get_started_thinking.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb#gemini3) 指南开始上手。
>
> **🎙️ Gemini 3.8 TTS 与自定义音色（Custom Voices）**：通过 [Gemini 3.8 TTS](./quickstarts/Get_started_TTS.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb) 生成富有表现力的单人与多人语音对话，并借助全新[音色设计指南（Voices Guide）](./quickstarts/Get_Started_Voices.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Voices.ipynb) 从文本设计专属音色或通过音频样本复刻声音！
>
> **Omni Flash**：视频编辑领域的 Nano Banana 震撼登场！了解如何通过 Interactions API 调用模型、使用自然语言编辑视频，详情请见[此处指南](./quickstarts/Get_started_Omni.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Omni.ipynb)！
> 
> **🍌 Nano-Banana 2.1**：体验我们最新的图像生成模型：**Nano-Banana 2.1**。在[此处入门](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb#nano-banana-pro) 与 512px、深度思考、搜索与图像事实依据接地（Grounding），并提供海量示例！
> 
> **🎶 Lyria 3.5**：释放您的音乐创作潜能：体验 **Lyria 3.5**。在[此处入门](./quickstarts/Get_started_Lyria.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Lyria.ipynb)，支持完整歌曲生成、图像生音乐（Image-to-Music）及丰富范例！
> 
> **Agents API**：使用全新的 [Antigravity 智能体](./quickstarts/Get_started_managed_agents.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_managed_agents.ipynb) 构建并运行您的自定义智能体！
>
> **Decisions API**：以校准的精准概率与零输出 Token 消耗回答类型化的 Yes/No（`noul`）、多选与评分问题。从 [Decisions API 指南](./quickstarts/Get_started_decisions.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_decisions.ipynb) 开始上手！
>
---

## 浏览 Cookbook 导览

本 Cookbook 组织为两大核心模块：

1.  **[快速入门（Quick Starts）](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)：** 循序渐进的动手指南，涵盖基础入门主题（"[快速入门](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb)"）以及具体 API 功能特性。
2.  **[实用示例（Examples）](https://github.com/google-gemini/cookbook/tree/main/examples/)：** 展示如何组合多种特性的落地实战案例。

我们还在独立的外部代码库中展示了端到端实际应用 **Demos**，展示 Gemini API 在真实业务场景下的强大能力。
<br><br>

## 最新动态（What's New?）

以下是 Gemini API 与 Cookbook 的最新功能特性与更新内容： 
* **Gemini 4 Hydrogen**：Gemini 4 系列中高速且兼具高性价比的日常生产力主力模型——在免费与付费层级均可使用，具备统一的 1M 上下文窗口、支持长达 1M 输出 Token 的长解码续写，以及最高达 `xhigh` 的思考级别（`gemini-4-hydrogen` 现已成为 Cookbook 快速入门的默认模型）。欢迎在[快速入门指南](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb)中开启构建。
* **Decisions API**：借助 `gemini-decision-1` 和 `client.decisions.create`，以校准的概率分布与零输出 Token 成本回答类型化的 是/否（`noul`）、选项选择与数值评分问题。从 [Decisions API 快速入门](./quickstarts/Get_started_decisions.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_decisions.ipynb) 快速上手！ 
* **Gemini 4 Carbon**：我们最强大的前沿推理模型，专为长程自主编码、多模态专业知识工作、科学推理与网络安全防御设计，具备统一的 1M 上下文窗口与长达 1M Token 的长解码能力。在[快速入门指南](./quickstarts/Get_started.ipynb#choosing_gemini4) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#choosing_gemini4) 中了解如何基于 `gemini-4-carbon` 构建应用，以及如何在 Hydrogen、Carbon 和 Argon 之间进行选型。
* **Gemini 4 Argon**：高效的前沿推理模型，专为复杂软件工程、深度数理与科学难题求解、多步自主智能体打造，支持长达 1M 输出 Token 的长解码能力。在[快速入门指南](./quickstarts/Get_started.ipynb#choosing_gemini4) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb#choosing_gemini4) 中了解如何使用 `gemini-4-argon`。
* **🎙️ Gemini 3.8 TTS、声音设计（Voice Design）与声音克隆（Voice Replication）**：通过 [TTS 快速入门](./quickstarts/Get_started_TTS.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb) 生成富有表现力的单人与多发音人语音，并借助[音色指南（声音设计与克隆）](./quickstarts/Get_Started_Voices.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Voices.ipynb) 从文本提示设计专属音色角色或根据参考音频复刻克隆声音。
* **Gemini 3.8 Flash**：我们最智能的 Flash 模型，专为长时程软件工程、自主智能体与企业复杂流程而设计。欢迎在[快速入门指南](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb) 中学习如何使用该模型。
* **Gemini 3.5 Flash-Lite**：3.5 系列中速度最快、成本最低的模型。在高吞吐执行场景下性能优于以往历代 Flash-Lite 模型。在[快速入门指南](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb) 中了解更多。
* **Omni Flash 1.2**：在 [Omni Flash 指南](./quickstarts/Get_started_Omni.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Omni.ipynb) 中体验使用 Gemini Omni Flash 与 Interactions API 进行对话式视频生成与编辑！
* **Agents API**：在受控安全环境中通过 [Antigravity 智能体](./quickstarts/Get_started_managed_agents.ipynb) [![Antigravity agent](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_managed_agents.ipynb) 创建并运行智能体。
* **Webhooks**：通过 [Webhooks 快速入门](./quickstarts/Webhooks.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Webhooks.ipynb) 获取批量任务处理（Batch Jobs）和视频生成等异步操作的实时事件回调通知。
* **推理层级（Inference Tiers）**：在[推理层级指南](./quickstarts/Inference_tiers.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Inference_tiers.ipynb) 中学习如何使用 Priority（优先）和 Flex（弹性）层级，帮助您灵活权衡速度、成本与稳定性。
* **🎶 Lyria 3.5 与 Lyria RealTime**：通过 [Lyria 歌曲生成](./quickstarts/Get_started_Lyria.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Lyria.ipynb) 全面把控音乐结构将创意转化为歌曲，或借助 [Lyria RealTime](./quickstarts/Get_started_LyriaRealTime.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LyriaRealTime.ipynb) 生成交互式实时音乐音频流！
* **🍌 Nano-Banana 2.1 与 Pro：** 利用 [Gemini 原生图像生成](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb) 能力实现高一致性图像编辑或生成视觉故事。体验极致速度的 **Nano-Banana 2** 或 4K 超高清画质的 **Nano-Banana Pro**——二者现均支持深度思考与搜索事实依据接地！
* **文件检索（File Search）：** 通过 [File Search 快速入门](./quickstarts/File_Search.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/File_Search.ipynb) 学习如何在托管式 RAG 检索增强系统中将生成内容锚定在您的专属数据中。
* **Google 地图数据依据接地（Grounding with Google Maps）：** 开始在您的应用中使用来自 📍 Google Maps 的真实地理事实数据！参见[接地指南（Grounding Guide）](./quickstarts/Grounding.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb) 中的 Google Maps 章节。
* **Gemini Robotics-ER 1.5**：了解专为[具身智能与机器人应用](./quickstarts/gemini-robotics-er.ipynb)的空间理解和物理推理定制的新型 Gemini 模型。[![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/gemini-robotics-er.ipynb)
* **Gemini Transcribe**：在 [Gemini Transcribe 指南](./quickstarts/Get_started_transcribe.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_transcribe.ipynb) 中体验对音频文件与实时音频流进行转录，支持词级时间戳、说话人日志分割（Diarization）、自定义词汇表以及智能转写！
* **Live API 与实时翻译（Live Translation）**：借助[多模态 Live API](./quickstarts/Get_started_LiveAPI.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.ipynb) 实现超低延迟语音/视频双向流式传输，或通过 [Live Translation API](./quickstarts/Get_started_LiveTranslate.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveTranslate.ipynb) 实时翻译音频流。
* **近期新增指南：**
  * [音色（声音设计与克隆）](./quickstarts/Get_Started_Voices.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Voices.ipynb)：使用 Gemini 3.8 TTS 从自然语言提示词创建专属音色角色（Voice Design），或从参考音频样本克隆声音（Voice Replication）。
  * [实时扩展思考（Live Extended Thinking）](./quickstarts/Get_started_Live_Thinking.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Live_Thinking.ipynb)：在实时 Live API 会话中启用扩展思考，搭配自然对话填充词提示与非阻塞式后台工具调用。
  * [Gemini Transcribe 音频转写](./quickstarts/Get_started_transcribe.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_transcribe.ipynb)：对音频文件和实时流进行高精转录，支持词级时间戳、说话人分割、自定义专有名词词汇表与智能规范化。
  * [Webhooks 回调](./quickstarts/Webhooks.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Webhooks.ipynb) 与 [推理层级](./quickstarts/Inference_tiers.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Inference_tiers.ipynb)：接收异步作业的实时通知，并通过 Priority（优先）和 Flex（弹性）推理层级兼顾处理速度、成本与可靠性。
  
<br><br>

## 1. 快速入门（Quick Starts）

[快速入门模块](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)包含逐步循序渐进的动手教程，帮助您快速熟悉 Gemini 并掌握各项具体特性。

**开始之前，您需要准备：**

1.  一个 Google 账号。
2.  一枚 API 密钥（可前往 [Google AI Studio](https://aistudio.google.com/app/apikey) 创建获取）。
<br><br>

我们推荐您从以下内容开始：

*   [身份认证（Authentication）](./quickstarts/Authentication.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb)：配置您的 API 密钥以建立访问连接。
*   [**快速入门（Get Started）**](./quickstarts/Get_started.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb)：上手 Gemini 模型与 Gemini API，涵盖基础提示词编写与多模态输入交互。
<br><br>

随后，您可以探索其他专项快速入门教程以掌握各项特定功能：
*  [Decisions API 快速入门](./quickstarts/Get_started_decisions.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_decisions.ipynb)：以校准概率与零输出 Token 成本回答类型化的 是/否、选择与评分问题
*  [语音合成（TTS）入门](./quickstarts/Get_started_TTS.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_TTS.ipynb) 与 [音色设计与克隆（Voices）](./quickstarts/Get_Started_Voices.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Voices.ipynb)：生成高表现力单人与多人语音、根据文本提示词设计专属音色或根据音频样本复刻声音
*  [Live API 快速入门](./quickstarts/Get_started_LiveAPI.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI.ipynb)：全面掌握双向低延迟多模态实时交互功能与应用方式
*  [实时扩展思考（Live Extended Thinking）](./quickstarts/Get_started_Live_Thinking.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Live_Thinking.ipynb)：在实时会话中引入扩展思考能力，包含自然过渡语音与后台并行工具调用
*  [实时翻译（Live Translation）入门](./quickstarts/Get_started_LiveTranslate.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveTranslate.ipynb)：使用 Live Translation API 实时流式翻译音频
*  [Gemini Transcribe 快速入门](./quickstarts/Get_started_transcribe.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_transcribe.ipynb)：对音频文件与实时语音流进行转录，支持词级时间戳、说话人分离与智能排版
*  [Omni Flash 快速入门](./quickstarts/Get_started_Omni.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Omni.ipynb)：通过 Interactions API 进行对话式视频生成与编辑
*  [Veo 视频生成入门](./quickstarts/Get_started_Veo.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Veo.ipynb)：全面了解并使用高质量视频生成能力
*  [Nano-Banana 图像生成入门](./quickstarts/Get_Started_Nano_Banana.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb)：探索最新一代原生图像生成与编辑功能
*  [Lyria 音乐生成入门](./quickstarts/Get_started_Lyria.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_Lyria.ipynb)：利用 Lyria 3.5 与 [Lyria RealTime](./quickstarts/Get_started_LyriaRealTime.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_started_LyriaRealTime.ipynb) 生成完整音乐作品与交互式音频
*  [数据依据接地（Grounding）](./quickstarts/Grounding.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb)：使用 Google 搜索增强事实性回答
*  [代码执行（Code Execution）](./quickstarts/Code_Execution.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb)：自动生成并运行 Python 代码以解决复杂任务甚至直接输出图表
*  以及[更多教程](https://github.com/google-gemini/cookbook/tree/main/quickstarts/)
<br><br>

## 2. 实用示例（Practical Use Cases）

这些实战案例演示了如何结合多种 Gemini API 特性或第三方工具构建更为复杂的完整应用：
*  [浏览器作为工具（Browser as a tool）](./examples/Browser_as_a_tool.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Browser_as_a_tool.ipynb)：使用 Web 浏览器进行实时外网及内部局域网交互
*  [书籍插图绘制（Illustrate a book）](./examples/Book_illustration.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb)：使用 Gemini 为开源书籍自动绘制生成精美配图
*  [动画故事生成（Animated Story Generation）](./examples/Animated_Story_Video_Generation_gemini.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Animated_Story_Video_Generation_gemini.ipynb)：结合 Gemini 故事情节生成、Imagen 图像生成与音频合成制作动画视频
*  [实时绘图与地图标定（Plotting and mapping Live）](./examples/LiveAPI_plotting_and_mapping.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/LiveAPI_plotting_and_mapping.ipynb)：融合 *Live API* 与 *代码执行（Code execution）* 实时解决复杂可视化与计算任务
*  [3D 空间理解（3D Spatial understanding）](./examples/Spatial_understanding_3d.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Spatial_understanding_3d.ipynb)：借助 Gemini 的 *3D 空间理解* 能力深度感知 3D 现实场景
*  [成本预估与健康度监控（Cost Estimation and Health Monitoring）](./examples/Cost_Estimation_And_Health_Monitoring.ipynb) [![Colab](https://storage.googleapis.com/generativeai-downloads/images/colab_icon16.png)](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/Cost_Estimation_And_Health_Monitoring.ipynb)：为 Gemini API 应用构建可观测性层，预估美元成本并全面监控系统健康度
*  [Gradio 与 Live API 集成](./examples/gradio_audio.py)：使用 Gradio 快速部署您自己的 *Live API* 交互式原型
*  以及[更多示例](https://github.com/google-gemini/cookbook/tree/main/examples/)
<br><br>

## 3. 端到端示范应用（Demos）

这些功能完备、开箱即用的端到端应用程序在现实业务场景中充分展现了 Gemini 的卓越潜力：

*   [Gemini CLI](https://github.com/google-gemini/gemini-cli)：直接将 Gemini 的强大功能带入终端的开源 AI 命令行智能体
*   [Gemini API quickstart](https://github.com/google-gemini/gemini-api-quickstart)：基于 Google AI Gemini API 构建的 Python Flask 应用，助您快速基于 Gemini 多模态能力开展构建
*   [Multimodal Live API Web Console](https://github.com/google-gemini/multimodal-live-api-web-console)：基于 React 开发的开箱即用 Web 操控台，通过 WebSocket 使用多模态 Live API
*   [Fullstack Langgraph Quickstart](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart)：采用 React 前端与 LangGraph 驱动后端智能体的全栈应用程序
*   [Google AI Studio Starter Applets](https://github.com/google-gemini/starter-applets)：一组精选小型应用集合，演示如何使用 Gemini 打造趣味丰富的交互体验
<br><br>

## 官方 SDK

Gemini API 本质为标准 REST API。您可以直接使用诸如 `curl` 等工具进行调用（参见 [REST 示例](https://github.com/google-gemini/cookbook/tree/main/quickstarts/rest/) 或优秀的 [Postman 工作区](https://www.postman.com/ai-on-postman/google-gemini-apis/overview)），也可以直接选用我们官方维护的各类语言 SDK：
* [Python](https://github.com/googleapis/python-genai)
* [Go](https://github.com/googleapis/go-genai)
* [Node.js](https://github.com/googleapis/js-genai)
* [Java](https://github.com/googleapis/java-genai)
* [C#](https://github.com/googleapis/dotnet-genai/)
<br><br>

## 获取帮助

欢迎在 [Google AI 开发者论坛（Google AI Developer Forum）](https://discuss.ai.google.dev/) 提问与交流。

## Google Cloud Vertex AI 上的 Gemini API

对于企业级开发者，Gemini API 同样可通过 Google Cloud Vertex AI 进行企业级合规调用。有关示例请参阅[此代码库](https://github.com/GoogleCloudPlatform/generative-ai)。

## 参与贡献

热烈欢迎广大开发者参与贡献！有关详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

感谢您基于 Gemini API 进行开发！我们无比期待见证您的非凡创造。
