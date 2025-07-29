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
# Gemini API: Enum Quickstart

The Gemini API allows you to supply a schema to define function arguments (for [function calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb)), or to constrain its output in [JSON](https://github.com/google-gemini/cookbook/blob/main/quickstarts/JSON_mode.ipynb) or using an Enum. This tutorial gives some examples using enums.

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
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite-preview-06-17", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
## Enums
*/

/* Markdown (render)
In the simplest case is you need the model to choose one option from a list of choices, use an enum class to define the schema. Ask it to identify this instrument:
*/

// [CODE STARTS]
IMAGE_URL = "https://storage.googleapis.com/generativeai-downloads/images/instrument.jpg";

// Step 1: Fetch the image as a Blob
imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
    reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]); // Extract base64 string
    reader.readAsDataURL(imageBlob);
});

console.image(imageDataUrl);
// [CODE ENDS]

/* Output Sample

<img src="https://storage.googleapis.com/generativeai-downloads/images/instrument.jpg" style="height:auto; width:100%;" />

*/

/* Markdown (render)
Pass the enum class as the `responseSchema`, and for this simplest case you can use the `responseMimeType = "text/x.enum"` option to get one of those enum members as the response.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            inlineData: {
                data: imageDataUrl,
                mimeType: "image/jpeg"
            }
        },
        "What is the category of this instrument?"
    ],
    config: {
        responseMimeType: "text/x.enum",
        responseSchema: {
            type: "string",
            enum: ["Percussion", "String", "Woodwind", "Brass", "Keyboard"]
        }
    }
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

Keyboard

*/

/* Markdown (render)
You can also use enums with `responseMimeType = "application/json"`. In this simple case the response will be identical but in quotes.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            inlineData: {
                data: imageDataUrl,
                mimeType: "image/jpeg"
            }
        },
        "What category of instrument is this?"
    ],
    config: {
        responseMimeType: "application/json",
        responseSchema: {
            type: "string",
            enum: ["Percussion", "String", "Woodwind", "Brass", "Keyboard"]
        }
    }
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

&quot;Keyboard&quot;

*/

/* Markdown (render)
Outside of simple multiple choice problems, an enum can be used anywhere in the schema for [JSON](../quickstarts/JSON_mode.ipynb) or [function calling](../quickstarts/Function_calling.ipynb). For example, ask it for a list of recipe titles, and use a `Grade` enum to give each one a popularity-grade:
*/

// [CODE STARTS]
recipeSchema = {
  type: "object",
  properties: {
    recipe_name: { type: "string" },
    grade: {
      type: "string",
      enum: ["a+", "a", "b", "c", "d","f"]
    }
  },
  required: ["recipe_name", "grade"]
};
// [CODE ENDS]

/* Markdown (render)
For this example you want a list of `Recipe` objects, so pass `list[Recipe]` to the `response_schema` field of the `generation_config`.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "List about 10 cookie recipes, grade them based on popularity",
  config: {
    responseMimeType: "application/json",
    responseSchema: {
      type: "array",
      items: recipeSchema
    },
    httpOptions: {
      timeout: 60000
    }
  }
});

console.log("```",response.text,"\n```")
// [CODE ENDS]

/* Output Sample

[
  {
    &quot;grade&quot;: &quot;a+&quot;,
    &quot;recipe_name&quot;: &quot;Chocolate Chip Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;a&quot;,
    &quot;recipe_name&quot;: &quot;Peanut Butter Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;a&quot;,
    &quot;recipe_name&quot;: &quot;Oatmeal Raisin Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;a+&quot;,
    &quot;recipe_name&quot;: &quot;Sugar Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;b&quot;,
    &quot;recipe_name&quot;: &quot;Snickerdoodle Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;b&quot;,
    &quot;recipe_name&quot;: &quot;Gingerbread Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;c&quot;,
    &quot;recipe_name&quot;: &quot;Shortbread Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;c&quot;,
    &quot;recipe_name&quot;: &quot;Macarons&quot;
  },
  {
    &quot;grade&quot;: &quot;b&quot;,
    &quot;recipe_name&quot;: &quot;Molasses Cookies&quot;
  },
  {
    &quot;grade&quot;: &quot;a&quot;,
    &quot;recipe_name&quot;: &quot;No-Bake Cookies&quot;
  }
] 


*/

/* Markdown (render)
## Next Steps
### Useful API references:

Check the [structured ouput](https://ai.google.dev/gemini-api/docs/structured-output) documentation or the [`GenerationConfig`](https://ai.google.dev/api/generate-content#generationconfig) API reference for more details.

### Related examples

* The constrained output is used in the [Text summarization](https://github.com/google-gemini/cookbook/blob/main/examples/json_capabilities/Text_Summarization.ipynb) example to provide the model a format to summarize a story (genre, characters, etc...)
* The [Object detection](https://github.com/google-gemini/cookbook/blob/main/examples/Object_detection.ipynb) examples are using the JSON constrained output to uniiformize the output of the detection.

### Continue your discovery of the Gemini API

An Enum is not the only way to constrain the output of the model, you can also use an [JSON](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Enum.ipynb) schema. [Function calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb) and [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb) are other ways to enhance your model by either let him use your own functions or by letting it write and run them.
*/