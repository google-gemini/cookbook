/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* Markdown (render)
# Gemini API: PDF Quickstart

This notebook demonstrates how you can convert a PDF file so that it can be read by the Gemini API.
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
MODEL_ID = "gemini-3-flash-preview" // "gemini-2.5-flash-lite", "gemini-2.5-flash""gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview"
// [CODE ENDS]

/* Markdown (render)

###Download the PDF

This PDF page is an article titled Smoothly editing material properties of objects with text-to-image models and synthetic data available on the Google Research Blog. 
*/

// [CODE STARTS] 
PDF_URL = "https://storage.googleapis.com/generativeai-downloads/data/Smoothly%20editing%20material%20properties%20of%20objects%20with%20text-to-image%20models%20and%20synthetic%20data.pdf"; 
pdfBlob = await fetch(PDF_URL).then(res => res.blob()); 
pdfMime = "application/pdf"; 
// [CODE ENDS]

/* Markdown (render)
###Upload the file to the API

Start by uploading the PDF using the [File API](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/File_API.ipynb).
*/

// [CODE STARTS] 
pdfFile = await ai.files.upload({ file: pdfBlob, config: { mimeType: pdfMime }, }); 
// [CODE ENDS]


/* Markdown (render)

The pages of the PDF file are each passed to the model as a screenshot of the page plus the text extracted by OCR.

You can count the tokens before sending the request to ensure it fits within the context window. 
*/
 
// [CODE STARTS] 
countTokensResponse = await ai.models.countTokens({ model: MODEL_ID, contents: [ { fileData: { fileUri: pdfFile.uri, mimeType: pdfMime } }, { text: 'Can you summarize this file as a bulleted list?' } ] });
console.log("Total tokens:", countTokensResponse.totalTokens); 
// [CODE ENDS]

/* Output Sample Total tokens: 3372 */

/* Markdown (render) 
Now, generate content using the uploaded file. 
*/

// [CODE STARTS] 
response = await ai.models.generateContent({ model: MODEL_ID, contents: [ { fileData: { fileUri: pdfFile.uri, mimeType: pdfMime } }, { text: 'Can you summarize this file as a bulleted list?' } ] });
console.log(response.text); 
// [CODE ENDS]

/* Output Sample
Based on the provided document from Google Research, here is a summary of the new method for editing object materials:

*   **Core Objective:** Researchers developed a method called **"Alchemist"** (presented at CVPR 2024) that allows users to precisely edit the material properties of objects in any photograph using text-to-image models.
*   **Controllable Properties:** The model provides "parametric control" over specific attributes, including **roughness, metallic appearance, albedo (base color), and transparency.**
*   **Shape Preservation:** Unlike previous generative models that often change an object's shape when trying to change its color or style, this method successfully modifies material properties while **preserving the original geometric shape**.
*   **The Synthetic Training Method:**
    *   The team used traditional computer graphics and physically based rendering to create a synthetic dataset of 100 3D household objects.
    *   They generated "base images" and then produced versions with varying "edit strengths" (a scalar value from -1 to +1) for specific attributes.
    *   They fine-tuned **Stable Diffusion 1.5** to accept these scalar values, teaching the model to change only the requested material property.
*   **Key Results:**
    *   The model generalizes well, meaning it can apply what it learned from synthetic data to real-world photographs.
    *   When making objects transparent, the model can realistically "fill in" the background and interior structures, including complex light effects like **caustics** (refracted light).
    *   In user studies, this method was found to be more photorealistic (69.6% vs. 30.4%) and was strongly preferred over baseline methods like InstructPix2Pix.
*   **Potential Applications:** 
    *   **Design:** Visualizing home renovations (e.g., changing paint color) or mocking up new product designs.
    *   **3D Modeling:** The edits are visually consistent enough to be used in downstream 3D tasks like **NeRF (Neural Radiance Fields)** to create 3D-consistent renderings of material changes.
*/

/* Markdown (render) 
In addition, take a look at how the Gemini model responds when you ask questions about the images within the PDF. 
*/

// [CODE STARTS] 
response_2 = await ai.models.generateContent({ model: MODEL_ID, contents: [ { fileData: { fileUri: pdfFile.uri, mimeType: pdfMime } }, { text: 'Can you explain the images on the first page of the document?' } ] });
console.log(response_2.text); 
// [CODE ENDS]

/* Output Sample
The images on the first page of the document serve as a visual demonstration of the research's primary goal: **parametric editing of material properties in photographs.**

The collage in the top-right corner displays four pairs of "Input" and "Output" images, each illustrating a different type of material transformation while preserving the object's original shape and lighting:

*   **Roughness:** The first example shows a teapot with the prompt "change the roughness of the teapot," demonstrating how the model can adjust the surface texture from matte to shiny or vice versa.
*   **Transparency:** The second example shows a stone cupid statue becoming translucent with the prompt "change the transparency of the cupid statue."
*   **Metallic Appearance:** The third example shows a ceramic plant pot taking on a metallic finish with the prompt "change the metallic of the pot."
*   **Albedo (Base Color):** The final example shows a Buddha statue having its base color/reflectance changed with the prompt "change the albedo of the Buddha statue."

Overall, these images highlight the model's ability to "disentangle" material properties from geometric shape, allowing users to precisely control how an object looks (e.g., how shiny, clear, or metallic it is) without changing what the object is.
*/

/* Markdown (render) 
## Next Steps

The File API lets you upload a variety of multimodal MIME types, including images, audio, and video formats. The File API handles inputs that can be used to generate content with `model.generateContent` or `model.streamGenerateContent`.

The File API accepts files under 2GB in size and can store up to 20GB of files per project. Files last for 2 days and cannot be downloaded from the API.

* Learn more about prompting with [media files](https://ai.google.dev/gemini-api/docs/file-prompting-strategies) in the docs, including the supported formats and maximum length.
* Learn more about to extract structured outputs from PDFs in the [Structured outputs on invoices and forms](https://github.com/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb) example.
*/
