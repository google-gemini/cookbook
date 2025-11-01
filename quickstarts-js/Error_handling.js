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
# Gemini API: Error handling
*/

/* Markdown (render)
This notebook demonstrates strategies for handling common errors you might encounter when working with the Gemini API:

*   **Transient Errors:** Temporary failures due to network issues, server overload, etc.
*   **Rate Limits:** Restrictions on the number of requests you can make within a certain timeframe.
*   **Timeouts:** When an API call takes too long to complete.

You have two main approaches to explore:

1.  **Automatic retries:** A simple way to retry requests when they fail due to transient errors.
2.  **Manual backoff and retry:** A more customizable approach that provides finer control over retry behavior.


**Gemini Rate Limits**

The default rate limits for different Gemini models are outlined in the [Gemini API model documentation](https://ai.google.dev/gemini-api/docs/models/gemini#model-variations). If your application requires a higher quota, consider [requesting a rate limit increase](https://ai.google.dev/gemini-api/docs/quota).
*/

/* Markdown (render)
### API Key Configuration
To ensure security, avoid hardcoding the API key in frontend code. Instead, set it as an environment variable on the server or local machine.
When using the Gemini API client libraries, the key will be automatically detected if set as either `GEMINI_API_KEY` or `GOOGLE_API_KEY`. If both are set, `GOOGLE_API_KEY` takes precedence.
For instructions on setting environment variables, see the official documentation: [Set API Key as Environment Variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)
*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
// [CODE ENDS]

/* Markdown (render)
### Automatic retries

The Gemini API's client library offers built-in retry mechanisms for handling transient errors. You can enable this feature by using the `request_options` argument with API calls like `generate_content`, `generate_answer`, `embed_content`, and `generate_content_async`.

**Advantages:**

* **Simplicity:** Requires minimal code changes for significant reliability gains.
* **Robust:** Effectively addresses most transient errors without additional logic.

**Customize retry behavior:**

Use these settings in [`retry`](https://googleapis.dev/python/google-api-core/latest/retry.html) to customize retry behavior:

* `predicate`:  (callable) Determines if an exception is retryable. Default: [`if_transient_error`](https://github.com/googleapis/python-api-core/blob/main/google/api_core/retry/retry_base.py#L75C4-L75C13)
* `initial`: (float) Initial delay in seconds before the first retry. Default: `1.0`
* `maximum`: (float) Maximum delay in seconds between retries. Default: `60.0`
* `multiplier`: (float) Factor by which the delay increases after each retry. Default: `2.0`
* `timeout`: (float) Total retry duration in seconds. Default: `120.0`
*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash";
prompt = "Write a story about a magic backpack.";

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: prompt,
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample
Elara wasn’t looking for magic. She was looking for a backpack. Her old one, affectionately nicknamed “The Beast,” had finally given up the ghost, its seams ripped and its zipper permanently jammed. So, she found herself in Mrs. Willowby’s Oddity Emporium, a place smelling of mothballs and forgotten dreams.

The backpack in question was tucked away in a dusty corner, almost hidden behind a taxidermied two-headed duck. It was made of a deep indigo fabric, embroidered with silver constellations that shimmered faintly even in the dim light. It was perfect.

“That one’s been here for ages,” Mrs. Willowby croaked, dusting it off with a flourish. “Nobody seems to want it.”

Elara didn't care. She paid the paltry sum, slung the backpack over her shoulder, and hurried home.

The first sign that something was amiss came the next day. Packing for school, Elara discovered the backpack was inexplicably larger inside than out. She could fit her textbooks, lunch, a bulky art project, and still have room for more. It was like a miniature, indigo TARDIS.

Then came the apple. She’d absentmindedly tossed an apple into the backpack, then spent the next five minutes searching for it. When she finally gave up, she pulled out her history book – and the apple was perched perfectly on top, gleaming as if freshly polished.

Over the next few weeks, Elara discovered the backpack’s magic was more whimsical than powerful. It couldn't grant wishes or transport her to other dimensions, but it could certainly make life interesting. It could produce the exact right color of paint she needed for her art project, always perfectly blended. It could conjure a warm scarf on a chilly day. It could even, on one particularly stressful day, produce a miniature, purring kitten that promptly curled up in her lap.

The backpack seemed to respond to Elara’s needs, often anticipating them. If she was bored, it would produce a book she'd been meaning to read. If she was nervous about a test, it would contain a perfectly sharpened pencil and a reassuring note, scrawled in elegant script she didn't recognize.

But the magic wasn't always predictable. One day, she reached in for her math textbook and pulled out a handful of sand, complete with a tiny, brightly colored seashell. Another time, expecting her lunch, she found a single, perfectly ripe strawberry.

Elara kept the backpack's magic a secret. It was her little secret, her personal quirk in a world that often felt mundane. She loved the element of surprise, the anticipation of what the backpack would conjure next.

One day, however, she overheard a girl in her class, Maya, crying in the hallway. Maya had lost her grandmother's locket, a tiny silver heart that was her most treasured possession. Elara hesitated. Could the backpack help?

She found Maya sitting on a bench, tears streaming down her face. "Maya," she said softly, "I... I might be able to help."

Reluctantly, Elara explained about the backpack. Maya looked at her with a mixture of disbelief and hope. Elara unzipped the backpack, her heart pounding. She closed her eyes, pictured the locket, the delicate silver chain, the intricate heart shape. She reached inside.

Her fingers brushed against something cold and smooth. She pulled it out. It was the locket.

Maya gasped, her eyes wide with wonder. "That's it! That's my locket!" She snatched it from Elara's hand and clutched it to her chest. "Thank you," she whispered, tears still falling, but now tears of joy.

From that day on, Elara didn't keep the backpack's magic a secret. She didn't advertise it, but when someone needed help, she offered what she could. A lost homework assignment, a forgotten umbrella, a comforting word – the backpack seemed to know exactly what was needed.

The indigo backpack wasn't just a bag; it was a symbol of hope, a reminder that even in the most ordinary of lives, a little bit of magic could make all the difference. And Elara, the girl who had simply been looking for a replacement for "The Beast," had become something much more – a bearer of magic, and a friend to those who needed it most. And she knew, with a certainty that warmed her from the inside out, that the magic of the backpack was only just beginning.
*/

/* Markdown (render)
### Manually increase timeout when responses take time

If you encounter `TimeoutError` or similar errors, meaning an API call exceeds the default timeout, you can manually adjust it by defining `timeout` in the `requestOptions` argument.
*/

// [CODE STARTS]
prompt = "Write a story about a magic backpack.";

// Increase timeout to 15 minutes (900000 milliseconds)
const requestOptions = {
    timeout: 900000,
};

const response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: prompt,
    requestOptions: requestOptions,
});

console.log(response);
// [CODE ENDS]

/* Output Sample
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Flora had always been unremarkable. Brown hair, brown eyes, perpetually lost in a book. Even her backpack, a drab canvas thing she'd inherited from her older brother, screamed \"invisible.\" Until, one Tuesday morning, it didn't.\n\nShe was rushing to catch the bus, her fingers fumbling with the zipper of the aforementioned backpack, when it refused to budge. Frustrated, she yanked harder. There was a ripping sound, but instead of canvas tearing, a shimmering, iridescent light spilled out.\n\nFlora gasped. The inside of the backpack wasn't canvas anymore. It was… a swirling vortex of colours, like the aurora borealis compressed into a small space. Hesitantly, she reached in. Her fingers brushed against something soft, and she pulled it out.\n\nIt was a perfect, crimson apple, polished to a gleam. She hadn't packed an apple. She hadn't packed anything, actually, other than a crumpled textbook and a half-eaten bag of chips. She shrugged and took a bite.\n\nThe apple exploded in her mouth with a flavour she'd never experienced. It tasted of sunshine, laughter, and the comforting smell of rain on dry earth. She felt a surge of energy, of boundless possibility.\n\nFrom that day on, Flora's life was anything but unremarkable. The backpack, it turned out, was magical. Whatever she needed, the backpack provided. Not necessarily what she *wanted*, but what she *needed*.\n\nOne day, facing a daunting math test, she reached in, hoping for a cheat sheet. Instead, she pulled out a skipping rope. Confused, she tucked it into her pocket. During the test, she felt a rising tide of anxiety. On impulse, she pulled out the rope and, ignoring the bewildered stares of her classmates, started skipping in the corner. The rhythm calmed her, cleared her head, and suddenly, the formulas clicked into place. She aced the test.\n\nAnother time, feeling lonely and ignored, she hoped for a new friend. The backpack gave her a packet of wildflower seeds. Disappointed, she almost tossed them aside. But then she remembered the empty patch of dirt behind the school. She planted the seeds, nurtured them, and soon, a riot of colours bloomed. Students, drawn to the vibrant flowers, started talking to her, helping her tend the garden. She found her community.\n\nThe backpack wasn't always easy. Sometimes, it gave her things she didn't understand or appreciate at first. A rusty key, a chipped teacup, a single, perfect feather. But each time, in its own strange way, the object taught her a lesson, filled a need she didn't even know she had.\n\nOne day, rummaging through the backpack for a pen, Flora found something unexpected: a small, leather-bound book. Its pages were blank, but the title was embossed in gold: \"The Unwritten Story.\"\n\nShe understood. The backpack wasn't just providing her with objects; it was providing her with opportunities, with the raw materials to build her own extraordinary life. It was up to her to write the story.\n\nFlora closed the book, a smile playing on her lips. She still had brown hair and brown eyes, and she still loved to read. But now, she carried herself with a newfound confidence, a spark of adventure in her eyes. She was no longer invisible. The magic backpack had helped her discover the magic within herself. And the greatest magic of all, she realised, was the power to create her own destiny, one chapter, one challenge, one adventure at a time."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": []
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 8,
    "candidatesTokenCount": 752,
    "totalTokenCount": 760
  }
}
*/

/* Markdown (render)
**Caution:**  While increasing timeouts can be helpful, be mindful of setting them too high, as this can delay error detection and potentially waste resources.
*/

/* Markdown (render)
### Manually implement backoff and retry with error handling

For finer control over retry behavior and error handling, you can use the [`retry`](https://googleapis.dev/python/google-api-core/latest/retry.html) library (or similar libraries like [`backoff`](https://pypi.org/project/backoff/) and [`tenacity`](https://tenacity.readthedocs.io/en/latest/)). This gives you precise control over retry strategies and allows you to handle specific types of errors differently.
*/

// [CODE STARTS]
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function generateWithRetry(prompt) {
  let retries = 3; // Max retries
  let backoff = 1000; // Initial delay in ms

  for (let i = 0; i < retries; i++) {
    try {
      const response = await ai.models.generateContent({
          model: MODEL_ID,
          contents: prompt,
      });
      return response;
    } catch (e) {
      console.log(`Attempt ${i + 1} failed. Retrying in ${backoff / 1000} seconds...`);
      if (i < retries - 1) {
        await delay(backoff);
        backoff *= 2; // Exponential backoff
      } else {
        console.error("All retry attempts failed.", e);
        throw e; // Re-throw the last error
      }
    }
  }
}

prompt = "Write a one-liner advertisement for magic backpack.";
response = await generateWithRetry(prompt);
console.log(response); 
// [CODE ENDS]

/* Output Sample
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Unzip endless possibilities with the Magic Backpack - more space, more adventure!\n"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": []
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 10,
    "candidatesTokenCount": 16,
    "totalTokenCount": 26
  }
}
*/

/* Markdown (render)
### Test the error handling with retry mechanism

To validate that your error handling and retry mechanism work as intended, you can simulate a failure. The following function is designed to fail on its first attempt and then succeed on the retry.
*/

// [CODE STARTS]
let callCounter = 0;

const delaySim = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function generateContentFirstFail(prompt) {
    let retries = 3;
    let backoff = 1000;

    for (let i = 0; i < retries; i++) {
        try {
            callCounter++;
            if (callCounter === 1) {
                throw new Error("Simulated Service Unavailable");
            }

            const response = await ai.models.generateContent({
                model: MODEL_ID,
                contents: prompt,
            });
            return response.text; 
        } catch (e) {
            console.log(`Error: ${e.message}`);
            if (i < retries - 1) {
                console.log(`Retrying in ${backoff / 1000} seconds...`);
                await delaySim(backoff);
                backoff *= 2;
            } else {
                console.error("All retry attempts failed.");
                throw e;
            }
        }
    }
}

prompt = "Write a one-liner advertisement for magic backpack.";
response = await generateContentFirstFail(prompt);
console.log(response);
// [CODE ENDS]

/* Output Sample
Error: Simulated Service Unavailable
Retrying in 1 seconds...
Unzip the impossible with the Magic Backpack - where adventure always fits!
*/