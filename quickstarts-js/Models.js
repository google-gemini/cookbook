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
# Gemini API: List models

This notebook demonstrates how to list the models that are available for you to use in the Gemini API, and how to find details about a model.

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

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
## List models

Use `listModels()` to see what models are available. These models support `generateContent`, the main method used for prompting.
*/

// [CODE STARTS]
models = await ai.models.list();
  for await (model of models) {
    console.log(model.name);
  }
// [CODE ENDS]

/* Output Sample

models/embedding-gecko-001

models/gemini-2.5-pro-preview-03-25

models/gemini-2.5-flash-preview-05-20

models/gemini-2.5-flash

models/gemini-2.5-flash-lite-preview-06-17

models/gemini-2.5-pro-preview-05-06

models/gemini-2.5-pro-preview-06-05

models/gemini-2.5-pro

models/gemini-2.0-flash-exp

models/gemini-2.0-flash

models/gemini-2.0-flash-001

models/gemini-2.0-flash-exp-image-generation

models/gemini-2.0-flash-lite-001

models/gemini-2.0-flash-lite

models/gemini-2.0-flash-preview-image-generation

models/gemini-2.0-flash-lite-preview-02-05

models/gemini-2.0-flash-lite-preview

models/gemini-2.0-pro-exp

models/gemini-2.0-pro-exp-02-05

models/gemini-exp-1206

models/gemini-2.0-flash-thinking-exp-01-21

models/gemini-2.0-flash-thinking-exp

models/gemini-2.0-flash-thinking-exp-1219

models/gemini-2.5-flash-preview-tts

models/gemini-2.5-pro-preview-tts

models/learnlm-2.0-flash-experimental

models/gemma-3-1b-it

models/gemma-3-4b-it

models/gemma-3-12b-it

models/gemma-3-27b-it

models/gemma-3n-e4b-it

models/gemma-3n-e2b-it

models/gemini-flash-latest

models/gemini-flash-lite-latest

models/gemini-pro-latest

models/gemini-2.5-flash-lite

models/gemini-2.5-flash-image-preview

models/gemini-2.5-flash-image

models/gemini-2.5-flash-preview-09-2025

models/gemini-2.5-flash-lite-preview-09-2025

models/gemini-robotics-er-1.5-preview

models/gemini-2.5-computer-use-preview-10-2025

models/embedding-001

models/text-embedding-004

models/gemini-embedding-exp-03-07

models/gemini-embedding-exp

models/gemini-embedding-001

models/aqa

models/imagen-3.0-generate-002

models/imagen-4.0-generate-preview-06-06

models/imagen-4.0-ultra-generate-preview-06-06

models/imagen-4.0-generate-001

models/imagen-4.0-ultra-generate-001

models/imagen-4.0-fast-generate-001

models/veo-2.0-generate-001

models/gemini-2.0-flash-live-001

models/gemini-live-2.5-flash-preview

models/gemini-2.5-flash-live-preview

models/gemini-2.5-flash-native-audio-latest

models/gemini-2.5-flash-native-audio-preview-09-2025

models/lyria-realtime-exp

*/

/* Markdown (render)
These models support `embedContent`, used for embeddings:
*/

// [CODE STARTS]
models = await ai.models.list();

for await (model of models) {
  if (model.supportedActions?.includes("embedContent")) {
    console.log(model.name);
  }
}

// [CODE ENDS]

/* Output Sample

models/embedding-001

models/text-embedding-004

models/gemini-embedding-exp-03-07

models/gemini-embedding-exp

models/gemini-embedding-001

*/

/* Markdown (render)
## Find details about a model

You can see more details about a model, including the `inputTokenLimit` and `outputTokenLimit` as follows.
*/

// [CODE STARTS]
models = await ai.models.list();

for await (model of models) {
  if (model.name === "models/gemini-2.5-flash") {
    console.log(model);
  }
}

// [CODE ENDS]

/* Output Sample

{
  &quot;name&quot;: &quot;models/gemini-2.5-flash&quot;,
  &quot;displayName&quot;: &quot;Gemini 2.5 Flash&quot;,
  &quot;description&quot;: &quot;Stable version of Gemini 2.5 Flash, our mid-size multimodal model that supports up to 1 million tokens, released in June of 2025.&quot;,
  &quot;version&quot;: &quot;001&quot;,
  &quot;tunedModelInfo&quot;: {},
  &quot;inputTokenLimit&quot;: 1048576,
  &quot;outputTokenLimit&quot;: 65536,
  &quot;supportedActions&quot;: [
    &quot;generateContent&quot;,
    &quot;countTokens&quot;,
    &quot;createCachedContent&quot;,
    &quot;batchGenerateContent&quot;
  ]
}

*/

/* Markdown (render)
## Learning more

* To learn how use a model for prompting, see the [Prompting](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Prompting.ipynb) quickstart.

* To learn how use a model for embedding, see the [Embedding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Embeddings.ipynb) quickstart.

* For more information on models, visit the [Gemini models](https://ai.google.dev/models/gemini) documentation.
*/