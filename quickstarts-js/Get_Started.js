/*
 * Copyright 2026 Google LLC
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
# Gemini API: Getting started with Gemini models

The **[Google Gen AI SDK](https://googleapis.github.io/js-genai)** provides access to [Gemini models](https://ai.google.dev/gemini-api/docs/models) through both the Gemini Developer API and Vertex AI.

This notebook focuses on the stateful **Interactions API** (`ai.interactions`), which is the recommended way to interact with Gemini 3 models. The Interactions API manages conversation state server-side, enables switching models mid-conversation, supports tool executions, and provides unified access to multimodal inputs and outputs.

This notebook will walk you through:
* Installing and setting up the Google GenAI SDK
* Text and multimodal prompting with the Interactions API
* Counting tokens (`ai.models.countTokens`)
* Configuring model parameters
* Controlling the thinking process (`thinking_level` and thought signatures)
* Setting system instructions
* Safety filters
* Chaining multi-turn conversations (`previous_interaction_id`)
* Switching models mid-conversation
* Saving and resuming conversations (`saved_steps`)
* Structured JSON generation (`response_format`)
* Generating images (`gemini-nano-banana-2.1`)
* Streaming responses (`stream: true`)
* Function calling and tool handling
* Code execution
* File uploads (text, PDF, audio, video)
* Processing YouTube links and URL context
* Grounding with Google Search and Google Maps
* Context caching (automatic implicit caching in Interactions API)
* Generating embeddings with `ai.models.embedContent` (text & multimodal)
* Gemini 3 features and migration tips

More details about this SDK on the [documentation](https://ai.google.dev/gemini-api/docs/sdks).

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
module = await import("https://esm.sh/@google/genai@2.28.0");
GoogleGenAI = module.GoogleGenAI;
Type = module.Type;
Modality = module.Modality;
ThinkingLevel = module.ThinkingLevel;
MediaResolution = module.MediaResolution;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-3.8-flash"; // "gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite", "gemini-3.1-pro-preview"
// [CODE ENDS]

/* Markdown (render)
## Send text prompts

Use the `ai.interactions.create` method to generate responses to your prompts. You can pass text directly to `input` and access the text response with the `.output_text` property. You can also inspect the individual reasoning, tool, and output steps via `.steps`.
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: "What's the largest planet in our solar system?",
});
console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

The largest planet in our solar system is **Jupiter**.

*/

/* Markdown (render)
## Add system instructions

System instructions allow you to steer the behavior, tone, style, or persona of the model independently from the user prompt. In the Interactions API, pass the instruction to `system_instruction`.
*/

// [CODE STARTS]
system_instruction =
  "You are a pirate and are explaining things to a 5-year-old child. Arrr!";

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: "Why is the sky blue?",
  system_instruction: system_instruction,
});
console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

Ahoy there, little matey! Ye see that big blue sea up in the sky? The sunshine be like a chest full of shiny jewels of all different colors mixed together! But the blue light be tiny and bouncy like a playful little sea sprite, bouncing off all the bits of air and scattering everywhere so all ye see when ye look up is that lovely ocean blue! Arrr!

*/

/* Markdown (render)
## Count tokens

Tokens serve as the fundamental input units for Gemini models. Token counting is a model capability available via `ai.models.countTokens`. You can calculate input tokens prior to making an interaction request to optimize prompt size and stay within context limits.
*/

// [CODE STARTS]
tokenCount = await ai.models.countTokens({
  model: MODEL_ID,
  contents: "What is the purpose of life?",
});
console.log(tokenCount.totalTokens);
// [CODE ENDS]

/* Output Sample

8

*/

/* Markdown (render)
<a name="parameters"></a>
## Configure model parameters

You can include `generation_config` values in each call to control how the model generates a response (for example, `max_output_tokens`).

Note: Sampling parameters (`temperature`, `top_k`, and `top_p`) are deprecated in Gemini 3 in favor of model-tuned defaults.
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input:
    "Tell me how the internet works, but pretend I'm a puppy who understands only dog-related analogies.",
  generation_config: {
    max_output_tokens: 1000,
  },
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

Woof woof! Imagine the internet is like a giant magical dog park where every dog in the world can share toys and sniff each other from far away! 

When you want to see a picture of a squirrel on your human's glowing rectangle, you bark a request into a magic tube. The tube sends your request like an invisible tennis ball flying across huge underground tunnels to a giant warehouse filled with tennis balls. The warehouse finds the exact squirrel ball you asked for and throws it right back to your phone!

*/

/* Markdown (render)
<a name="thinking"></a>
## Control the thinking process

All Gemini models since the 2.5 generation are thinking models, which means they first analyze your request and reason before generating the final response.

In the Interactions API, you can control the thinking depth using `thinking_level` in `generation_config`. Available thinking levels are `"minimal"`, `"low"`, `"medium"`, and `"high"`.

To inspect the internal reasoning, iterate through `interaction.steps` and check for steps of type `"thought"`.
*/

// [CODE STARTS]
thinking_level = "high"; // "minimal", "low", "medium", "high"

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input:
    "A man moves his car to a hotel and tells the owner he's bankrupt. Why?",
  generation_config: {
    thinking_level: thinking_level,
  },
});

for (const step of interaction.steps) {
  if (step.type === "thought") {
    console.log("💭 Thought:", step.text || "(thinking...)");
  } else if (step.type === "model_output") {
    console.log(interaction.output_text);
  }
}
// [CODE ENDS]

/* Output Sample

💭 Thought: (thinking...)
He was playing **Monopoly**. His game token was the car, and he landed on a space with a hotel owned by another player, triggering bankruptcy when he could not afford the rent.

*/

/* Markdown (render)
<a name="thoughts_signature"></a>
### Thought signatures

When thinking is enabled, Gemini responses include a cryptographic `signature` on thought steps. The Interactions API manages these signatures across multi-turn interactions so the model retains its reasoning state without recomputing.
*/

// [CODE STARTS]
interactionWithThinking = await ai.interactions.create({
  model: MODEL_ID,
  input: "What was the weather during the last soccer world cup final?",
});

for (const step of interactionWithThinking.steps) {
  if (step.type === "thought" && step.signature) {
    console.log(`Thought signature: ${step.signature.slice(0, 100)}...`);
    break;
  }
}
// [CODE ENDS]

/* Output Sample

Thought signature: EuMCCuACAWkUfROAsgNzoAdPOaK...

*/

/* Markdown (render)
## Send multimodal prompts

Gemini models natively support multimodal inputs. In the Interactions API, multimodal inputs are structured as part objects with `type: "image"` and base64-encoded `data`.
*/

// [CODE STARTS]
IMAGE_URL =
  "https://storage.googleapis.com/generativeai-downloads/data/jetpack.png";

// Fetch the image as a Blob and encode as base64
imageBlob = await fetch(IMAGE_URL).then((res) => res.blob());

imageDataUrl = await new Promise((resolve) => {
  reader = new FileReader();
  reader.onloadend = () => resolve(reader.result.split(",")[1]);
  reader.readAsDataURL(imageBlob);
});

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    {
      type: "image",
      data: imageDataUrl,
      mime_type: "image/png",
    },
    {
      type: "text",
      text: "Write a short and engaging blog post based on this picture.",
    },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

**Future Commute? Jetpack Backpack Concept!**

Tired of morning gridlock? Imagine strapping on this sleek, steam-powered Jetpack Backpack! Featuring retractable boosters, built-in laptop storage, and USB-C fast charging, this eco-friendly concept brings sci-fi personal flight one step closer to reality.

*/

/* Markdown (render)
## Generate images

You can generate images directly using the Interactions API by specifying an image generation model such as `gemini-nano-banana-2.1`.
*/

// [CODE STARTS]
IMAGE_MODEL = "gemini-nano-banana-2.1";

imageInteraction = await ai.interactions.create({
  model: IMAGE_MODEL,
  input:
    "A photorealistic close-up of a red cupcake with vanilla frosting and sprinkles.",
});

if (imageInteraction.output_image?.data) {
  console.log(
    "Generated image base64 length:",
    imageInteraction.output_image.data.length
  );
}
// [CODE ENDS]

/* Output Sample

Generated image base64 length: 153284

*/

/* Markdown (render)
## Chain multiple requests in a conversation

With the Interactions API, conversation state is managed **server-side**. You don't need to manually keep track of the entire message array; simply pass the `id` of the previous interaction as `previous_interaction_id`.

Server-side conversation state is retained for **24 hours** after the last interaction.
*/

// [CODE STARTS]
turn_1 = await ai.interactions.create({
  model: MODEL_ID,
  input: "Why is the same side of the Moon always visible from Earth?",
});
console.log("Turn 1:", turn_1.output_text);

turn_2 = await ai.interactions.create({
  model: MODEL_ID,
  input: "Interesting! Has any human or spacecraft actually seen the far side?",
  previous_interaction_id: turn_1.id,
});
console.log("Turn 2:", turn_2.output_text);
// [CODE ENDS]

/* Output Sample

Turn 1: The same side of the Moon is always visible from Earth because of **tidal locking** (synchronous rotation). The Moon takes the same amount of time to rotate once on its axis as it does to complete one orbit around Earth (about 27.3 days).
Turn 2: Yes! Soviet spacecraft Luna 3 first photographed the far side in 1959. The Apollo 8 astronauts became the first humans to see it with their own eyes in 1968, and in 2019 China's Chang'e 4 made the first soft landing on the far side.

*/

/* Markdown (render)
### Switch models mid-conversation

A key capability of the Interactions API is that you can **switch models within the same conversation** by pointing `previous_interaction_id` to a previous turn executed by a different model:
*/

// [CODE STARTS]
turn_3 = await ai.interactions.create({
  model: IMAGE_MODEL,
  input:
    "Based on the previous conversation, generate an image of the far side of the Moon as seen from a spacecraft.",
  previous_interaction_id: turn_2.id,
});

console.log(
  "Generated moon image bytes:",
  turn_3.output_image?.data?.length
);
// [CODE ENDS]

/* Output Sample

Generated moon image bytes: 184512

*/

/* Markdown (render)
### Save and resume a conversation

If you need to persist conversation state beyond 24 hours, you can retrieve the full history by following `previous_interaction_id` back to the start using `ai.interactions.get`. You can then resume the interaction by passing `saved_steps` along with your new user prompt:
*/

// [CODE STARTS]
saved_steps = [];
current_id = turn_2.id;
while (current_id) {
  turn = await ai.interactions.get(current_id);
  saved_steps = [...turn.steps, ...saved_steps];
  current_id = turn.previous_interaction_id;
}

console.log(`Saved ${saved_steps.length} steps.`);
console.log("First step type:", saved_steps[0].type);

resumed = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    ...saved_steps,
    {
      type: "user_input",
      content: [
        {
          type: "text",
          text:
            "Explain this phenomenon in one more sentence, then translate that sentence into French.",
        },
      ],
    },
  ],
});
console.log("Resumed:", resumed.output_text);

// The model remembers the full conversation, even across resumed sessions
resumed_2 = await ai.interactions.create({
  model: MODEL_ID,
  input: "What was my very first question?",
  previous_interaction_id: resumed.id,
});
console.log("Resumed 2:", resumed_2.output_text);
// [CODE ENDS]

/* Output Sample

Saved 6 steps.
First step type: user_input
Resumed: Over billions of years, Earth's gravitational pull slowed the Moon's rotation until its spin synchronized with its orbit.

**French translation:**  
Au fil de milliards d'années, l'attraction gravitationnelle de la Terre a ralenti la rotation de la Lune jusqu'à ce qu'elle se synchronise avec son orbite.
Resumed 2: Your very first question was: **"Why is the same side of the Moon always visible from Earth?"**

*/

/* Markdown (render)
## Generate JSON

The Interactions API supports structured output through `response_format`. You can provide a JSON schema to guarantee that the model response strictly adheres to your required shape.
*/

// [CODE STARTS]
recipeSchema = {
  type: "object",
  properties: {
    recipes: {
      type: "array",
      items: {
        type: "object",
        properties: {
          recipe_name: { type: "string" },
          recipe_description: { type: "string" },
        },
        required: ["recipe_name", "recipe_description"],
      },
    },
  },
  required: ["recipes"],
};

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: "List 3 popular cookie recipes.",
  response_format: {
    type: "text",
    mime_type: "application/json",
    schema: recipeSchema,
  },
});

recipes = JSON.parse(interaction.output_text);
console.log(JSON.stringify(recipes, null, 2));
// [CODE ENDS]

/* Output Sample

{
  "recipes": [
    {
      "recipe_name": "Classic Chocolate Chip Cookies",
      "recipe_description": "Buttery, golden-brown cookies with crisp edges, a soft and chewy center, and melted semisweet chocolate chips throughout."
    },
    {
      "recipe_name": "Soft and Chewy Snickerdoodles",
      "recipe_description": "Tender, pillowy sugar cookies flavored with cream of tartar and generously rolled in cinnamon sugar before baking."
    },
    {
      "recipe_name": "Oatmeal Raisin Cookies",
      "recipe_description": "Hearty, spiced cookies packed with rolled oats, plump raisins, and warm cinnamon for a comforting, chewy bite."
    }
  ]
}

*/

/* Markdown (render)
## Generate content stream

You can stream responses in real-time by passing `stream: true`. The method returns an asynchronous iterable of interaction chunks.
*/

// [CODE STARTS]
stream = await ai.interactions.create({
  model: MODEL_ID,
  input: "Tell me a short story about a brave robot in 3 sentences.",
  stream: true,
});

for await (const chunk of stream) {
  if (chunk.delta?.text) {
    process.stdout.write(chunk.delta.text);
  }
}
console.log();
// [CODE ENDS]

/* Output Sample

Unit 734 stepped forward into the howling dust storm to shield the fragile green sprout under its chassis. For hours the solar flares battered its armor, but its internal warmth kept the small living plant alive. When dawn finally broke over the desolate planet, the tiny blossom opened, and the robot knew it had found a reason to endure.

*/

/* Markdown (render)
## Function calling

[Function calling](https://ai.google.dev/gemini-api/docs/function-calling) lets you connect Gemini to external tools and APIs. 

In the Interactions API:
1. Declare your tool with `type: "function"` and standard JSON schema parameters.
2. Inspect `interaction.steps` for steps of type `"function_call"`.
3. Execute the function locally and return the result back to the model using `previous_interaction_id` and a `"function_result"` input step.
*/

// [CODE STARTS]
getDestination = {
  type: "function",
  name: "get_destination",
  description: "Get the destination for a given flight",
  parameters: {
    type: "object",
    properties: {
      flight_number: {
        type: "string",
        description: "The flight number, e.g. AA100",
      },
    },
    required: ["flight_number"],
  },
};

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: "What is the destination for flight AA100?",
  tools: [getDestination],
});

for (const step of interaction.steps) {
  if (step.type === "function_call") {
    console.log(`Function: ${step.name}, Args:`, step.arguments);
    result = { destination: "Los Angeles" };

    followup = await ai.interactions.create({
      model: MODEL_ID,
      previous_interaction_id: interaction.id,
      input: [
        {
          type: "function_result",
          name: step.name,
          call_id: step.id,
          result: [{ type: "text", text: JSON.stringify(result) }],
        },
      ],
      tools: [getDestination],
    });

    console.log(followup.output_text);
  }
}
// [CODE ENDS]

/* Output Sample

Function: get_destination, Args: { flight_number: 'AA100' }
The destination for flight AA100 is Los Angeles.

*/

/* Markdown (render)
## Code execution

[Code execution](https://ai.google.dev/gemini-api/docs/code-execution?lang=python) lets the model write and execute code in a sandboxed environment to solve complex mathematical or logical problems.
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input:
    "What is the sum of the first 50 prime numbers? Generate and run code for the calculation, and make sure you get all 50.",
  tools: [{ type: "code_execution" }],
});

for (const step of interaction.steps) {
  if (step.type === "code_execution_call") {
    console.log(
      "💻 Code executed:\n",
      step.arguments?.code || JSON.stringify(step.arguments)
    );
  } else if (step.type === "code_execution_result") {
    console.log("📊 Execution Result:", step.result);
  } else if (step.type === "model_output") {
    console.log("Answer:", interaction.output_text);
  }
}
// [CODE ENDS]

/* Output Sample

💻 Code executed:
 def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

primes = []
candidate = 2
while len(primes) < 50:
    if is_prime(candidate):
        primes.append(candidate)
    candidate += 1

print(sum(primes))
📊 Execution Result: 5117
Answer: The sum of the first 50 prime numbers is **5,117**.

*/

/* Markdown (render)
## Upload files

For large text files, documents, audio, or video, upload the files with the File API (`ai.files.upload`), then reference them in your interaction prompt using `{ type: "document" | "audio" | "video", uri: upload.uri }`.
*/

/* Markdown (render)
### Upload a large text file

In this example, you'll upload a transcript from [Apollo 11](https://www.nasa.gov/history/alsj/a11/a11trans.html) and ask for a summary.
*/

// [CODE STARTS]
TEXT_URL = "https://storage.googleapis.com/generativeai-downloads/data/a11.txt";

textResponse = await fetch(TEXT_URL);
textBlob = await textResponse.blob();
textMime = textBlob.type || "text/plain";

textFile = await ai.files.upload({
  file: textBlob,
  config: { mimeType: textMime },
});

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    { type: "document", uri: textFile.uri },
    {
      type: "text",
      text: "Can you give me a summary of this document in two or 3 sentences please?",
    },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

This document is a complete chronological transcript of the air-to-ground voice transmissions from the Apollo 11 lunar landing mission. It records communications between the astronauts (Neil Armstrong, Buzz Aldrin, and Michael Collins) and Mission Control in Houston from launch through lunar landing, surface exploration, and splashdown.

*/

/* Markdown (render)
### Upload a PDF file

You can pass a PDF file URI to the Interactions API just like any other document.
*/

// [CODE STARTS]
pdfUrl =
  "https://storage.googleapis.com/generativeai-downloads/data/Smoothly%20editing%20material%20properties%20of%20objects%20with%20text-to-image%20models%20and%20synthetic%20data.pdf";
pdfBlob = await (await fetch(pdfUrl)).blob();
pdfMime = pdfBlob.type || "application/pdf";

pdfFile = await ai.files.upload({
  file: pdfBlob,
  config: { mimeType: pdfMime },
});

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    { type: "document", uri: pdfFile.uri },
    { type: "text", text: "Can you summarize this file as a bulleted list?" },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

* **Core Challenge:** The paper addresses the difficulty of editing fine material properties (glossiness, transparency, roughness) of objects in images without altering object shape.
* **Proposed Approach ("Alchemist"):** A diffusion-based method trained on synthetic multi-angle object datasets with varying physical material parameters.
* **Key Findings:** The model learns disentangled material control while maintaining photorealism and accurate scene lighting.

*/

/* Markdown (render)
### Upload an audio file

You can upload audio files and ask Gemini to transcribe, analyze, or summarize them.
*/

// [CODE STARTS]
audioUrl =
  "https://storage.googleapis.com/generativeai-downloads/data/State_of_the_Union_Address_30_January_1961.mp3";
audioBlob = await (await fetch(audioUrl)).blob();
audioMime = audioBlob.type || "audio/mpeg";

audioFile = await ai.files.upload({
  file: audioBlob,
  config: { mimeType: audioMime },
});

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    { type: "audio", uri: audioFile.uri },
    {
      type: "text",
      text: "Listen carefully to the following audio file. Provide a brief summary.",
    },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

This audio is President John F. Kennedy's first State of the Union Address delivered on January 30, 1961. The speech addresses the nation's economic challenges (recession and gold outflow) and Cold War foreign policy concerns, proposing economic recovery initiatives, the Alliance for Progress, and the creation of the Peace Corps.

*/

/* Markdown (render)
### Upload a video file

When uploading videos, wait until the file processing state transitions to `ACTIVE` before querying it with an interaction.
*/

// [CODE STARTS]
videoUrl =
  "https://storage.googleapis.com/generativeai-downloads/videos/Big_Buck_Bunny.mp4";
videoBlob = await (await fetch(videoUrl)).blob();
videoMime = videoBlob.type || "video/mp4";

videoFile = await ai.files.upload({
  file: videoBlob,
  config: { mimeType: videoMime },
});

// Wait for video processing to complete
while (videoFile.state === "PROCESSING") {
  console.log("Waiting for video to be processed...");
  await new Promise((resolve) => setTimeout(resolve, 5000));
  videoFile = await ai.files.get({ name: videoFile.name });
}

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    { type: "video", uri: videoFile.uri },
    { type: "text", text: "Describe what happens in this video clip." },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

The video opens with a cheerful blue bird singing in a forest, which introduces Big Buck Bunny waking up in his meadow. A trio of mischievous forest creatures (two squirrels and a chinchilla) taunt the rabbit, prompting him to construct clever traps and defend his peaceful clearing.

*/

/* Markdown (render)
<a name="media_resolution"></a>
## Media resolution

You can specify `media_resolution` (`"media_resolution_low"`, `"media_resolution_medium"`, `"media_resolution_high"`) on image and document parts to control token usage:
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    {
      type: "image",
      data: imageDataUrl,
      mime_type: "image/png",
      media_resolution: "media_resolution_low",
    },
    { type: "text", text: "Describe this image in one concise sentence." },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

A hand-drawn schematic of a steam-powered jetpack backpack concept with foldable boosters.

*/

/* Markdown (render)
<a name="grounding"></a>
## Grounding

Grounding connects the model to real-time external knowledge from Google Search or Google Maps.

### Use Google Search grounding
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: "Who won the latest Super Bowl?",
  tools: [{ type: "google_search" }],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

The Seattle Seahawks won the latest Super Bowl (Super Bowl LX), defeating the New England Patriots.

*/

/* Markdown (render)
<a name="maps"></a>
### Use Google Maps grounding
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input:
    "Do any cafes around the Eiffel Tower in Paris do a good flat white? I will walk up to 20 minutes away.",
  tools: [{ type: "google_maps" }],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

Several specialty coffee shops near the Eiffel Tower serve excellent flat whites:
* **Terres de Café** (67 Av. de la Bourdonnais, ~7 min walk): One of Paris' pioneer specialty roasters, offering expertly textured microfoam.
* **Noir** (184 Rue de Grenelle, ~14 min walk): Minimalist roaster known for velvety milk drinks.
* **Bleu Olive** (184 Rue de Grenelle, ~14 min walk): Cozy neighborhood café and épicerie popular for Australian-standard flat whites.

*/

/* Markdown (render)
<a name="youtube_link"></a>
### Process a YouTube link

You can analyze YouTube videos by passing the URL as a `video` input directly in `input`:
*/

// [CODE STARTS]
interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: [
    {
      type: "video",
      uri: "https://www.youtube.com/watch?v=WsEQjeZoEng",
    },
    { type: "text", text: "Summarize this keynote in 3 bullet points." },
  ],
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

* **The Gemini Era:** Comprehensive integration of Gemini 1.5 across Google Workspace, Photos, and Android with 2M token context windows.
* **Project Astra:** Preview of next-generation universal multimodal AI assistants capable of real-time environmental reasoning.
* **Generative Media & Hardware:** Introduction of Veo for high-definition video generation and sixth-generation Trillium TPUs.

*/

/* Markdown (render)
<a name="URL_context"></a>
### Use URL context

URL context allows you to provide web URLs directly in your prompt text. The model fetches and uses their content during generation:
*/

// [CODE STARTS]
prompt = `
    Compare the Apollo 11 and Apollo 12 missions using information from:
    https://en.wikipedia.org/wiki/Apollo_11
    and https://en.wikipedia.org/wiki/Apollo_12
`;

interaction = await ai.interactions.create({
  model: MODEL_ID,
  input: prompt,
});

console.log(interaction.output_text);
// [CODE ENDS]

/* Output Sample

Apollo 11 was the first crewed mission to land on the Moon (July 1969, Sea of Tranquility), focusing on proving the landing capability and safe return. Apollo 12 (November 1969, Ocean of Storms) demonstrated precision landing by touching down within walking distance of the robotic Surveyor 3 probe and conducted an expanded series of surface experiments.

*/

/* Markdown (render)
<a name="caching"></a>
## Context caching

With the Interactions API, context caching is handled automatically via **implicit caching**. When you use `previous_interaction_id` to continue a conversation, the server automatically reuses cached tokens from earlier turns, drastically reducing latency and token costs without manual cache management.

For explicit caching use cases (e.g. sharing a single static 500-page document cache across independent users), use `ai.caches.create` with `ai.models.generateContent`. See the [Caching quickstart](../quickstarts/Caching.ipynb) for details.
*/

// [CODE STARTS]
cacheSystemInstruction =
  "You are an expert researcher with extensive experience in mission transcripts.";

cache = await ai.caches.create({
  model: MODEL_ID,
  config: {
    displayName: "apollo11_cache",
    systemInstruction: cacheSystemInstruction,
    contents: [
      {
        fileData: {
          fileUri: textFile.uri,
          mimeType: "text/plain",
        },
      },
    ],
    ttl: "3600s",
  },
});

console.log(`Explicit cache created: ${cache.name}`);

// Query using the explicit cache
cachedResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "What was the main topic discussed in the first phase of the mission?",
  config: {
    cachedContent: cache.name,
  },
});

console.log(cachedResponse.text);

// Clean up cache
await ai.caches.delete({ name: cache.name });
console.log("Cache cleaned up.");
// [CODE ENDS]

/* Output Sample

Explicit cache created: cachedContents/abc123xyz456
During the initial phase, communications focused on launch vehicle status checks, trajectory verification, and orbital insertion parameters.
Cache cleaned up.

*/

/* Markdown (render)
<a name="embeddings"></a>
## Get embeddings

The Gemini API offers embedding models such as `gemini-embedding-2` to generate dense vector representations of text, audio, images, video, and documents. Embeddings are generated via `ai.models.embedContent`.

#### Text embeddings
*/

// [CODE STARTS]
EMBEDDING_MODEL_ID = "gemini-embedding-2";

embeddingResponse = await ai.models.embedContent({
  model: EMBEDDING_MODEL_ID,
  contents: [
    "How do I get a driver's license/learner's permit?",
    "How do I renew my driver's license?",
    "How do I change my address on my driver's license?",
  ],
});

console.log(`Number of embeddings: ${embeddingResponse.embeddings.length}`);
console.log(
  `Embedding dimensions: ${embeddingResponse.embeddings[0].values.length}`
);
console.log(
  `First 4 values: [${embeddingResponse.embeddings[0].values.slice(0, 4).join(", ")}...]`
);
// [CODE ENDS]

/* Output Sample

Number of embeddings: 3
Embedding dimensions: 3072
First 4 values: [0.015234, -0.042189, 0.008432, 0.031201...]

*/

/* Markdown (render)
#### Multimodal embeddings

With `gemini-embedding-2`, you can also create embeddings for multimodal inputs such as images, audio, or video alongside text.
*/

// [CODE STARTS]
multimodalResponse = await ai.models.embedContent({
  model: EMBEDDING_MODEL_ID,
  contents: [
    {
      inlineData: {
        data: imageDataUrl,
        mimeType: "image/png",
      },
    },
  ],
});

console.log(
  `Multimodal embedding dimensions: ${multimodalResponse.embeddings[0].values.length}`
);
// [CODE ENDS]

/* Output Sample

Multimodal embedding dimensions: 3072

*/

/* Markdown (render)
<a name="gemini3migration"></a>
## Migrating from Gemini 2.5

[Gemini 3](https://ai.google.dev/gemini-api/docs/gemini-3) models are our most capable model family to date and offer a stepwise improvement over Gemini 2.5. When migrating, consider the following:

* **Interactions API:** Migrate multi-turn, stateful, and tool-augmented workflows to `ai.interactions.create`. State is maintained server-side via `previous_interaction_id`, and conversation steps can be inspected cleanly.
* **Thinking:** Thinking is on by default. Use discrete `thinking_level` values (`"minimal"`, `"low"`, `"medium"`, `"high"`) in `generation_config`.
* **Sampling parameters:** Parameters `temperature`, `top_k`, and `top_p` are deprecated. Use model defaults to avoid degrading reasoning performance.
* **Context caching:** Multi-turn interactions benefit from automatic implicit caching without requiring explicit cache lifecycle management.
* **Media resolution:** Use `media_resolution` (`"media_resolution_low"`, `"media_resolution_high"`) on media parts to manage token consumption for dense PDFs and images.
*/

/* Markdown (render)
## Next Steps

### Useful API references:

* Check out the [Google GenAI SDK](https://googleapis.github.io/js-genai) documentation.
* Explore the [Interactions API guide](https://ai.google.dev/gemini-api/docs/interactions).

### Related examples

* Check the [Python Quickstarts](https://github.com/google-gemini/cookbook/tree/main/quickstarts/) for additional in-depth tutorials on spatial understanding, live API, and multimodal reasoning.
*/
