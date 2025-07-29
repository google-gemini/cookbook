/* Markdown (render)
# Gemini API: Read a PDF

This notebook demonstrates how you can convert a PDF file so that it can be read by the Gemini API.

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
## Download the PDF which will be used for analysis

This PDF page is an article titled [Smoothly editing material properties of objects with text-to-image models and synthetic data](https://research.google/blog/smoothly-editing-material-properties-of-objects-with-text-to-image-models-and-synthetic-data/) available on the Google Research Blog.
*/

// [CODE STARTS]
testPdfBlob = await fetch("https://storage.googleapis.com/generativeai-downloads/data/Smoothly%20editing%20material%20properties%20of%20objects%20with%20text-to-image%20models%20and%20synthetic%20data.pdf")
    .then(res => res.blob());

// [CODE ENDS]

/* Markdown (render)
## Upload the file to the API

Start by uploading the PDF using the File API.
*/

// [CODE STARTS]
pdfFile = await ai.files.upload({
    file: testPdfBlob,
    config: {
        displayName: "test.pdf",
        mimeType: "application/pdf"
    }
});

console.log(pdfFile.name, "successfully uploaded!")
// [CODE ENDS]

/* Output Sample

files/rkz09xjah5hp successfully uploaded!

*/

/* Markdown (render)
## Try it out

Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb) for more details and in particular learn how to switch the thiking off).

*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash" // gemini-2.5-flash-lite","gemini-2.5-flash","gemini-2.5-pro","gemini-2.0-flash"
// [CODE ENDS]

/* Markdown (render)
The pages of the PDF file are each passed to the model as a screenshot of the page plus the text extracted by OCR.
*/

// [CODE STARTS]
countTokensResponse = await ai.models.countTokens({
    model: MODEL_ID,
    contents: [
        {
            fileData: {
                fileUri: pdfFile.uri,
                mimeType: "application/pdf"
            }
        },
        {
            text: "Can you summarize this file as a bulleted list?"
        }
    ]
});

console.log("Prompt with file tokens:", countTokensResponse.totalTokens);
// [CODE ENDS]

/* Output Sample

Prompt with file tokens: 1560

*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            fileData: {
                fileUri: pdfFile.uri,
                mimeType: "application/pdf"
            }
        },
        {
            text: "Can you summarize this file as a bulleted list?"
        }
    ]
});

console.log(response.text)
// [CODE ENDS]

/* Output Sample

Here&#x27;s a summary of the provided content in a bulleted list:

*   **Objective:** To enable smooth, parametric editing of material properties (e.g., color, shininess, transparency) of objects within any photograph, while preserving photorealism, object shape, and lighting.
*   **Problem Addressed:** Existing tools for photorealistic material editing often require expert skill and struggle with disambiguating material from shape/lighting, leading to changes in geometry when only material is desired.
*   **Methodology:**
    *   Leverages pre-trained text-to-image (T2I) models, specifically by fine-tuning **Stable Diffusion 1.5**.
    *   A **synthetic dataset** was created using traditional computer graphics and physically based rendering (PBR) of 100 3D household objects.
    *   This dataset involves systematically varying single material attributes (roughness, metallic, albedo, transparency) across a defined &quot;edit strength&quot; scalar (-1 to +1), while keeping object shape, lighting, and camera angle constant.
    *   The fine-tuned model learns to apply these material edits to a &quot;context image&quot; given an instruction and the desired edit strength.
*   **Key Capabilities &amp; Results:**
    *   Successfully changes object appearance (e.g., making an object metallic or transparent) while retaining its original geometric shape and image lighting.
    *   Realistically fills in hidden background structures and generates accurate caustic effects (refracted light) for transparent objects.
    *   Demonstrates strong generalization from the synthetic training data to real-world images.
    *   A user study found the method&#x27;s outputs to be significantly more photorealistic (69.6% vs. 30.4%) and preferred overall (70.2% vs. 29.8%) compared to InstructPix2Pix.
*   **Applications:**
    *   Facilitates design mock-ups (e.g., visualizing room changes, new product designs).
    *   Enables 3D consistent material edits when combined with Neural Radiance Fields (NeRF) for synthesizing new views of a scene.
*   **Publication:** The method is detailed in the paper &quot;Alchemist: Parametric Control of Material Properties with Diffusion Models,&quot; published at CVPR 2024.

*/

/* Markdown (render)
In addition, take a look at how the Gemini model responds when you ask questions about the images within the PDF.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      fileData: {
        fileUri: pdfFile.uri,
        mimeType: "application/pdf"
      }
    },
    {
      text: "Can you explain the images on the first page of the document?"
    }
  ]
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

The first page of the document primarily features a large visual demonstration of the method&#x27;s capabilities, titled &quot;Smoothly editing material properties of objects with text-to-image models and synthetic data.&quot;

This main image block is structured as a series of **Input** (original image) and **Output** (edited image) pairs, showcasing the model&#x27;s ability to parametrically edit material properties based on text commands.

Here&#x27;s a breakdown of each example:

1.  **Teapot (Roughness Edit):**
    *   **Command:** `&quot;change the roughness of the teapot.&quot;`
    *   **Input:** A smooth, somewhat shiny brown teapot.
    *   **Output:** The same teapot, but its surface now appears significantly rougher, giving it a matte or stony texture while retaining its color and shape.

2.  **Cupid Statue (Transparency Edit):**
    *   **Command:** `&quot;change the transparency of the cupid statue.&quot;`
    *   **Input:** A solid, opaque white cupid statue.
    *   **Output:** The cupid statue becomes translucent, allowing the background (a wall) to be clearly visible through its form. The shape and lighting remain consistent, but the material is now see-through.

3.  **Pot (Metallic Edit):**
    *   **Command:** `&quot;change the metallic of the pot.&quot;`
    *   **Input:** A matte, dark grey/black pot.
    *   **Output:** The pot transforms into a highly metallic object, exhibiting strong reflections and a shiny, polished appearance, akin to polished metal.

4.  **Buddha Statue (Albedo/Base Color Edit):**
    *   **Command:** `&quot;change the albedo of the Buddha statue.&quot;`
    *   **Input:** A golden-colored Buddha statue.
    *   **Output:** The Buddha statue&#x27;s base color (albedo) changes to a lighter, almost white shade, while still maintaining its metallic quality and the way light reflects off its surface.

In essence, these images serve as a primary visual summary of the paper&#x27;s core contribution: demonstrating how the model can precisely and smoothly alter specific material attributes (like roughness, transparency, metallicity, and base color) of objects in an image, solely based on a text prompt, while preserving the object&#x27;s underlying geometry and the scene&#x27;s lighting conditions.

*/

/* Markdown (render)
## Learning more

The File API lets you upload a variety of multimodal MIME types, including images, audio, and video formats. The File API handles inputs that can be used to generate content with `model.generateContent` or `model.streamGenerateContent`.

The File API accepts files under 2GB in size and can store up to 20GB of files per project. Files last for 2 days and cannot be downloaded from the API.

* Learn more about prompting with [media files](https://ai.google.dev/gemini-api/docs/file-prompting-strategies) in the docs, including the supported formats and maximum length.
* Learn more about to extract structured outputs from PDFs in the [Structured outputs on invoices and forms](https://github.com/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb) example.

*/