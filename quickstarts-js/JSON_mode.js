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
# Gemini API: JSON Mode and Enum Quickstart

When building applications with the Gemini API, you often need the model's output in a structured format—for example, extracting recipe data to populate a database, or classifying items into predefined categories. JSON mode lets you constrain the model's response to valid JSON, so you can reliably parse the output without fragile string manipulation.

This guide walks you through two approaches—describing the schema in your prompt vs. supplying it programmatically—and shows how to use Enum constraints for classification tasks.

## Setup
### Install SDK and set-up the client

To interact with Gemini models using JavaScript, you'll need the `@google/genai` library. In standard environments, you can install the SDK using `npm`:

```bash
npm install @google/genai
```

Once installed, you can import and initialize the client in your code:

```js
import { GoogleGenAI } from '@google/genai';
const ai = new GoogleGenAI({});
```

In this notebook's interactive environment, the SDK is imported dynamically from a CDN.

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

MODEL_ID = "gemini-3.5-flash" // "gemini-3.5-flash", "gemini-3-pro"
// [CODE ENDS]

/* Markdown (render)
## Set your constrained output in the prompt

The simplest approach is to describe the desired output format directly in the prompt. The notation below (`Recipe = {'recipe_name': str}`, `Return: list[Recipe]`) uses Python-style type hints as a shorthand—Gemini understands this convention even in JavaScript contexts since the schema format originates from the Python SDK:

*/

// [CODE STARTS]
prompt = `
  List a few popular cookie recipes using this JSON schema:

  Recipe = {'recipe_name': str}
  Return: list[Recipe]
`
// [CODE ENDS]

/* Markdown (render)
Now select the model you want to use in this guide. Keep in mind that some models, like the 3.5 ones, are thinking models and thus take slightly more time to respond (cf. [thinking notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_thinking.ipynb) for more details).

Then activate JSON mode by specifying `responseMimeType` as `application/json` in the `config` parameter:
*/

// [CODE STARTS]
rawResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: prompt,
  config: {
    responseMimeType: 'application/json',
  },
});

console.log("```\n",rawResponse.text,"\n```")
// [CODE ENDS]

/* Output Sample

```
 [
  {
    "recipe_name": "Chocolate Chip Cookies"
  },
  {
    "recipe_name": "Oatmeal Raisin Cookies"
  },
  {
    "recipe_name": "Peanut Butter Cookies"
  },
  {
    "recipe_name": "Sugar Cookies"
  }
] 
```

*/

/* Markdown (render)
## Supply the schema to the model directly

You can pass a structured schema object directly to the model configuration, ensuring the output strictly adheres to the schema shape. The schema follows the [OpenAPI 3.0 Schema Object](https://spec.openapis.org/oas/v3.0.3#schema-object) format.

Here is a schema definition for a cookie recipe:
*/

// [CODE STARTS]
recipeSchema = {
  type: "object",
  properties: {
    recipe_name: { type: "string" },
    recipe_description: { type: "string" },
    recipe_ingredients: {
      type: "array",
      items: { type: "string" },
    },
  },
  required: ["recipe_name", "recipe_description", "recipe_ingredients"],
};

// [CODE ENDS]

/* Markdown (render)
To request a list of recipes matching this structure, define the `responseSchema` as an array of the `recipeSchema` object:
*/

// [CODE STARTS]
result = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "List a few imaginative cookie recipes along with a one-sentence description as if you were a gourmet restaurant and their main ingredients",
  config: {
    responseMimeType: "application/json",
    responseSchema: {
        type: "array",
        items: recipeSchema
    },
  },
});
console.log("```\n",result.text,"\n```");

// [CODE ENDS]

/* Output Sample

```
 [
  {
    "recipe_description": "A crescent of delicate shortbread, infused with the warm embrace of autumnal pear and a whisper of exotic cardamom, culminating in a celestial experience.",
    "recipe_ingredients": ["Unsalted butter", "All-purpose flour", "Powdered sugar", "Ripe pears", "Ground cardamom", "Vanilla bean paste"],
    "recipe_name": "Celestial Spiced Pear & Cardamom Crescent"
  },
  {
    "recipe_description": "Rich, dark chocolate cookies with a molten espresso ganache heart, dusted with cocoa for an intensely decadent and sophisticated bite.",
    "recipe_ingredients": ["Dark cocoa powder", "Unsalted butter", "Granulated sugar", "Eggs", "All-purpose flour", "Espresso powder", "Heavy cream", "Bittersweet chocolate"],
    "recipe_name": "Midnight Velvet Espresso Truffle Buttons"
  },
  {
    "recipe_description": "Crisp, golden honey shortbread adorned with delicate crystallized lavender florets, offering a sweet, aromatic, and truly ethereal indulgence.",
    "recipe_ingredients": ["Unsalted butter", "All-purpose flour", "Granulated sugar", "Honey", "Culinary lavender", "Egg yolk", "Sea salt"],
    "recipe_name": "Lavender Honeycomb Dreams"
  }
] 
```

*/

/* Markdown (render)
## Enums

If you need the model to choose one option from a set of choices, you can define an enum constraint. 

Let's fetch a sample image of a musical instrument:
*/

// [CODE STARTS]
IMAGE_URL = "https://storage.googleapis.com/generativeai-downloads/images/instrument.jpg";

imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
    reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]); // Extract base64 string
    reader.readAsDataURL(imageBlob);
});
// [CODE ENDS]

/* Markdown (render)
You can pass the enum constraint as the `responseSchema`, and set `responseMimeType` to `text/x.enum` to retrieve only the raw matched value:
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
Alternatively, you can query enums with `responseMimeType` set to `application/json`, which returns the value in JSON quotes:
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

"Keyboard"

*/

/* Markdown (render)
## Using Enums within a JSON Schema

You can also nest Enum schemas inside properties of a larger JSON schema. Let's ask the model for a list of recipe titles and have it label each one with a popularity grade:
*/

// [CODE STARTS]
gradedRecipeSchema = {
  type: "object",
  properties: {
    recipe_name: { type: "string" },
    grade: {
      type: "string",
      enum: ["a+", "a", "b", "c", "d", "f"]
    }
  },
  required: ["recipe_name", "grade"]
};

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "List about 10 cookie recipes, grade them based on popularity",
  config: {
    responseMimeType: "application/json",
    responseSchema: {
      type: "array",
      items: gradedRecipeSchema
    }
  }
});

console.log("```\n",response.text,"\n```")
// [CODE ENDS]

/* Output Sample

```
[
  {
    "grade": "a+",
    "recipe_name": "Chocolate Chip Cookies"
  },
  {
    "grade": "a",
    "recipe_name": "Peanut Butter Cookies"
  },
  {
    "grade": "a",
    "recipe_name": "Oatmeal Raisin Cookies"
  },
  {
    "grade": "a+",
    "recipe_name": "Sugar Cookies"
  },
  {
    "grade": "b",
    "recipe_name": "Snickerdoodle Cookies"
  },
  {
    "grade": "b",
    "recipe_name": "Gingerbread Cookies"
  },
  {
    "grade": "c",
    "recipe_name": "Shortbread Cookies"
  },
  {
    "grade": "c",
    "recipe_name": "Macarons"
  },
  {
    "grade": "b",
    "recipe_name": "Molasses Cookies"
  },
  {
    "grade": "a",
    "recipe_name": "No-Bake Cookies"
  }
] 
```

*/

/* Markdown (render)
## Next Steps
### Useful API references:

Check the [structured output](https://ai.google.dev/gemini-api/docs/structured-output) documentation or the [`GenerationConfig`](https://ai.google.dev/api/generate-content#generationconfig) API reference for more details.

### Related examples

* The constrained output is used in the [Text summarization](https://github.com/google-gemini/cookbook/blob/main/examples/json_capabilities/Text_Summarization.ipynb) example to provide the model a format to summarize a story (genre, characters, etc...)
* The [Object detection](https://github.com/google-gemini/cookbook/blob/main/examples/Object_detection.ipynb) examples are using the JSON constrained output to uniformize the output of the detection.

### Continue your discovery of the Gemini API

Structured output is not the only way to guide model behavior. [Function calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb) and [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb) are other ways to expand your model's capabilities by integrating external functions or letting it execute code dynamically.
*/