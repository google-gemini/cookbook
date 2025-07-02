/* Markdown (render)
# Gemini API: Getting started with Gemini models

The new **[Google Gen AI SDK](https://github.com/googleapis/python-genai)** provides a unified interface to [Gemini models](https://ai.google.dev/gemini-api/docs/models) through both the [Gemini Developer API](https://ai.google.dev/gemini-api/docs) and the Gemini API on [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview). With a few exceptions, code that runs on one platform will run on both. This notebook uses the Developer API.

This notebook will walk you through:
* [Installing and setting-up](Get_started.ipynb#scrollTo=Mfk6YY3G5kqp) the Google GenAI SDK
* [Text](Get_started.ipynb#scrollTo=6TYNPrNvQ8ue) and [multimodal](#scrollTo=yww-vrxmRiIy) prompting
* Counting [tokens](Get_started.ipynb#scrollTo=_9B8pb7tv_Cx)
* Setting system instructions
* Configuring [safety filters](Get_started.ipynb#scrollTo=HTAnYx_bbxPk)
* Initiating a [multi-turn chat](Get_started.ipynb#scrollTo=HTAnYx_bbxPk)
* [Controlling generated output](Get_started.ipynb#scrollTo=nyZMoM6tgnTA)
* Using [function calling](Get_started.ipynb#scrollTo=Rl-y9SZywD0s)
* Generating a [content stream](Get_started.ipynb#scrollTo=uQfLCxfQtPTg) and sending [asynchronous](Get_started.ipynb#scrollTo=plCtEIaHuv96) requests
* Using [file uploads](Get_started.ipynb#scrollTo=enBhuaIk3KYa)
* Using [context caching](Get_started.ipynb#scrollTo=oTgeR3_9wN5J)
* Generating [text embeddings](Get_started.ipynb#scrollTo=sXNCRn8Wx71d)

More details about this new SDK on the [documentation](https://ai.google.dev/gemini-api/docs/sdks).

## Setup
### Install SDK and set-up the client
*/

// [CODE STARTS]
const module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
Modality = module.Modality
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const resp = await ai.models.generateContent({
  model: 'gemini-2.0-flash',
  contents: 'Briefly define machine learning.',
  config: {}
});
console.log(resp.text);
// [CODE ENDS]

/* Output Sample

Machine learning is a type of artificial intelligence that allows computer systems to learn from data without being explicitly programmed. It involves algorithms that can improve their performance on a specific task over time as they are exposed to more data.

*/

/* Markdown (render)
## Count tokens

Tokens are the basic inputs to the Gemini models. You can use the `count_tokens` method to calculate the number of input tokens before sending a request to the Gemini API.
*/

// [CODE STARTS]
const resp2 = await ai.models.countTokens({
    model: 'gemini-2.0-flash',
    contents: 'What is the purpose of life?',
});
console.log(resp2.countTokens);
// [CODE ENDS]

/* Output Sample
8
*/

/* Markdown (render)
## Ground your requests using Google Search

Google Search grounding is particularly useful for queries that require current information or external knowledge. Using Google Search, Gemini can access nearly real-time information and better responses.
*/

// [CODE STARTS]
const resp2 = await ai.models.generateContent({
    model: 'gemini-2.0-flash',
    contents: 'What are some recent breakthroughs in the field of AI?',
    config: {
        tools: [{ googleSearch: {} }],
    },
});
console.log(resp2.text);
console.log(resp2.candidates[0].groundingMetadata.searchEntryPoint.renderedContent)
// [CODE ENDS]

/* Output Sample

It appears that AI is a rapidly evolving field. Here are some recent breakthroughs:

**Generative AI & Large Language Models (LLMs):**
*   **Advancements in LLMs:** There's been remarkable progress, including Meta's Llama 4 which is designed to handle contentious questions more effectively and process various data types.
*   **Gemini 2.0:** Google released this powerful AI model designed for the "agentic era" and integrated it into various products.
*   **Image, video and audio generation:** Improvements have been made to video-to-audio technology, which can generate dynamic soundscapes through natural language text prompts based on on-screen action.
*   **Creative AI tools:** Tools like ImageFX and MusicFX have been introduced to create images and audio clips from text prompts.

**AI Models & Reasoning:**
*   **More capable models:** AI models are becoming faster and more efficient, with advanced reasoning capabilities, useful in fields like science, coding, math, law, and medicine.
*   **AlphaGeometry:** Google DeepMind launched an AI system that can solve complex geometry problems at the level of a human Olympiad gold medalist.
*   **Reasonable reasoning models:** There are increasing improvements in AI's ability to remember more and reason better.

**AI Applications in Various Sectors:**
*   **Engineering:** AI has revolutionized the field of engineering, with platforms using geometric deep learning to deliver simulation results much faster.
*   **Manufacturing:** AI is optimizing production lines and reducing costs.
*   **Healthcare:** AI is being integrated for diagnosing medical conditions.
*   **Scientific discovery:** AI is fueling breakthroughs in scientific research, including biomolecular science.
*   **Materials Science:** AI tools are aiding in the discovery of new materials with potential applications in solar cells, batteries, and superconductors.

**Other Key Trends & Developments:**
*   **Embodied AI and Robotics:**  Funding is increasing for AI-driven humanoid robotics.
*   **AI Agents:** AI-powered agents will do more with greater autonomy to simplify tasks.
*   **Edge Computing:** Edge computing is gaining traction to reduce latency and enhance real-time processing for AI applications.
*   **AI for Sustainability:** AI applications are being used to address environmental challenges.
*   **Quantum Computing:** Quantum computers are enhancing machine learning performance.

*/

/* Markdown (render)
## Generate Images

Gemini can output images directly as part of a conversation:
*/

// [CODE STARTS]
const response = await ai.models.generateContent({
  model: "gemini-2.0-flash-preview-image-generation",
  contents: `A 3D rendered pig with wings and a top hat flying over
             a futuristic sci-fi city filled with greenery.`,
  config: { responseModalities: [Modality.TEXT, Modality.IMAGE] }
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

I will generate a 3D rendering of a whimsical scene: a pink pig with small, feathery wings gracefully soaring above a vibrant, futuristic cityscape. The city below will feature sleek, silver buildings intertwined with lush green vegetation and softly glowing lights. The pig will be wearing a dapper black top hat perched jauntily on its head.


<img src="https://i.ibb.co/4DMSgyf/download.png"/>

*/
