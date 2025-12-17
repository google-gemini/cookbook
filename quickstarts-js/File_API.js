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
# Gemini API: File API Quickstart

The Gemini API supports prompting with text, image, and audio data, also known as *multimodal* prompting. You can include text, image,
and audio in your prompts. For small images, you can point the Gemini model
directly to a local file when providing a prompt. For larger text files, images, videos, and audio, upload the files with the [File
API](https://ai.google.dev/api/rest/v1beta/files) before including them in
prompts.

The File API lets you store up to 20GB of files per project, with each file not
exceeding 2GB in size. Files are stored for 48 hours and can be accessed with
your API key for generation within that time period. It is available at no cost in all regions where the [Gemini API is
available](https://ai.google.dev/available_regions).

For information on valid file formats (MIME types) and supported models, see the documentation on
[supported file formats](https://ai.google.dev/tutorials/prompting_with_media#supported_file_formats)
and view the text examples at the end of this guide.

This guide shows how to use the File API to upload a media file and include it in a `GenerateContent` call to the Gemini API.

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
## Upload file

The File API lets you upload a variety of multimodal MIME types, including images and audio formats. The File API handles inputs that can be used to generate content with [`model.generateContent`](https://ai.google.dev/api/generate-content#method:-models.generatecontent) or [`model.streamGenerateContent`](https://ai.google.dev/api/generate-content#method:-models.streamgeneratecontent).

The File API accepts files under 2GB in size and can store up to 20GB of files per project. Files last for 2 days and cannot be downloaded from the API.

First, you will prepare a sample image to upload to the API.
*/

// [CODE STARTS]
imageFile = await fetch("https://storage.googleapis.com/generativeai-downloads/images/jetpack.jpg")
    .then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
    reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]); // Get only base64 string
    reader.readAsDataURL(imageFile);
});
console.image(imageDataUrl)
// [CODE ENDS]

/* Output Sample

<img src="https://storage.googleapis.com/generativeai-downloads/images/jetpack.jpg" style="height:auto; width:100%;" />

*/

/* Markdown (render)
Next, you will upload that file to the File API.
*/

// [CODE STARTS]
uploadedFile = await ai.files.upload({ file: imageFile });

console.log(`Uploaded file '${uploadedFile.name}' as: ${uploadedFile.uri}`);
// [CODE ENDS]

/* Output Sample

Uploaded file &#x27;files/wrcset8sfug1&#x27; as: https://generativelanguage.googleapis.com/v1main/files/wrcset8sfug1

*/

/* Markdown (render)

The `response` object confirms that the File API stored the specified `displayName` for the uploaded file along with a `uri` that can be used to reference the file in future Gemini API calls. You can use the `response` to track how uploaded files are associated with their URIs.

Depending on your use case, you might want to store the URIs in structures like a plain JavaScript object or a database.

*/

/* Markdown (render)
## Get file

After uploading the file, you can verify the API has successfully received the files by calling `files.get`.

It lets you get the file metadata that have been uploaded to the File API that are associated with the Cloud project your API key belongs to. Only the `name` (and by extension, the `uri`) are unique. Only use the `displayName` to identify files if you manage uniqueness yourself.
*/

// [CODE STARTS]
const retrievedFile = await ai.files.get({ name: uploadedFile.name });
console.log(`Retrieved file '${retrievedFile.name}' as: ${retrievedFile.uri}`);
// [CODE ENDS]

/* Output Sample

Retrieved file &#x27;files/wrcset8sfug1&#x27; as: https://generativelanguage.googleapis.com/v1main/files/wrcset8sfug1

*/

/* Markdown (render)
## Generate content

After uploading the file, you can make `GenerateContent` requests that reference the file by providing the URI. In the Python SDK you can pass the returned object directly.

Here you create a prompt that starts with text and includes the uploaded image.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      fileData: {
        fileUri: uploadedFile.uri,
        mimeType: "image/jpeg"
      }
    },
    "Describe the image with a creative description."
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Behold, a visionary concept scribbled with bold blue ink on classic ruled notebook paper: the &quot;JETPACK BACKPACK.&quot;

This ingenious invention, proudly titled at the top, presents itself as an unassuming rounded backpack, sleek in its sketched simplicity. But the arrows pointing to its various features tell a tale of discreet power and futuristic practicality.

On the left, we learn of its ergonomic design, promising &quot;PADDED STRAP SUPPORT&quot; for comfort, even when soaring above the daily commute. Below, the future of charging is here, with &quot;USB-C CHARGING,&quot; though adventurers will need to plan their flights carefully, as it offers a &quot;15-MIN BATTERY LIFE.&quot;

To the right, the backpack&#x27;s true magic is revealed. It&#x27;s designed to be &quot;LIGHTWEIGHT&quot; and, crucially, &quot;LOOKS LIKE A NORMAL BACKPACK,&quot; allowing its wearer to blend seamlessly into any crowd before making a grand exit. It&#x27;s capacious too, designed to fit an &quot;18&quot; LAPTOP.&quot; The core of its power lies beneath, with &quot;RETRACTABLE BOOSTERS&quot; ready to emerge when needed, unleashing whimsical, swirling plumes of &quot;STEAM-POWERED&quot; propulsion â€“ a promise of &quot;GREEN/CLEAN&quot; flight that leaves nothing but a charming vapor trail in its wake.

This handwritten blueprint captures the dream of everyday flight, balancing the fantastical with thoughtful, if ambitious, specifications.

*/

/* Markdown (render)
## Delete files

Files are automatically deleted after 2 days or you can manually delete them using `files.delete()`.
*/

// [CODE STARTS]
await ai.files.delete({ name: uploadedFile.name });
console.log(`Deleted ${uploadedFile.name}.`);
// [CODE ENDS]

/* Output Sample

Deleted files/wrcset8sfug1.

*/

/* Markdown (render)
## Supported text types

As well as supporting media uploads, the File API can be used to embed text files, such as Python code, or Markdown files, into your prompts.

This example shows you how to load a markdown file into a prompt using the File API.
*/

// [CODE STARTS]
fileUrl = "https://raw.githubusercontent.com/google-gemini/cookbook/main/CONTRIBUTING.md";

response = await fetch(fileUrl);
blob = await response.blob();
file = new File([blob], "contrib.md", { type: "text/markdown" });

uploadedFile = await ai.files.upload({
  file,
  config: {
    displayName: "CONTRIBUTING.md",
    mimeType: "text/markdown"
  }
});
console.log("Uploaded:", uploadedFile.uri);

modelResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      text: "What should I do before I start writing, when following these guidelines?"
    },
    {
      fileData: {
        fileUri: uploadedFile.uri,
        mimeType: "text/markdown"
      }
    }
  ]
});

console.log(modelResponse.text);

await ai.files.delete({ name: uploadedFile.name });
console.log(`Deleted ${uploadedFile.name}`);

// [CODE ENDS]

/* Output Sample

Uploaded: https://generativelanguage.googleapis.com/v1main/files/qvq94l4c5jhz

Before you start writing, when contributing to the Gemini API Cookbook, you should do the following:

1.  **Sign the Contributor License Agreement (CLA):** All contributions require you (or your employer) to sign a CLA. Visit [https://cla.developers.google.com/](https://cla.developers.google.com/) to check your current agreements or sign a new one.
2.  **Review Style Guides:**
    *   Take a look at the [technical writing style guide](https://developers.google.com/style), specifically reading the [highlights](https://developers.google.com/style/highlights) to understand common feedback points.
    *   Check out the relevant [style guide](https://google.github.io/styleguide/) for the language you will be using (e.g., Python).
3.  **File an Issue:** For any new content submission (beyond small fixes), you **must** file an [issue](https://github.com/google-gemini/cookbook/issues) on GitHub. This allows for discussion of your idea, guidance on structure, and ensures your concept has support before you invest time in writing.

Deleted files/qvq94l4c5jhz

*/

/* Markdown (render)
Some common text formats are automatically detected, such as `text/x-python`, `text/html` and `text/markdown`. If you are using a file that you know is text, but is not automatically detected by the API as such, you can specify the MIME type as `text/plain` explicitly.
*/

// [CODE STARTS]
fileUrl = "https://raw.githubusercontent.com/google/gemma.cpp/main/examples/hello_world/run.cc";

response = await fetch(fileUrl);
blob = await response.blob();
cppFile = new File([blob], "gemma.cpp", { type: "text/plain" }); // Forced MIME

uploadedCpp = await ai.files.upload({
  file: cppFile,
  config: {
    displayName: "gemma.cpp",
    mimeType: "text/plain"
  }
});
console.log("Uploaded:", uploadedCpp.uri);

modelResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { text: "What does this program do?" },
    {
      fileData: {
        fileUri: uploadedCpp.uri,
        mimeType: "text/plain"
      }
    }
  ]
});

console.log(modelResponse.text);

await ai.files.delete({ name: uploadedCpp.name });
console.log(`Deleted ${uploadedCpp.name}`);

// [CODE ENDS]

/* Output Sample

Uploaded: https://generativelanguage.googleapis.com/v1main/files/ih9sjrj7h21x

This C++ program is a minimal example demonstrating how to load and use Google&#x27;s **Gemma large language model** for text generation, with a specific focus on **constrained decoding**.

Here&#x27;s a breakdown of what it does:

1.  **Argument Parsing:**
    *   It processes command-line arguments using `gcpp::LoaderArgs`, `gcpp::InferenceArgs`, and `gcpp::AppArgs`. These likely configure aspects like the model path, batch size, number of threads, etc.
    *   It specifically looks for a `&quot;--reject&quot;` flag. Any integer arguments following `--reject` are interpreted as token IDs that should *never* be generated by the model. This is the core of its constrained decoding demonstration.

2.  **Model Initialization:**
    *   It sets up the necessary environment for the Gemma model, including:
        *   `gcpp::BoundedTopology` and `gcpp::NestedPools`: For managing threading and parallel computations (likely using Highway, a SIMD library).
        *   `gcpp::MatMulEnv`: An environment for matrix multiplication, essential for neural networks.
        *   `gcpp::Gemma model`: The actual Gemma model instance, loaded based on `loader` arguments.
        *   `gcpp::KVCache kv_cache`: A Key-Value Cache, crucial for efficient LLM inference by storing past activations, avoiding recomputation.

3.  **Prompt Definition and Tokenization:**
    *   It defines a fixed input prompt: `&quot;Write a greeting to the world.&quot;`
    *   It then uses the model&#x27;s tokenizer (`model.Tokenizer()`) to convert this string prompt into a sequence of integer token IDs.

4.  **Text Generation with Callbacks:**
    *   **Random Number Generator:** Initializes a `std::mt19937` (Mersenne Twister) random number generator, seeded by `std::random_device`, which is used for probabilistic token sampling during generation (e.g., when `temperature` &gt; 0).
    *   **`stream_token` Callback:** A lambda function is defined to be called every time the model generates a new token.
        *   If the token is part of the initial prompt (before generation truly starts), it currently does nothing (the placeholder comment `// print feedback` suggests it *could* be used for that).
        *   Once actual generation begins, it decodes the integer token ID back into human-readable text using `model.Tokenizer().Decode()` and prints it immediately to `std::cout` using `std::flush`. This provides a streaming output experience.
    *   **`accept_token` Callback (Constrained Decoding):** Another lambda function is defined. This is the core of the `--reject` functionality.
        *   Before the model chooses a token, this callback is invoked for potential candidate tokens.
        *   It checks if the candidate token is present in the `reject_tokens` set (populated from the `--reject` command-line argument).
        *   If the token *is* in `reject_tokens`, it returns `false`, effectively preventing the model from ever outputting that specific token. This &quot;constrains&quot; the output.
    *   **`model.Generate()`:** The program then calls `model.Generate()`, passing in:
        *   `runtime_config`: Containing generation parameters like `max_generated_tokens` (1024), `temperature` (1.0), the random generator, the `stream_token` callback, and crucially, the `accept_token` callback.
        *   `tokens`: The initial prompt tokens.
        *   `kv_cache`: For efficient inference.

**In Summary:**

This program loads the Gemma large language model, initializes it with various parameters (some configurable via command-line), tokenizes a hardcoded prompt (&quot;Write a greeting to the world.&quot;), and then generates a response. Its primary demonstration feature is **constrained decoding**, allowing the user to specify (via the `--reject` flag) certain token IDs that the model must *never* output during the generation process. The generated text is streamed to standard output token by token.

Deleted files/ih9sjrj7h21x

*/

/* Markdown (render)
## Next Steps
### Useful API references:

For more information about the File API, check its [API reference](https://ai.google.dev/api/files). You will also find more code samples [in this folder](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/).

### Related examples

Check those examples using the File API to give you more ideas on how to use that very useful feature:
* Share [Voice memos](https://github.com/google-gemini/cookbook/blob/main/examples/Voice_memos.ipynb) with Gemini API and brainstorm ideas
* Analyze videos to [classify](https://github.com/google-gemini/cookbook/blob/main/examples/Analyze_a_Video_Classification.ipynb) or [summarize](https://github.com/google-gemini/cookbook/blob/main/examples/Analyze_a_Video_Summarization.ipynb) them

### Continue your discovery of the Gemini API

If you're not already familiar with it, learn how [tokens are counted](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Counting_Tokens.js). Then check how to use the File API to use [Audio](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Audio.js) or [Video_understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Video_understanding.js) files with the Gemini API.

*/