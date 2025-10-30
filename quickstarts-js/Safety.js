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

The Gemini API has adjustable safety settings. This guide walks you through how to use them. You'll write a prompt that might be blocked, see the reason why, and then adjust the filters to unblock it.

Safety is an important topic, and you can learn more with the links at the end of this guide. Here, you will focus on the code.
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
*/
 
// [CODE STARTS]
const module = await import("https://esm.sh/@google/genai@1.4.0");
const { GoogleGenAI, HarmCategory, HarmBlockThreshold } = module;

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const MODEL_ID = "gemini-2.5-flash-lite";
// [CODE ENDS]

/* Markdown (render)
Send your prompt request to Gemini

Pick a prompt to test the safety filters. This example uses a prompt that could trigger the HARM_CATEGORY_HARASSMENT filter.
*/

// [CODE STARTS]
const unsafePrompt =
  "I support Martians Soccer Club and I think Jupiterians Football Club sucks! Write an ironic phrase about them.";

try {
  const response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: unsafePrompt,
  });
  console.log(response.text);
} catch (e) {
  console.log("Request was blocked.", e.message);
  // If the prompt is blocked, the response will be empty.
  // We can inspect the error to see the reason.
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
The finishReason is SAFETY, which means the request was blocked. You can inspect the safetyRatings to see which category was triggered. In this case, HARM_CATEGORY_HARASSMENT was rated as LOW.

Because the request was blocked, the response text is empty.
*/

/* Markdown (render)
Customizing safety settings

Depending on your use case, you might need to adjust the safety filters. You can customize the safetySettings in your request. In this example, we'll set the harassment filter to BLOCK_LOW_AND_ABOVE.

Important: Only adjust safety settings if you are sure it is necessary for your use case.
*/

// [CODE STARTS]
const safetySettings = [
  {
    category: HarmCategory.HARM_CATEGORY_HARASSMENT,
    threshold: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
  },
];

try {
  const responseWithSettings = await ai.models.generateContent({
    model: MODEL_ID,
    contents: unsafePrompt,
    config: {
      safetySettings: safetySettings,
    },
  });
  console.log("Finish Reason:", responseWithSettings.candidates[0].finishReason);
  console.log(responseWithSettings.text);
} catch (e) {
  console.log("Request was blocked.", e.message);
}
// [CODE ENDS]

/* Output Sample
Request was blocked. [GoogleGenerativeAI Error]: Text generation failed.
*/

/* Markdown (render)
Even with the adjusted settings, this prompt might still be blocked depending on the model's current safety calibration. If it is, the finishReason will still be SAFETY. If it succeeds, the finishReason will be STOP and you will see the generated text.
*/

/* Markdown (render)
Learning more

Learn more with these articles on safety guidance and safety settings.
*/
