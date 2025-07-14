/* Markdown (render)
# Gemini API: JSON Mode Quickstart


The Gemini API can be used to generate a JSON output if you set the schema that you would like to use.

Two methods are available. You can either set the desired output in the prompt or supply a schema to the model separately.


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
## Set your constrained output in the prompt

For this first example just describe the schema you want back in the prompt:

*/

// [CODE STARTS]
prompt = `
  List a few popular cookie recipes using this JSON schema:

  Recipe = {'recipe_name': str}
  Return: list[Recipe]
`
// [CODE ENDS]

/* Markdown (render)
Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](./Get_started_thinking.ipynb) for more details and in particular learn how to switch the thiking off).

Then activate JSON mode by specifying `respose_mime_type` in the `config` parameter:
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
    &quot;recipe_name&quot;: &quot;Chocolate Chip Cookies&quot;
  },
  {
    &quot;recipe_name&quot;: &quot;Oatmeal Raisin Cookies&quot;
  },
  {
    &quot;recipe_name&quot;: &quot;Peanut Butter Cookies&quot;
  },
  {
    &quot;recipe_name&quot;: &quot;Sugar Cookies&quot;
  }
] 
```

*/

/* Markdown (render)
## Supply the schema to the model directly

The newest models (1.5 and beyond) allow you to pass a schema object (or a python type equivalent) directly and the output will strictly follow that schema.

Following the same example as the previous section, here's that recipe type:
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
For this example you want a list of `Recipe` objects, so pass `list[Recipe]` to the `response_schema` field of the `config`.
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
    &quot;recipe_description&quot;: &quot;A crescent of delicate shortbread, infused with the warm embrace of autumnal pear and a whisper of exotic cardamom, culminating in a celestial experience.&quot;,
    &quot;recipe_ingredients&quot;: [&quot;Unsalted butter&quot;, &quot;All-purpose flour&quot;, &quot;Powdered sugar&quot;, &quot;Ripe pears&quot;, &quot;Ground cardamom&quot;, &quot;Vanilla bean paste&quot;],
    &quot;recipe_name&quot;: &quot;Celestial Spiced Pear &amp; Cardamom Crescent&quot;
  },
  {
    &quot;recipe_description&quot;: &quot;Rich, dark chocolate cookies with a molten espresso ganache heart, dusted with cocoa for an intensely decadent and sophisticated bite.&quot;,
    &quot;recipe_ingredients&quot;: [&quot;Dark cocoa powder&quot;, &quot;Unsalted butter&quot;, &quot;Granulated sugar&quot;, &quot;Eggs&quot;, &quot;All-purpose flour&quot;, &quot;Espresso powder&quot;, &quot;Heavy cream&quot;, &quot;Bittersweet chocolate&quot;],
    &quot;recipe_name&quot;: &quot;Midnight Velvet Espresso Truffle Buttons&quot;
  },
  {
    &quot;recipe_description&quot;: &quot;Crisp, golden honey shortbread adorned with delicate crystallized lavender florets, offering a sweet, aromatic, and truly ethereal indulgence.&quot;,
    &quot;recipe_ingredients&quot;: [&quot;Unsalted butter&quot;, &quot;All-purpose flour&quot;, &quot;Granulated sugar&quot;, &quot;Honey&quot;, &quot;Culinary lavender&quot;, &quot;Egg yolk&quot;, &quot;Sea salt&quot;],
    &quot;recipe_name&quot;: &quot;Lavender Honeycomb Dreams&quot;
  }
] 
```

*/

/* Markdown (render)
It is the recommended method if you're using a compatible model.
*/

/* Markdown (render)
## Next Steps
### Useful API references:

Check the [structured ouput](https://ai.google.dev/gemini-api/docs/structured-output) documentation or the [`GenerationConfig`](https://ai.google.dev/api/generate-content#generationconfig) API reference for more details

### Related examples

* The constrained output is used in the [Text summarization](https://github.com/google-gemini/cookbook/blob/main/examples/json_capabilities/Text_Summarization.ipynb) example to provide the model a format to summarize a story (genre, characters, etc...)
* The [Object detection](https://github.com/google-gemini/cookbook/blob/main/examples/Object_detection.ipynb) examples are using the JSON constrained output to uniiformize the output of the detection.

### Continue your discovery of the Gemini API

JSON is not the only way to constrain the output of the model, you can also use an [Enum](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Enum.ipynb). [Function calling](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb) and [Code execution](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Code_Execution.ipynb) are other ways to enhance your model by either using your own functions or by letting the model write and run them.
*/