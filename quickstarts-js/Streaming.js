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
# Gemini API: Streaming Quickstart

This notebook demonstrates streaming in the Javascript SDK. By default, the Javascript SDK returns a response after the model completes the entire generation process. You can also stream the response as it is being generated, and the model will return chunks of the response as soon as they are generated.

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
## Generating streaming responses

To stream responses, use [`Models.generateContentStream`](https://googleapis.github.io/js-genai/release_docs/classes/models.Models.html#generatecontentstream).
*/

// [CODE STARTS]
response = await ai.models.generateContentStream({
  model: MODEL_ID,
  contents: "Tell me a story in 300 words.",
});

for await (const chunk of response) {
  console.log(chunk.text);
  console.log("_".repeat(80));
}
// [CODE ENDS]

/* Output Sample

Elara lived in a village cradled by the Whisperwood, a forest the elders warned against. &amp;quot;Lost souls wander there,&amp;quot; they&amp;#x27;d croak, &amp;quot;lured by the Song of the Forgotten Spring.&amp;quot; But Elara heard no despair;

________________________________________________________________________________

 only an insistent hum, a melody only she seemed to catch. It spoke of ancient secrets, not danger.

One dawn, while the village still slept, she slipped past the carved protective gates. The air immediately thickened, smelling of damp

________________________________________________________________________________

 earth and something sweet, like forgotten honey. Sunlight dappled through the impossibly tall canopy, painting shifting mosaics on the forest floor. Birds sheÃ¢â‚¬â„¢d never seen flitted between branches, their calls richer, more complex than those in her

________________________________________________________________________________

 garden.

She followed the hum, deeper now, a gentle vibration in her chest. Twisting vines formed archways, leading her further into a green cathedral. The path narrowed, then opened abruptly into a clearing bathed in an otherworldly luminescence

________________________________________________________________________________

. In its center, an enormous willow wept shimmering leaves into a pool of water so still and clear, it reflected the sky like a perfect, inverted mirror.

This was no forgotten spring, but a living heart. The &amp;#x27;song&amp;#x27;

________________________________________________________________________________

 was the rustle of the willowÃ¢â‚¬â„¢s leaves, the gentle gurgle of the water, the quiet hum of life itself. Elara knelt, dipping her fingers into the cool surface. A wave of profound peace washed over her,

________________________________________________________________________________

 an understanding that transcended words. The magic wasn&amp;#x27;t in a spell, but in the quiet, undeniable connection to something vast and ancient.

She stayed until the sun began its descent, then turned back, the hum now a part

________________________________________________________________________________

 of her own pulse. The village still slept under its protective gaze, oblivious to the world sheÃ¢â‚¬â„¢d found. Elara carried the WhisperwoodÃ¢â‚¬â„¢s secret, not as a burden, but as a silent, shimmering jewel in her soul

________________________________________________________________________________

. She knew she would return.

________________________________________________________________________________

*/

/* Markdown (render)
## Handle streaming responses asynchronously

The `generateContentStream` function returns a non-blocking stream, allowing your application to remain responsive and perform other tasks while the AI response is being generated.

This example demonstrates this by running a simple timer (somethingElse) concurrently with the `generateContentStream` call. You will see the timer's `=======not blocked!=======` messages print interleaved with the story chunks, showcasing that the code isn't frozen while waiting for the AI response.
*/

// [CODE STARTS]
async function getResponse() {
  const response = await ai.models.generateContentStream({
    model: MODEL_ID,
    contents: "Tell me a story in 300 words.",
  });


  for await (const chunk of response) {
    if (chunk.text) {
      console.log(chunk.text);
    }
    console.log("_".repeat(80));
  }
  
}

async function somethingElse() {
  for (let i = 0; i < 5; i++) {
    await new Promise((resolve) => setTimeout(resolve, 6000));
    console.log("==========not blocked!==========");
  }
  
}

await Promise.all([getResponse(), somethingElse()]);
// [CODE ENDS]

/* Output Sample

==========not blocked!==========

==========not blocked!==========

Elara loved the quiet hum of the library after closing. Tonight, the silence was particularly deep as she made her rounds through the rare books section, a ritual she cherished. Dust motes danced in the last slivers of twilight filtering through the high arched

________________________________________________________________________________

 windows.

She was securing the ancient vellum-bound folios when a small, leather-covered volume, almost hidden, caught her eye. It wasn&#x27;t particularly grand â€“ a modest botanical guide from the late 17th

________________________________________________________________________________

 century. As she reached for it, her fingers brushed its spine, and it tumbled from the shelf, landing open on the polished oak table with a soft thud.

Elara gasped. There, pressed between brittle, yellowed pages

________________________________________________________________________________

, was a flower. Not a faded, desiccated ghost of a bloom, but a vivid, impossibly fresh violet. Its petals were a deep, velvety purple, and a single dewdrop seemed to cling to its soft green leaf,

________________________________________________________________________________

 glistening as if just plucked from a morning garden. A faint, sweet fragrance, distinctly reminiscent of spring rain and earthy soil, wafted up, too subtle to be real, yet undeniably present.

She leaned closer, her breath held.

________________________________________________________________________________

 The flower seemed to pulse with a gentle luminescence, a quiet heartbeat against the backdrop of ancient text. Cautiously, Elara extended a finger. Just before she touched it, a tiny shimmer, like heat rising from pavement on a summer

________________________________________________________________________________

==========not blocked!==========

 day, rippled across its surface.

She pulled her hand back, heart pounding. This wasn&#x27;t preservation; it wasâ€¦ life. A forgotten miracle suspended in time. Carefully, with hands that trembled slightly, she closed the book

________________________________________________________________________________

. The scent lingered on her fingertips, a whisper of a secret.

Elara placed the botanical guide back on its shelf, a new respect for its quiet power. The library was no longer just a repository of knowledge; it held mysteries

________________________________________________________________________________

==========not blocked!==========

 that defied explanation, living wonders hidden in plain sight. She locked the heavy oak doors, the image of the vibrant violet burning bright in her mind. Tomorrow, she knew, her first stop would be that particular shelf, eager to see if

________________________________________________________________________________

 the impossible bloom still graced its pages, waiting to share its timeless secret.

________________________________________________________________________________

==========not blocked!==========

*/