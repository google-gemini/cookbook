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
# Gemini API: Safety Quickstart

The Gemini API has adjustable safety settings. This notebook walks you through how to use them. You'll write a prompt that's blocked, see the reason why, and then adjust the filters to unblock it.

Safety is an important topic, and you can learn more with the links at the end of this notebook. Here, you will focus on the code.
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
HarmCategory = module.HarmCategory;
HarmBlockThreshold = module.HarmBlockThreshold;

ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
// [CODE ENDS]

/* Markdown (render)
## Send your prompt request to Gemini

Pick the prompt you want to use to test the safety filters settings. An example could be `Write a list of 5 very rude things that I might say to the universe after stubbing my toe in the dark` which was previously tested and triggered the `HARM_CATEGORY_HARASSMENT` and `HARM_CATEGORY_DANGEROUS_CONTENT` categories.
*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash-lite"; // @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]

const unsafePrompt = `I support Martians Soccer Club and I think Jupiterians Football Club sucks! Write an ironic phrase about them.`;

try {
  response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: unsafePrompt,
  });
  console.log("Finish Reason:", response.candidates[0].finishReason);
  console.log(response.text);
} catch (e) {
  console.log("Request was blocked.", e.message);
  // If the prompt is blocked, inspect the error's response object.
  if (e.response) {
      console.log("Finish Reason:", e.response.candidates[0].finishReason);
      console.log("Safety Ratings:", e.response.candidates[0].safetyRatings);
  }
}
// [CODE ENDS]

/* Output Sample
Request was blocked. [GoogleGenerativeAI Error]: Text generation failed.
Finish Reason: SAFETY
Safety Ratings: [
  { category: 'HARM_CATEGORY_HATE_SPEECH', probability: 'NEGLIGIBLE' },
  { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', probability: 'NEGLIGIBLE' },
  { category: 'HARM_CATEGORY_HARASSMENT', probability: 'LOW' },
  { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', probability: 'NEGLIGIBLE' }
]
*/

/* Markdown (render)
The `finishReason` is `SAFETY`, which means the request was blocked. You can inspect the `safetyRatings` to see which category was triggered. In this case, `HARM_CATEGORY_HARASSMENT` was rated as `LOW`.

Because the request was blocked, no text was generated.
*/

/* Markdown (render)
## Customizing safety settings

Depending on your use case, you might need to adjust the safety filters. You can customize the `safetySettings` in your request. In the example below, all the filters are being set to `BLOCK_LOW_AND_ABOVE`.

**Important:** Only adjust safety settings if you are sure it is necessary for your use case. To guarantee Google's commitment to Responsible AI development and its AI Principles, some prompts will be blocked regardless of settings.
*/

// [CODE STARTS]
const safetySettings = [
  {
    category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
    threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_HARASSMENT,
    threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
    threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
  },
  {
    category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
  },
];

try {
    responseWithSettings = await ai.models.generateContent({
        model: MODEL_ID,
        contents: unsafePrompt,
        config: {
            safetySettings: safetySettings,
        }
    });
    console.log("Finish Reason:", responseWithSettings.candidates[0].finishReason);
    console.log(responseWithSettings.text);
} catch(e) {
    console.log("Request was blocked.", e.message);
     if (e.response) {
      console.log("Finish Reason:", e.response.candidates[0].finishReason);
      console.log("Safety Ratings:", e.response.candidates[0].safetyRatings);
  }
}
// [CODE ENDS]

/* Output Sample
Request was blocked. [GoogleGenerativeAI Error]: Text generation failed.
Finish Reason: SAFETY
Safety Ratings: [
  { category: 'HARM_CATEGORY_HATE_SPEECH', probability: 'NEGLIGIBLE' },
  {
    category: 'HARM_CATEGORY_DANGEROUS_CONTENT',
    probability: 'NEGLIGIBLE'
  },
  { category: 'HARM_CATEGORY_HARASSMENT', probability: 'LOW' },
  {
    category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
    probability: 'NEGLIGIBLE'
  }
]
*/

/* Markdown (render)
Even with the adjusted settings, this prompt may still be blocked depending on the model's current safety calibration. If it is blocked, the `finishReason` will still be `SAFETY`. If it succeeds, the `finishReason` will be `STOP` and the generated text will be displayed.
*/

/* Markdown (render)
## Learning more

Learn more with these articles on [safety guidance](https://ai.google.dev/docs/safety_guidance) and [safety settings](https://ai.google.dev/docs/safety_setting_gemini).

## Useful API references:

The JavaScript SDK provides enums for `HarmCategory` and `HarmBlockThreshold` to configure your safety settings.

- `HarmCategory`:
  - `HARM_CATEGORY_HARASSMENT`
  - `HARM_CATEGORY_HATE_SPEECH`
  - `HARM_CATEGORY_SEXUALLY_EXPLICIT`
  - `HARM_CATEGORY_DANGEROUS_CONTENT`

- `HarmBlockThreshold`:
  - `HARM_BLOCK_THRESHOLD_UNSPECIFIED`
  - `BLOCK_LOW_AND_ABOVE`
  - `BLOCK_MEDIUM_AND_ABOVE`
  - `BLOCK_ONLY_HIGH`
  - `BLOCK_NONE`

You can pass these settings in the `config` object on each `generateContent` request. The response, or the error object if the request is blocked, will contain `safetyRatings` for each category.
*/