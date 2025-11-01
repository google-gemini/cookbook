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
# Gemini API: Asynchronous JavaScript requests

This notebook demonstrates how to make asynchronous and parallel requests using the Gemini API's JavaScript SDK with modern async/await syntax.

The examples here can run in environments like Node.js, or in browser consoles that support async functions. You can also manage concurrency using JavaScript's built-in event loop with `Promise.all()` or `for await...of` for efficient parallel execution.

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
## Using local files

This simple example shows how can you use local files (presumed to load quickly) with the SDK's `async` API.
*/

// [CODE STARTS]
prompt = "Describe this image in just 3 words.";

imgFilenames = ["firefighter.jpg", "elephants.jpeg", "jetpack.jpg"];
imgDir = "https://storage.googleapis.com/generativeai-downloads/images/";
// [CODE ENDS]

/* Markdown (render)
Start by downloading the files locally.
*/

// [CODE STARTS]
imgFilenames = ["firefighter.jpg", "elephants.jpeg", "jetpack.jpg"];
imgDir = "https://storage.googleapis.com/generativeai-downloads/images/";

imageList = []
for (imgFilename of imgFilenames) {
  imageBlob = await fetch(imgDir + imgFilename).then(res => res.blob());
  imageBase64 = await new Promise((resolve) => {
    reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(imageBlob);
  });

  imageList.push({ inlineData: { data: imageBase64, mimeType: "image/jpeg" } });
}
// [CODE ENDS]

/* Markdown (render)
This async function uses ai.models.generateContent to describe local images sequentially. Each await pauses for the API response, allowing the event loop to handle other tasks in between.
*/

// [CODE STARTS]
async function describeLocalImages() {
  for (image of imageList) {
    response = await ai.models.generateContent({
      model: MODEL_ID,
      contents: [prompt, image],
    });
    console.log(response.text);
  }
}

await describeLocalImages();
// [CODE ENDS]

/* Output Sample

Boy, cat, tree.

Jungle elephant family

Jetpack Backpack Sketch

*/

/* Markdown (render)
## Downloading images asynchronously and in parallel

This example shows a more real-world case where images are downloaded from an external source using the async fetch() function in JavaScript, and each image is processed in parallel.
*/

// [CODE STARTS]
async function downloadImage(imgUrl) {
  imageBlob = await fetch(imgUrl).then(res => res.blob());
  imageBase64 = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(imageBlob);
  });

  return { inlineData: { data: imageBase64, mimeType: "image/jpeg" } };
}

async function processImage(imgPromise) {
  response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [prompt, await imgPromise],
  });
  return response.text;
}

responsePromises = [];

for (imgFilename of imgFilenames) {
  const imgPromise = downloadImage(imgDir + imgFilename);
  const textPromise = processImage(imgPromise);
  responsePromises.push(textPromise);
}

console.log(`Download and content generation queued for ${responsePromises.length} images.`);

for await (response of responsePromises) {
  console.log(await response);
}
// [CODE ENDS]

/* Output Sample

Download and content generation queued for 3 images.

Boy, cat, tree.

Wild Elephant Family

Jetpack concept sketch.

*/

/* Markdown (render)
In the above example, an async function is created for each image that both downloads and then summarizes the image. These async tasks are executed in the final step, when their Promises are awaited in sequence. To start them as early as possible without blocking other work, you could wrap the downloadImage call in Promise.resolve() or trigger it immediately, but in this example, execution is deferred to keep the creation and execution logic separate.
*/

/* Markdown (render)
## Next Steps

* Explore the [`@google/genai`](https://www.npmjs.com/package/@google/genai) JavaScript SDK for detailed usage and API documentation.  
* Learn more about JavaScript's [`async/await`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function) and [`Promise.all`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all) for efficient parallel execution.
*/