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
# Gemini API: All about tokens

An understanding of tokens is central to using the Gemini API. This guide will provide a interactive introduction to what tokens are and how they are used in the Gemini API.

## About tokens

LLMs break up their input and produce their output at a granularity that is smaller than a word, but larger than a single character or code-point.

These **tokens** can be single characters, like `z`, or whole words, like `the`. Long words may be broken up into several tokens. The set of all tokens used by the model is called the vocabulary, and the process of breaking down text into tokens is called tokenization.

For Gemini models, a token is equivalent to about 4 characters. **100 tokens are about 60-80 English words**.

When billing is enabled, the price of a paid request is controlled by the [number of input and output tokens](https://ai.google.dev/pricing), so knowing how to count your tokens is important.

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
## Tokens in the Gemini API

### Context windows

The models available through the Gemini API have context windows that are measured in tokens. These define how much input you can provide, and how much output the model can generate, and combined are referred to as the "context window". This information is available directly through [the API](https://ai.google.dev/api/rest/v1/models/get) and in the [models](https://ai.google.dev/models/gemini) documentation.

In this example you can see the `gemini-2.5-flash` model has an 1M tokens context window. If you need more, Pro models have an even bigger 2M tokens context window.
*/

// [CODE STARTS]
modelInfo = await ai.models.get({ model: MODEL_ID });

console.log("Context window:", modelInfo.inputTokenLimit, "tokens");
console.log("Max output window:", modelInfo.outputTokenLimit, "tokens");

// [CODE ENDS]

/* Output Sample

Context window: 1048576 tokens

Max output window: 65536 tokens

*/

/* Markdown (render)
## Counting tokens

The API provides an endpoint for counting the number of tokens in a request: [`ai.models.countTokens`](https://googleapis.github.io/js-genai/release_docs/classes/models.Models.html#counttokens). You pass the same arguments as you would to [`ai.models.generateContent`](https://googleapis.github.io/js-genai/release_docs/classes/models.Models.html#counttokens) and the service will return the number of tokens in that request.
*/

/* Markdown (render)

### Choose a model

Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Get_started_thinking.js) for more details and in particular learn how to switch the thiking off).

The tokenization should be more or less the same for each of the Gemini models, but you can still switch between the different ones to double-check.

For more information about all Gemini models, check the [documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for extended information on each of them.
*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash" // "gemini-2.5-flash-lite", "gemini-2.5-flash""gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview"
// [CODE ENDS]

/* Markdown (render)
### Text tokens
*/

// [CODE STARTS]
countTokensResponse = await ai.models.countTokens({
  model: MODEL_ID,
  contents: [
    { text: "What's the highest mountain in Africa?" }
  ]
});
console.log("Prompt tokens:", countTokensResponse.totalTokens);
// [CODE ENDS]

/* Output Sample

Prompt tokens: 10

*/

/* Markdown (render)
When you call `ai.models.generateContent` (or `ai.sendMessage`) the response object has a `usageMetadata` attribute containing both the input and output token counts (`promptTokenCount` and `candidatesTokenCount`):
*/

// [CODE STARTS]
genResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "The quick brown fox jumps over the lazy dog."
});

console.log(genResponse.text);
// [CODE ENDS]

/* Output Sample

Indeed it is!

This is a classic example of a **pangram**â€”a sentence that contains every letter of the alphabet at least once.

It&#x27;s famously used for testing typewriters, keyboards, and fonts, as it allows you to see all the letters in action. It&#x27;s remarkably efficient and widely recognized!

*/

// [CODE STARTS]
console.log("Prompt tokens:", genResponse.usageMetadata.promptTokenCount);
console.log("Output tokens:", genResponse.usageMetadata.candidatesTokenCount);
console.log("Total tokens:", genResponse.usageMetadata.totalTokenCount);
// [CODE ENDS]

/* Output Sample

Prompt tokens: 11

Output tokens: 67

Total tokens: 725

*/

/* Markdown (render)
### Multi-modal tokens

All input to the API is tokenized, including images or other non-text modalities.

Images are considered to be a fixed size, so they consume a fixed number of tokens, regardless of their display or file size.

Video and audio files are converted to tokens at a fixed per second rate.

The current rates and token sizes can be found on the [documentation](https://ai.google.dev/gemini-api/docs/tokens?lang=node#multimodal-tokens)
*/

// [CODE STARTS]
const IMAGE_URL = "https://t3.gstatic.com/licensed-image?q=tbn:ANd9GcQVVI2MWny3lHHTBYrzBOkRDMrJ3Bq2SbJrY0utnaCL8r0prFCjGFyujAFblaPu_eqAMXSPkrTqYGJ3rqdIQQ";
imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
  reader = new FileReader();
  reader.onloadend = () => resolve(reader.result.split(',')[1]); 
  reader.readAsDataURL(imageBlob);
});

console.image(imageDataUrl)
// [CODE ENDS]

/* Output Sample

<img src="https://t3.gstatic.com/licensed-image?q=tbn:ANd9GcQVVI2MWny3lHHTBYrzBOkRDMrJ3Bq2SbJrY0utnaCL8r0prFCjGFyujAFblaPu_eqAMXSPkrTqYGJ3rqdIQQ" style="height:auto; width:100%;" />

*/

/* Markdown (render)
#### Inline content

Media objects can be sent to the API inline with the request:
*/

// [CODE STARTS]
countTokensResponse = await ai.models.countTokens({
  model: MODEL_ID,
  contents: [
    {
      inlineData: {
        data: imageDataUrl,
        mimeType: imageBlob.type
      }
    }
  ]
});

console.log("Prompt with image tokens:", countTokensResponse.totalTokens);
// [CODE ENDS]

/* Output Sample

Prompt with image tokens: 288661

*/

/* Markdown (render)
You can try with different images and should always get the same number of tokens, that is independent of their display or file size. Note that an extra token seems to be added, representing the empty prompt.
*/

/* Markdown (render)
#### Files API

The model sees identical tokens if you upload parts of the prompt through the files API instead:
*/

// [CODE STARTS]
organUpload = await ai.files.upload({
    file: imageBlob,
    mimeType: imageBlob.type,
    displayName: "organ.jpg"
});

countTokensResponse = await ai.models.countTokens({
    model: MODEL_ID,
    contents: [
        { fileData: { fileUri: organUpload.uri } }
    ]
});

console.log("Prompt with image tokens:", countTokensResponse.totalTokens);

// [CODE ENDS]

/* Output Sample

Prompt with image tokens: 259

*/

/* Markdown (render)
Audio and video are each converted to tokens at a fixed rate of tokens per minute.
*/

// [CODE STARTS]
mp3Url = "https://storage.googleapis.com/generativeai-downloads/data/State_of_the_Union_Address_30_January_1961.mp3";
response = await fetch(mp3Url);
audioBlob = await response.blob();

audioUrl = URL.createObjectURL(audioBlob);
audio = new Audio(audioUrl);

await new Promise((resolve) => {
  audio.addEventListener("loadedmetadata", () => {
    console.log("Duration (in seconds):", audio.duration);
    resolve();
  });
});

// [CODE ENDS]

/* Output Sample

Duration (in seconds): 2610.128938

*/

/* Markdown (render)
As you can see, this audio file is 2610s long.
*/

// [CODE STARTS]
uploadedAudio = await ai.files.upload({
  file: audioBlob,
  displayName: "sample.mp3",
  mimeType: "audio/mpeg"
});
// [CODE ENDS]

// [CODE STARTS]
countTokensResponse = await ai.models.countTokens({
    model: MODEL_ID,
    contents: [
        {
            fileData: {
                fileUri: uploadedAudio.uri,
                mimeType: uploadedAudio.mimeType
            }
        }
    ]
});

console.log("Prompt with audio tokens:", countTokensResponse.totalTokens);
console.log("Tokens per second:", countTokensResponse.totalTokens / 2610);
// [CODE ENDS]

/* Output Sample

Prompt with audio tokens: 83528

Tokens per second: 32.003065134099614

*/

/* Markdown (render)
### Chat, tools and cache

Chat, tools and cache are currently not supported by the unified SDK `count_tokens` method. This notebook will be updated when that will be the case.

In the meantime you can still check the token used after the call using the `usageMetadata` from the response. Check the [[Python](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Caching.ipynb)] caching notebook for more details.
*/

/* Markdown (render)
## Further reading

For more on token counting, check out the [documentation](https://ai.google.dev/gemini-api/docs/tokens?lang=node#multimodal-tokens) or the API reference:

* [`countTokens`](https://ai.google.dev/api/rest/v1/models/countTokens) REST API reference,
* [`countTokens`](https://googleapis.github.io/js-genai/release_docs/classes/models.Models.html#counttokens) JavaScript API reference,
*/