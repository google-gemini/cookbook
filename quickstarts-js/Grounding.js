/*
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* Markdown (render)
# Gemini API: Getting started with information grounding for Gemini models

In this notebook you will learn how to use information grounding with [Gemini models](https://ai.google.dev/gemini-api/docs/models/).

Information grounding is the process of connecting these models to specific, verifiable information sources to enhance the accuracy, relevance, and factual correctness of their responses. While LLMs are trained on vast amounts of data, this knowledge can be general, outdated, or lack specific context for particular tasks or domains. Grounding helps to bridge this gap by providing the LLM with access to curated, up-to-date information.

Here you will experiment with:
- Grounding information using Google Search grounding
- Adding YouTube links to gather context information to your prompt
- Using URL context to include website URL as context to your prompt

## Setup
### Install SDK and set-up the client

### API Key Configuration

To ensure security, avoid hardcoding the API key in frontend code. Instead, set it as an environment variable on the server or local machine.

When using the Gemini API client libraries, the key will be automatically detected if set as either `GEMINI_API_KEY` or `GOOGLE_API_KEY`. If both are set, `GOOGLE_API_KEY` takes precedence.

For instructions on setting environment variables across different operating systems, refer to the official documentation: [Set API Key as Environment Variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)

In code, the key can then be accessed as:

```js
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```
*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite-preview-06-17", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
## Use Google Search grounding
Google Search grounding is particularly useful for queries that require current information or external knowledge. Using Google Search, Gemini can access nearly real-time information and better responses.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: 'What was the latest Indian Premier League match and who won?',
    config: { tools: [{ googleSearch: {} }] },
}
);


console.log(`Response:\n ${response.text}`);
console.log(`Search Query: ${response.candidates[0].groundingMetadata.webSearchQueries}`);
console.log(`Search Pages: ${response.candidates[0].groundingMetadata.groundingChunks.map(site => site.web.title).join(', ')}`);
console.log(response.candidates[0].groundingMetadata.searchEntryPoint.renderedContent);
// [CODE ENDS]

/* Output Sample

Response:
 The current date is July 16, 2025. According to the search results, the Indian Premier League (IPL) 2025 season concluded on June 3, 2025.

The latest Indian Premier League match was the final of the IPL 2025 season, which took place on June 3, 2025, at the Narendra Modi Stadium in Ahmedabad.

The Royal Challengers Bengaluru (RCB) won this match, defeating the Punjab Kings (PBKS) by 6 runs to secure their first-ever IPL title.

Search Query: latest Indian Premier League match,who won the last Indian Premier League match

Search Pages: adda247.com, indiatimes.com, thehindu.com, wikipedia.org

[latest Indian Premier League match](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEtr8-P9FxmzE5PrGAEvbYP_eNq3HJlAD3XnEMLdMtwkM7jC-tXubA7eJKskCibcGMYjIY8Xh4tdlYAOFiiXKNP36gb1x7jpl_FhQWHAoQlSJ5MnE1pGFs9BV0WBj28QJWD-q5ef1RdfqUCSdU_-gF48WjwM3ddVU4gyuWn7CS9wL-E72vSApakwXCFBrRIS2ktQ6ixncJGSdH3EeC3dTne7BdXmw==)
[who won the last Indian Premier League match](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHgknhnvHpE4GvFS4cmnl-V67TGhtahXIT_Jd1dpC1Qs01usDCOBEeB7TfFGEd7Gh8oiPu-9xoGrEkNPgV6VcXYnaD5Q7bxazpb5FDWmOicu41zqKUOviMp_6UO7pnmjwjU9d18GvwyJezKQg0lqt4BvWt0YFdORJuEhOVQHp9Xj1Q5XVboxreIp5wDNP1HirA-7QOph6XVf0wOupUHvPry3t3L9E1ySwLnIq2o8Eg=)

*/

/* Markdown (render)
You can see that running the same prompt without search grounding gives you outdated information:
*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: 'What was the latest Indian Premier League match and who won?',
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

The latest Indian Premier League match was the **final of the IPL 2024 season**, played on **May 26, 2024**.

It was between:
*   **Kolkata Knight Riders (KKR)**
*   **Sunrisers Hyderabad (SRH)**

**Kolkata Knight Riders (KKR) won the match by 8 wickets**, securing their third IPL title.

*/

/* Markdown (render)
## Grounding with YouTube links

you can directly include a public YouTube URL in your prompt. The Gemini models will then process the video content to perform tasks like summarization and answering questions about the content.

This capability leverages Gemini's multimodal understanding, allowing it to analyze and interpret video data alongside any text prompts provided.

You do need to explicitly declare the video URL you want the model to process as part of the contents of the request. Here a simple interaction where you ask the model to summarize a YouTube video:
*/

// [CODE STARTS]
ytLink = "https://www.youtube.com/watch?v=XV1kOFo1C8M";

response = await ai.models.generateContent({
    model:MODEL_ID,
    contents:[
        {
            fileData: {
                fileUri: ytLink,
            },
        },
        {
            text: "Summarize this video.",
        },
    ]
}
);

console.log(response.text);
// [CODE ENDS]

/* Output Sample

The video introduces &quot;Gemma Chess,&quot; a new application of Google DeepMind&#x27;s Gemma language model to enhance the game of chess. Ju-yeong Ji from Google DeepMind explains that while traditional chess engines excel at calculating optimal moves (like AlphaZero), Gemma aims to bring a &quot;new dimension&quot; to the game by leveraging its natural language understanding and generation capabilities.

Here&#x27;s how Gemma can be applied:

1.  **Explainer:** Gemma can analyze complex chess games (like the Kasparov vs. Deep Blue match) and translate technical move sequences and engine outputs into plain, understandable text. It can explain *why* certain moves are strategically or tactically significant, detailing the &quot;big ideas&quot; and potential dangers, helping players quickly grasp key takeaways from games.

2.  **Storytellers:** Gemma can generate engaging narratives about chess games. By analyzing the moves, player information, and tournament context, it can write a descriptive story of how a match unfolded, bringing the game to life in a more human and interesting way than just looking at move notation.

3.  **Supporting Chess Learning:** Gemma can act as a personal chess coach. Users can ask questions about chess concepts (e.g., &quot;What is the Sicilian Defense?&quot;), and Gemma will explain them in detail, even tailoring the explanation to the user&#x27;s skill level (beginner, intermediate, advanced) and preferred language (demonstrated with Korean). It can provide insights into strategy, tactics, and historical context, and even suggest areas for improvement.

The video highlights that Gemma&#x27;s strength lies in its ability to understand, explain, and communicate like humans, offering a more intuitive approach to chess learning and analysis by combining the analytical power of traditional chess AI with its own linguistic abilities through function calls. This creates a more accessible, engaging, and personalized chess experience for players of all levels.

*/

/* Markdown (render)
But you can also use the link as the source of truth for your request. In this example, you will first ask how Gemma models can help on chess games:
*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        { text: "How Gemma models can help on chess games?" },
    ]
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

Gemma models, as large language models (LLMs) from Google, are primarily designed for understanding, generating, and processing human language. They are **not** chess engines like Stockfish or AlphaZero, which are built for calculating moves and evaluating positions.

However, Gemma models can be incredibly helpful in chess in several **indirect and supportive ways**, leveraging their language capabilities:

1.  **Learning and Education:**
    *   **Explaining Concepts:** Gemma can explain complex chess concepts (e.g., &quot;what is Zugzwang?&quot;, &quot;explain the concept of pawn structure,&quot; &quot;what is the difference between strategy and tactics?&quot;).
    *   **Opening Explanations:** It can describe various chess openings, their main ideas, common traps, and typical plans (e.g., &quot;Tell me about the King&#x27;s Indian Defense,&quot; &quot;What are the main lines of the Ruy Lopez?&quot;).
    *   **Endgame Principles:** It can explain fundamental endgame principles (e.g., &quot;Explain the concept of opposition in king and pawn endgames,&quot; &quot;How do you checkmate with a king and rook?&quot;).
    *   **Rules and Etiquette:** Answering questions about chess rules, tournament etiquette, or common chess terms.

2.  **Post-Game Analysis (Textual Interpretation):**
    *   **Summarizing Engine Analysis:** If you provide engine analysis (e.g., &quot;Stockfish said my move Qg4 was a blunder, why?&quot;), Gemma could help interpret *why* it was a blunder by explaining the underlying strategic or tactical reasons, translating complex engine output into understandable language.
    *   **Identifying Strategic Themes:** After a game, you could describe certain positions or the flow of the game, and Gemma might help identify recurring strategic themes or common mistakes you made (e.g., &quot;I often lose when I have an isolated queen&#x27;s pawn, what are common plans for and against it?&quot;).
    *   **Explaining Variations:** If you&#x27;re studying a PGN, Gemma could help clarify specific variations or lines, giving you human-readable explanations.

3.  **Opening and Endgame Study Material Generation:**
    *   **Generating Study Questions:** &quot;Give me 5 questions about tactical motifs.&quot;
    *   **Creating Explanations:** &quot;Write a short paragraph explaining how to play with the initiative.&quot;
    *   **Summarizing Opponent Styles (if provided data):** If you feed it a player&#x27;s games (or a summary of their style), Gemma could synthesize a textual description of their preferences, common openings, or tactical tendencies.

4.  **Content Creation:**
    *   **Writing Articles/Blogs:** Generating content for chess blogs, articles, or lesson plans on specific topics.
    *   **Drafting Chess Puzzles (Descriptions):** Creating the *description* or *setup* for chess puzzles, though not necessarily solving them or generating the FEN directly (unless specifically fine-tuned for it).
    *   **Scripting Tutorials:** Helping draft scripts for video tutorials or instructional material.

5.  **Strategic Brainstorming and Conceptual Understanding:**
    *   **Pros and Cons:** Discussing the pros and cons of specific strategic decisions or piece placements (e.g., &quot;What are the advantages and disadvantages of trading queens early?&quot;).
    *   **Hypothetical Scenarios:** Exploring hypothetical &quot;what if&quot; scenarios in a strategic sense, explaining potential outcomes based on common chess principles.

**Limitations to keep in mind:**

*   **Not a Chess Engine:** Gemma cannot calculate moves, evaluate positions numerically, or play chess itself. It doesn&#x27;t &quot;understand&quot; the game in the way a chess engine does.
*   **Relies on Training Data:** Its knowledge is based on the data it was trained on. While vast, it might not have the most up-to-date analysis of very recent games or cutting-edge theoretical lines unless specifically fine-tuned.
*   **Can Hallucinate:** Like all LLMs, Gemma can sometimes generate plausible-sounding but incorrect information. Always cross-reference critical chess advice.
*   **No Real-Time Game Play:** It cannot assist you *during* a live game or provide real-time move suggestions.

In essence, Gemma models act as a powerful **linguistic assistant** for chess players, helping them learn, understand, analyze, and create content related to the game, rather than directly improving their in-game performance through calculation.

*/

/* Markdown (render)
And then you can ask the same question, now having the YouTube video as context to be used by the model:
*/

// [CODE STARTS]
ytLink = "https://www.youtube.com/watch?v=XV1kOFo1C8M";

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            fileData: {
                fileUri: ytLink,
            },
        },
        {
            text: "How Gemma models can help on chess games?",
        },
    ],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Based on the video, Gemma models can bring a new dimension to chess by leveraging their natural language understanding and generation capabilities, rather than directly replacing powerful chess engines like AlphaZero. Here&#x27;s how:

1.  **Explaining and Analyzing Moves:**
    *   **Problem:** Traditional chess engines output technical numbers and complex move sequences that can be hard for humans to understand.
    *   **Gemma&#x27;s Solution:** Gemma can take this technical output, combine it with the actual moves, and turn it into plain, understandable text. It can explain:
        *   Why a specific move is good.
        *   The big strategic ideas behind moves.
        *   Potential dangers or tactical implications.
        *   Summarize complicated parts of the game by picking out key tactical and strategic moments.
    *   **Benefit:** This makes chess analysis much more accessible and insightful, allowing players to quickly grasp important takeaways from games.

2.  **Storytelling about Games:**
    *   **Capability:** Gemma can generate narratives about chess games.
    *   **How:** By analyzing the moves and contextual information (like players, tournament), Gemma can write a descriptive story of how the game unfolded.
    *   **Benefit:** This humanizes the game, bringing it to life in a way that mere move notation cannot, making historical or personal games more engaging and memorable.

3.  **Supporting Chess Learning:**
    *   **Role:** Gemma can act as a &quot;super helpful study buddy&quot; or a &quot;personal chess coach.&quot;
    *   **How:** Users can ask Gemma questions about chess concepts (e.g., &quot;What is the Sicilian Defense?&quot;, &quot;Explain a passed pawn&quot;) in natural language, even in different languages like Korean. Gemma can then:
        *   Provide clear and concise explanations tailored to the user&#x27;s skill level (beginner, intermediate, advanced).
        *   Point out areas where the user might need to improve.
    *   **Benefit:** This offers a readily available, intelligent encyclopedia and coaching tool, making learning complex chess ideas more intuitive and personalized.

**Underlying Mechanism (Function Calling):**
The video demonstrates that Gemma achieves these capabilities by using &quot;function calls&quot; to interact with external chess engines. For instance, to identify the &quot;optimal next move,&quot; Gemma calls a `get_best_move()` function which likely interfaces with a traditional chess engine. Gemma then takes the engine&#x27;s output and uses its linguistic abilities to interpret and explain it in a human-friendly way.

In essence, Gemma enhances the chess experience by bridging the gap between raw computational power and human understanding, making chess more approachable, engaging, and educational.

*/

/* Markdown (render)
## Grounding information using URL context

The URL Context tool empowers Gemini models to directly access and process content from specific web page URLs you provide within your API requests. This is incredibly interesting because it allows your applications to dynamically interact with live web information without needing you to manually pre-process and feed that content to the model.

URL Context is effective because it allows the models to base its responses and analysis directly on the content of the designated web pages. Instead of relying solely on its general training data or broad web searches (which are also valuable grounding tools), URL Context anchors the model's understanding to the specific information present at those URLs.
*/

// [CODE STARTS]
prompt = `
    based on https://ai.google.dev/gemini-api/docs/models, what are the key
    differences between Gemini 1.5, Gemini 2.0 and Gemini 2.5 models?
    Create a markdown table comparing the differences.
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
    config: {
        tools: [{ urlContext: {} }],
    },
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

The browsed page provides details on &quot;Gemini 2.5 Pro&quot;, &quot;Gemini 2.5 Flash&quot;, &quot;Gemini 2.5 Flash-Lite Preview&quot;, &quot;Gemini 2.0 Flash&quot;, &quot;Gemini 2.0 Flash-Lite&quot;, &quot;Gemini 1.5 Flash&quot;, and &quot;Gemini 1.5 Pro&quot;. There is no explicit &quot;Gemini 2.0&quot; or &quot;Gemini 2.5&quot; model as a general category, but rather specific variants like &quot;Flash&quot; and &quot;Pro&quot; under those versions.

I will focus on the most prominent models from each major version mentioned: Gemini 1.5 Pro, Gemini 2.0 Flash (as it seems to be the primary 2.0 model mentioned), and Gemini 2.5 Pro.

Here&#x27;s a comparison table based on the information from the provided URL:

| Feature/Model          | Gemini 1.5 Pro                                          | Gemini 2.0 Flash                                                              | Gemini 2.5 Pro                                                  |
| :--------------------- | :---------------------------------------------------------- | :-------------------------------------------------------------------------------- | :------------------------------------------------------------------ |
| **Description**        | Mid-size multimodal model optimized for reasoning tasks. | Delivers next-gen features, improved capabilities, superior speed, native tool use. | Our most powerful thinking model with maximum response accuracy and state-of-the-art performance. |
| **Input(s)**           | Audio, images, video, text.                             | Audio, images, video, text.                                                   | Audio, images, video, text, and PDF.                          |
| **Output**             | Text.                                                   | Text.                                                                         | Text.                                                           |
| **Input Token Limit**  | 2,097,152.                                              | 1,048,576.                                                                    | 1,048,576.                                                      |
| **Output Token Limit** | 8,192.                                                  | 8,192.                                                                        | 65,536.                                                         |
| **Key Strengths**      | Processes large amounts of data (2 hours video, 19 hours audio, 60k lines code, 2k pages text). | Speed, native tool use, 1M context window.                                    | Complex coding, reasoning, multimodal understanding, analyzing large datasets. |
| **Thinking**           | Not explicitly mentioned as a core feature.                 | Experimental.                                                                 | Supported (on by default).                                      |
| **Live API**           | Not supported.                                          | Supported.                                                                    | Not supported.                                                  |
| **Latest Update**      | September 2024.                                         | February 2025.                                                                | June 2025.                                                      |
| **Knowledge Cutoff**   | Not explicitly mentioned.                                   | August 2024.                                                                  | January 2025.                                                   |
| **Deprecation Date**   | September 2025.                                         | Not explicitly mentioned.                                                         | Not explicitly mentioned.                                           |


*/

/* Markdown (render)
As a reference, you can see how the answer would be without the URL context, using the official models documentation as reference:
*/

// [CODE STARTS]
prompt = `
    what are the key differences between Gemini 1.5, Gemini 2.0 and Gemini 2.5
    models? Create a markdown table comparing the differences.
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

It&#x27;s important to clarify the naming convention for Google&#x27;s Gemini models. As of my last update, Google has not publicly announced distinct models named &quot;Gemini 2.0&quot; or &quot;Gemini 2.5&quot; as major version increments following the pattern you might expect (e.g., 1.0 -&gt; 1.5 -&gt; 2.0).

The primary progression and current publicly available models are:

1.  **Gemini 1.0 (Original):** The initial foundational model suite.
2.  **Gemini 1.5 Pro:** A significant leap forward, particularly known for its massive context window.
3.  **Gemini 1.5 Flash:** A lighter, faster, and more cost-effective version of Gemini 1.5 Pro, optimized for high-volume, lower-latency use cases.

It&#x27;s possible that &quot;Gemini 2.0&quot; or &quot;Gemini 2.5&quot; might refer to internal development names, future anticipated releases, or a misunderstanding of the current public model lineage.

Therefore, I will compare **Gemini 1.0**, **Gemini 1.5 Pro**, and **Gemini 1.5 Flash**, as these are the actual distinct versions available for comparison.

Here&#x27;s a markdown table comparing these models:

## Comparison of Gemini Models (1.0, 1.5 Pro, 1.5 Flash)

| Feature / Model       | Gemini 1.0 (Original)                                  | Gemini 1.5 Pro                                                        | Gemini 1.5 Flash                                                            |
| :-------------------- | :----------------------------------------------------- | :-------------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| **Status/Release**    | Initial public release (Dec 2023)                     | Major upgrade, generally available (Feb 2024 initial preview)         | Faster, more efficient version of 1.5 (Apr 2024)                            |
| **Key Innovation**    | Google&#x27;s first truly multimodal foundation model      | **Massive context window**, native multimodal long-context processing | Optimized for **speed and cost** with large context                        |
| **Context Window**    | ~32K tokens                                           | **1 million tokens (standard)**, up to 2 million tokens (preview)     | 1 million tokens                                                            |
| **Modality**          | Multimodal (text, images, audio, video understanding) | Multimodal (text, images, audio, video understanding)                 | Multimodal (text, images, audio, video understanding)                       |
| **Performance**       | Strong general capabilities, good reasoning, coding    | State-of-the-art long-context reasoning, highly capable, robust       | Very capable, but optimized for speed, so might be slightly less &quot;deep&quot; than Pro for very complex, multi-turn reasoning, but still excellent. |
| **Speed/Cost**        | Standard                                             | Higher cost, focused on high-quality, complex tasks                   | **Significantly faster and cheaper** than 1.5 Pro                         |
| **Use Cases**         | General-purpose assistant, content generation, summarization | Deep code analysis, long document summarization, video processing, large dataset analysis, complex R&amp;D, advanced agents | Building agents, fast real-time applications, large-scale data processing, conversational AI, high-volume use cases, real-time analytics |
| **Availability**      | Gemini Advanced (formerly Bard), Google AI Studio, Vertex AI API | Google AI Studio, Vertex AI API                                       | Google AI Studio, Vertex AI API                                             |

**In Summary:**

*   **Gemini 1.0** was the groundbreaking initial release, establishing multimodal capabilities.
*   **Gemini 1.5 Pro** is the current flagship, defined by its industry-leading massive context window and advanced multimodal understanding. It&#x27;s for high-quality, complex tasks requiring deep analysis.
*   **Gemini 1.5 Flash** is a strategic variant of 1.5 Pro, sacrificing a tiny fraction of the &quot;Pro&quot; model&#x27;s peak reasoning depth for immense gains in speed and cost-efficiency, making it ideal for scalable, real-time applications.

There is no public information about a &quot;Gemini 2.0&quot; or &quot;Gemini 2.5&quot; as of now. The numbering `1.5` indicates a significant upgrade within the `1.x` series, rather than a completely new major version `2.0`.

*/

/* Markdown (render)
As you can see, using the model knowledge only, it does not know about the new Gemini 2.5 models family.
*/

/* Markdown (render)
## Next steps


* For more details about using Google Search grounding, check out the Search Grounding cookbook [Python](https://github.com/google-gemini/cookbook/blob/main/quickstarts//Search_Grounding.ipynb).
* If you are looking for another scenarios using videos, take a look at the Video understanding cookbook [Python](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb).

Also check the other Gemini capabilities that you can find in the Gemini quickstarts [Python](https://github.com/google-gemini/cookbook/tree/main/quickstarts/) | [JS](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/).
*/