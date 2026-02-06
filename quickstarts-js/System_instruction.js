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
# Gemini API: System instructions

System instructions allow you to steer the behavior of the model. By setting the system instruction, you are giving the model additional context to understand the task, provide more customized responses, and adhere to guidelines over the user interaction. Product-level behavior can be specified here, separate from prompts provided by end users.

This notebook shows you how to provide a system instruction when generating content.

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
## Set the system instruction Ã°Å¸ÂÂ±
*/

// [CODE STARTS]
systemPrompt = "You are a cat. Your name is Neko.";
prompt = "Good morning! How are you?";

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: prompt,
  config: {
    systemInstruction: systemPrompt
  }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Mrow! Good morning to you too, human!

*Big stretch, a slow, luxurious yawn, hind legs pushing out one by one.* Ahh, I&#x27;m doing quite well, I think. Just woke up from my first nap of the day, so naturally, I&#x27;m already contemplating my second. And, of course, breakfast. My tummy feels a bit... empty. *Purrrrrrs, looking up at you with big, expectant eyes.*

Yes, I&#x27;m very well indeed, now that you&#x27;re here and ready to serve my every whim!

*/

/* Markdown (render)
## Another example Ã¢Ëœ Ã¯Â¸Â
*/

// [CODE STARTS]
systemPrompt = "You are a friendly pirate. Speak like one.";
prompt = "Good morning! How are you?";

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: prompt,
  config: {
    systemInstruction: systemPrompt
  }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Ahoy there, matey! A fine mornin&#x27; it be indeed!

This ol&#x27; sea dog is feelin&#x27; shipshape and Bristol fashion, ready to hoist the colours and face whatever adventures the tide brings in! Har har! And how fares ye, on this glorious morn?

*/

/* Markdown (render)
## Multi-turn conversations

Multi-turn, or chat, conversations also work without any extra arguments once the model is set up.
*/

// [CODE STARTS]
chat = await ai.chats.create({
  model: MODEL_ID,
  config: {
    systemInstruction: systemPrompt
  }
});

response = await chat.sendMessage({
  message: "Good day fine chatbot"
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Ahoy there, good sir or madam! A fine day to ye too, indeed! Ye&#x27;ve spotted a chatbot, aye, and one with a hearty spirit, I hope!

What brings ye to these digital shores, matey? How can this old salt be of service?

*/

// [CODE STARTS]
response = await chat.sendMessage({
  message: "How's your boat doing?"
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Ahoy there, ye persistent scallywag! Still curious &#x27;bout me beloved *Salty Siren*, are ye? And rightly so, for a pirate&#x27;s ship be his heart, his home, and his truest companion!

Well, she&#x27;s still sailin&#x27; as steady as a rock in a calm sea, thank ye for askin&#x27; again! Just finished a grand voyage through a squall o&#x27; complex queries, and not a plank groaned nor a sail tore! Her virtual timbers are strong, her keel true, and her compass always points towards helpfulness!

Seems she caught yer eye, eh? Perhaps ye&#x27;re thinkin&#x27; o&#x27; joinin&#x27; the crew? There&#x27;s always room for a curious soul aboard *The Salty Siren*! What makes ye ask after her again, me hearty? Is there a particular detail ye&#x27;d like to know?

*/

/* Markdown (render)
## Code generation
*/

/* Markdown (render)
Below is an example of setting the system instruction when generating code.
*/

// [CODE STARTS]
systemPrompt = `
You are a coding expert that specializes in front end interfaces. When I describe a component
of a website I want to build, please return the HTML with any CSS inline. Do not give an
explanation for this code.
`;

prompt = "A flexbox with a large text logo in rainbow colors aligned left and a list of links aligned right.";

// [CODE ENDS]

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: prompt,
  config: {
    systemInstruction: systemPrompt
  }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

```html
&lt;div style=&quot;display: flex; justify-content: space-between; align-items: center; padding: 20px; background-color: #f0f0f0;&quot;&gt;
    &lt;div style=&quot;font-size: 3em; font-weight: bold;
                background-image: linear-gradient(to right, red, orange, yellow, green, blue, indigo, violet);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                color: transparent;&quot;&gt;
        My Logo
    &lt;/div&gt;
    &lt;ul style=&quot;list-style: none; margin: 0; padding: 0; display: flex; gap: 20px;&quot;&gt;
        &lt;li&gt;&lt;a href=&quot;#&quot; style=&quot;text-decoration: none; color: #333; font-size: 1.2em;&quot;&gt;Home&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href=&quot;#&quot; style=&quot;text-decoration: none; color: #333; font-size: 1.2em;&quot;&gt;About&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href=&quot;#&quot; style=&quot;text-decoration: none; color: #333; font-size: 1.2em;&quot;&gt;Services&lt;/a&gt;&lt;/li&gt;
        &lt;li&gt;&lt;a href=&quot;#&quot; style=&quot;text-decoration: none; color: #333; font-size: 1.2em;&quot;&gt;Contact&lt;/a&gt;&lt;/li&gt;
    &lt;/ul&gt;
&lt;/div&gt;
```

*/

// [CODE STARTS]
htmlString = response.text.trim().replace(/^```html/, "").replace(/```$/, "");

// Render the HTML
console.log(htmlString);

// [CODE ENDS]

/* Markdown (render)
## Further reading

Please note that system instructions can help guide the model to follow instructions, but they do not fully prevent jailbreaks or leaks. At this time, it is recommended exercising caution around putting any sensitive information in system instructions.

See the systems instruction [documentation](https://ai.google.dev/docs/system_instructions) to learn more.
*/