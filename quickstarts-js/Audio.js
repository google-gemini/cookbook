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
# Gemini API: Audio Quickstart
This notebook provides an example of how to prompt Gemini Flash using an audio file. In this case, you'll use a [sound recording](https://www.jfklibrary.org/asset-viewer/archives/jfkwha-006) of President John F. Kennedyâ€™s 1961 State of the Union address.
*/

/* Markdown (render)
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
// [CODE ENDS]

/* Markdown (render)
### Choose a model

Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Get_started_thinking.ipynb) for more details and in particular learn how to switch the thinking off).

For more information about all Gemini models, check the [documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for extended information on each of them.
*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash" // "gemini-2.5-flash-lite", "gemini-2.5-flash""gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview"
// [CODE ENDS]

/* Markdown (render)
### Upload an audio file with the File API

To use an audio file in your prompt, you must first upload it using the [File API](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/File_API.ipynb).

*/

// [CODE STARTS]
AUDIO_URL = "https://storage.googleapis.com/generativeai-downloads/data/State_of_the_Union_Address_30_January_1961.mp3";
audioBlob = await fetch(AUDIO_URL).then(res => res.blob());
audioMime = audioBlob.type || "audio/mpeg";

audioFile = await ai.files.upload({
  file: audioBlob,
  config: { mimeType: audioMime },
});

// [CODE ENDS]

/* Markdown (render)
## Use the file in your prompt
*/

// [CODE STARTS]
audioResponse = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        { fileData: { fileUri: audioFile.uri, mimeType: audioMime } },
        { text: "Listen carefully to the following audio file. Provide a brief summary." }
    ],
});

console.log(audioResponse.text);
// [CODE ENDS]

/* Output Sample

In his State of the Union address on January 30, 1961, President John F. Kennedy presented a somber yet determined assessment of the nation&#x27;s domestic and international challenges.

Domestically, he highlighted a struggling economy marked by recession, high unemployment, stagnant growth, falling farm income, and rising bankruptcies. He also pointed to critical social issues like substandard housing, overcrowded schools, and inadequate healthcare for the aged.

Internationally, Kennedy emphasized the severity of Cold War threats, citing communist pressures in Asia (Laos), civil unrest in Africa (Congo), and the presence of a communist base in Cuba. He also noted the weakening unity within NATO and the ambition for world domination held by the Soviet Union and China. While acknowledging a significant balance of payments deficit and gold outflow, he affirmed the dollar&#x27;s underlying strength and pledged no devaluation.

To address these issues, Kennedy outlined a comprehensive program:
1.  **Economic Revival:** Proposing measures to boost employment, stimulate housing, increase the minimum wage, and provide tax incentives for investment, aiming to showcase the strength of a free economy.
2.  **Military Strengthening:** Ordering a full reappraisal of defense strategy, including increased airlift, accelerated Polaris submarine construction, and improved missile programs, to ensure an &quot;invulnerable&quot; and &quot;futilizing&quot; deterrent.
3.  **Enhanced Foreign Aid &amp; Development:** Calling for a new, more effective economic assistance program, including a $500 million &quot;Alliance for Progress&quot; for Latin America, and expanding the Food for Peace initiative.
4.  **Global Cooperation:** Proposing the formation of a National Peace Corps and inviting the Soviet Union to cooperate on scientific endeavors like weather prediction, satellite communications, and space exploration, seeking to leverage science for peace.
5.  **Strengthening Diplomacy:** Emphasizing arms control as a central goal, and bolstering support for the United Nations as a critical instrument for world peace.

Kennedy acknowledged that the path ahead would be difficult, with likely further setbacks before improvement. He called for national unity, candor, and a renewed sense of public service, stating that rank would be determined by the &quot;size of the job he does.&quot; He concluded with a call for unwavering dedication, recognizing that the hopes of all mankind rested on America&#x27;s ability to face these challenges with pride and perseverance.

*/

/* Markdown (render)
## Inline Audio
For small requests you can inline the audio data into the request, like you can with images.
First slice a small part from the audio blob.
*/

// [CODE STARTS]
slicedBlob = audioBlob.slice(0, 160 * 1024); // ~10,000 ms audio slice for 128 kbps audio file

slicedBase64 = await new Promise((resolve) => {
  const reader = new FileReader();
  reader.onloadend = () => resolve(reader.result.split(',')[1]);
  reader.readAsDataURL(slicedBlob);
});
// [CODE ENDS]

/* Markdown (render)
Add it to the list of parts in the prompt:
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    "Describe this audio clip",
    {
      inlineData: {
        data: slicedBase64,
        mimeType: "audio/mpeg"
      }
    }
  ]
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

This audio clip features a **male voice speaking clearly and formally**, like an announcer or orator. The content of his speech refers to &quot;The President&#x27;s State of the Union address to a joint session of the Congress from the rostrum of the House of Representatives, Washington.&quot;

The clip begins with a **distinct mechanical click or thud sound**, possibly indicating a microphone being engaged or adjusted. Throughout the entire speech, there is a **consistent, low hum or electrical buzzing sound** present in the background, which might suggest an older recording, broadcast equipment, or ambient noise from the venue. The speech concludes, and the background hum continues briefly before the clip ends.

*/

/* Markdown (render)
Note the following about providing audio as inline data:

- The maximum request size is 20 MB, which includes text prompts, system instructions, and files provided inline. If your file's size will make the total request size exceed 20 MB, then [use the File API](https://ai.google.dev/gemini-api/docs/audio#upload-audio) to upload files.
- If you're using an audio sample multiple times, it is more efficient to [use the File API](https://ai.google.dev/gemini-api/docs/audio#upload-audio).

*/

/* Markdown (render)
### Refer to timestamps in the audio file
A prompt can specify timestamps of the form `MM:SS` to refer to particular sections in an audio file. For example: 
`prompt = "Generate a transcript of the speech."`
*/

/* Markdown (render)
### Refer to timestamps in the audio file
A prompt can specify timestamps of the form `MM:SS` to refer to particular sections in an audio file. For example:
*/

// [CODE STARTS]
prompt = "Provide a transcript of the speech between the timestamps 02:30 and 03:29."

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        prompt,
        { fileData: { fileUri: audioFile.uri, mimeType: audioMime } },
    ],
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

I speak today in an hour of national peril and national opportunity. Before my term has ended, we shall have to test anew whether a nation organized and governed, such as ours, can endure. The outcome is by no means certain. The answers are by no means clear. All of us together, this administration, this Congress, this nation, must forge those answers. But today were I to offer after little more than a week in office, detailed legislation to remedy every national ill, the Congress would rightly wonder whether the desire for speed had replaced the duty of responsibility. My remarks therefore will be limited, but they will also be candid. To state the facts frankly is not to despair the future, nor indict the past.

*/

/* Markdown (render)
## Use a Youtube video
*/

// [CODE STARTS]
youtubeUrl = "https://www.youtube.com/watch?v=RDOMKIw1aF4";

prompt = `
  Analyze the following YouTube video content. Provide a concise summary covering:

  1. **Main Thesis/Claim:** What is the central point the creator is making?
  2. **Key Topics:** List the main subjects discussed, referencing specific examples or technologies mentioned (e.g., AI models, programming languages, projects).
  3. **Call to Action:** Identify any explicit requests made to the viewer.
  4. **Summary:** Provide a concise summary of the video content.

  Use the provided title, chapter timestamps/descriptions, and description text for your analysis.
`;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { text: prompt },
    { fileData: { fileUri: youtubeUrl } }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Here&#x27;s an analysis of the YouTube video content:

---

**1. Main Thesis/Claim:**
Google&#x27;s Gemini 2.5 Pro Experimental is the best coding AI the creator has ever used, demonstrating exceptional capabilities in logical code generation and particularly in code refactoring, despite some current limitations in accurately interpreting and building complex user interfaces from visual inputs.

**2. Key Topics:**

*   **Overall AI Model Evaluation:** The video benchmarks Gemini 2.5 Pro Experimental against other leading AI models (OpenAI GPT-3 mini, GPT-4.5, Claude 3.7 Sonnet, Grok 3 Beta, DeepSeek R1) across various domains including Reasoning &amp; Knowledge, Science, Mathematics, Code Generation, Code Editing, Agentic Coding, Factuality, Visual Reasoning, Image Understanding, Long Context, and Multilingual Performance. Gemini consistently performs well, often leading or being competitive.
*   **Code Generation Projects:**
    *   **Ultimate Tic-Tac-Toe (Java Swing):** Successfully &quot;one-shotted&quot; (generated a complete, functional game in a single prompt) demonstrating strong multi-file Java application creation.
    *   **Kitten Cannon Clone (p5.js):** Required three prompts (&quot;three-shotted&quot;) to correct initial errors (e.g., `TypeError: Cannot set properties of undefined`, `TypeError: sketch.sign is not a function`), showcasing the AI&#x27;s effective debugging capabilities through iterative feedback.
    *   **Landing Page Build (Vite, React, Tailwind CSS from Mockup):** Performed poorly in accurately recreating a landing page based on an image mockup, struggling with visual interpretation and requiring significant manual setup.
    *   **X (Twitter) Website UI Recreation (Single HTML file):** Achieved a decent static visual representation of the Twitter/X desktop UI, although without functionality, reinforcing that front-end visual creation from prompts is still developing.
*   **Code Refactoring:** Showcased impressive ability to refactor Rust code by replacing traditional `for` loops with more idiomatic `iter()` methods, including complex logic for conditions and data processing, which the creator notes was superior to other models.
*   **Knowledge and Currency:** Gemini 2.5 Pro&#x27;s training data is highly current (up to March 2025). It successfully leveraged &quot;Grounding with Google Search&quot; to provide the most up-to-date version of React.js.
*   **Developer Workflow:** The video highlights the potential for seamless integration of AI into developer workflows, especially for tasks like debugging and refactoring, though manual steps (like copying code into appropriate files) are still present.

**3. Call to Action:**
The creator explicitly asks viewers who have used Gemini 2.5 Pro Experimental (for coding or other tasks) to **leave their thoughts/experiences in the comments below**. He also implicitly encourages viewers to subscribe, like the video, and enable the notification bell.

**4. Summary:**
The video presents a compelling review of Google&#x27;s new Gemini 2.5 Pro Experimental AI, asserting its superiority as a coding assistant based on the creator&#x27;s extensive testing. Through practical coding challenges, Gemini successfully generated a full Java Swing Ultimate Tic-Tac-Toe game in one go and iteratively debugged a p5.js Kitten Cannon clone. Its most remarkable performance was in refactoring complex Rust code, where it significantly improved efficiency and idiomatic style, outperforming competing models. While the AI struggled with precise front-end UI generation from image mockups, it demonstrated strong foundational knowledge, current information recall (aided by Google Search integration), and robust problem-solving. The creator concludes that Gemini 2.5 Pro is an &quot;awesome&quot; tool for developers, particularly for backend logic and code optimization, and looks forward to further integration into development environments.

*/

/* Markdown (render)
## Count audio tokens

You can count the number of tokens in your audio file using the [countTokens](https://googleapis.github.io/js-genai/release_docs/classes/models.Models.html#counttokens) method.

Audio files have a fixed per second token rate (more details in the dedicated [count token quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Counting_Tokens.ipynb)).
*/

// [CODE STARTS]
countTokensResponse = await ai.models.countTokens({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: audioFile.uri, mimeType: audioMime } },
  ]
});

console.log("Audio file tokens:", countTokensResponse.totalTokens);

// [CODE ENDS]

/* Output Sample

Audio file tokens: 83528

*/

/* Markdown (render)
## Next Steps
### Useful API references:

More details about Gemini API's [vision capabilities](https://ai.google.dev/gemini-api/docs/vision) in the documentation.

If you want to know about the File API, check its [API reference](https://ai.google.dev/api/files) or the [File API](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/File_API.js) quickstart.

### Related examples

Check this example using the audio files to give you more ideas on what the gemini API can do with them:
* Share [Voice memos](https://github.com/google-gemini/cookbook/blob/main/examples/Voice_memos.ipynb) with Gemini API and brainstorm ideas

### Continue your discovery of the Gemini API

Have a look at the [Video_Understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Video_understanding.js) quickstart to learn about another type of media file, then learn more about [prompting with media files](https://ai.google.dev/gemini-api/docs/files#prompt-guide) in the docs, including the supported formats and maximum length for audio files.

*/