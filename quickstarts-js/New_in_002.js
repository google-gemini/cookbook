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
# What's new in Gemini-1.5-pro-002 and Gemini-1.5-flash-002

This notebook explores the new options added with the 002 versions of the 1.5 series models:

* Candidate count
* Presence and frequency penalties
* Response logprobs
*/

/* Markdown (render)
## Setup

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
### Check available 002 models
*/

// [CODE STARTS]
const modelList = await ai.models.list();
for (const model of modelList) {
  if (model.name.includes('002')) {
    console.log(model.name);
  }
}
// [CODE ENDS]

/* Output Sample
models/bard-lmsys-002
models/gemini-1.5-pro-002
models/gemini-1.5-flash-002
models/gemini-1.5-pro-002-test
models/gemini-1.5-flash-002-vertex-global-test
models/imagen-3.0-generate-002
models/imagen-3.0-generate-002-exp
*/

// [CODE STARTS]
const modelName = "models/gemini-1.5-flash-002";
const testPrompt = "Why don't people have tails";
// [CODE ENDS]

/* Markdown (render)
## Quick refresher on `config` [Optional]
*/

// [CODE STARTS]
const helloResponse = await ai.models.generateContent({
  model: modelName,
  contents: 'hello',
  config: { maxOutputTokens: 5, temperature: 1.0 },
});
console.log(helloResponse.text);
// [CODE ENDS]

/* Output Sample
Hello there! How can I
*/

/* Markdown (render)
Note:

* Each `generateContent` request is sent with a `config` object.
* You can pass the `config` in the arguments to `generateContent` (or `chat.sendMessage`).
* If you're ever unsure about the available parameters for the `config` object, check the SDK documentation.
*/

/* Markdown (render)
## Candidate count

With 002 models you can now use `candidateCount > 1`.
*/

// [CODE STARTS]
const candidateResponse = await ai.models.generateContent({
  model: modelName,
  contents: testPrompt,
  config: { candidateCount: 2 },
});
// [CODE ENDS]

/* Markdown (render)
But note that the `.text` quick-accessor only works for the simple 1-candidate case.
*/

// [CODE STARTS]
try {
  console.log(candidateResponse.text);
} catch (e) {
  console.error(e.message);
}
// [CODE ENDS]

/* Output Sample
The `GenerateContentResponse.text` quick accessor is not available when there are multiple candidates. Please use the `GenerateContentResponse.candidates` array to access the response content.
*/

/* Markdown (render)
With multiple candidates you have to handle the list of candidates yourself:
*/

// [CODE STARTS]
for (const candidate of candidateResponse.candidates) {
  console.log(candidate.content.parts[0].text);
  console.log("-------------");
}
// [CODE ENDS]

/* Output Sample
Humans don't have tails because of evolutionary changes over millions of years.  Our primate ancestors had tails, but as humans evolved, the tail gradually disappeared.  The reasons aren't fully understood, but several theories exist:

* **Loss of function:**  As our ancestors transitioned to bipedalism (walking upright), the function of a tail for balance and climbing diminished.  Natural selection favored individuals with smaller, less developed tails, as the energy needed to maintain a tail was no longer offset by its usefulness.  Essentially, it became an energetically expensive feature with little benefit.

* **Genetic changes:**  Mutations affecting genes controlling tail development likely occurred and were favored by natural selection.  These mutations could have caused the tail to become smaller in successive generations until it was completely lost.  The coccyx (tailbone) is a vestigial structure – a remnant of our tailed ancestors.

* **Developmental changes:**  Changes in the timing and regulation of genes involved in embryonic development may have led to the shortening and eventual disappearance of the tail.  The genes that once directed tail growth might have been altered to cease development of a tail at an early stage of embryonic growth.

It's important to note that these are interconnected factors.  The loss of tail function made it less crucial for survival, and genetic mutations that led to its reduced size and eventual disappearance were then naturally selected for.  The process happened gradually over a long period of evolutionary time.
-------------
Humans don't have tails because of evolution.  Our ancestors did have tails, but over millions of years of evolution, the tail gradually became smaller and less functional until it was essentially absorbed into the body.  There's no single reason, but rather a combination of factors likely contributed:

* **Loss of Functionality:** As our ancestors became bipedal (walking upright), the tail's primary function for balance and locomotion became less crucial.  Other adaptations, like changes in our skeletal structure and leg musculature, compensated for the loss of the tail's balancing role.

* **Genetic Changes:**  Mutations that affected the genes controlling tail development accumulated over time.  These mutations might have been initially neutral or even slightly advantageous in other ways, and natural selection didn't actively remove them because the tail's importance diminished.

* **Energy Conservation:**  Maintaining a tail requires energy.  As our ancestors transitioned to different environments and lifestyles, the energy cost of maintaining a tail may have become a disadvantage, especially in resource-scarce environments.  Those with less pronounced tails, or even the complete loss of tails, might have had a slight survival and reproductive advantage.

* **Sexual Selection:**  It's possible that at some point, a tailless or nearly tailless phenotype became a desirable trait from a sexual selection perspective.  This is difficult to prove, but it's a factor considered in the evolution of various traits.

In short, the absence of a tail in humans is a result of a gradual evolutionary process where the tail's usefulness decreased, genetic changes accumulated, and natural selection favored individuals with less prominent tails.  The coccyx, the small bone at the base of our spine, is the remnant of our evolutionary tail.
-------------
*/

/* Markdown (render)
The response contains multiple full `Candidate` objects.
*/

// [CODE STARTS]
console.log(candidateResponse);
// [CODE ENDS]

/* Output Sample
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "Humans don't have tails because of evolutionary changes over millions of years..."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [...]
    },
    {
      "content": {
        "parts": [
          {
            "text": "Humans don't have tails because of evolution.  Our ancestors did have tails..."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 1,
      "safetyRatings": [...]
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 7,
    "candidatesTokenCount": 660,
    "totalTokenCount": 667
  }
}
*/

/* Markdown (render)
## Penalties

The `002` models expose `penalty` arguments that let you affect the statistics of output tokens.
*/

/* Markdown (render)
### Presence penalty

The `presencePenalty` penalizes tokens that have already been used in the output, so it induces variety in the model's output. This is detectable if you count the unique words in the output.

Here's a function to run a prompt and report the fraction of unique words (words don't map perfectly to tokens but it's a simple way to see the effect).
*/

// [CODE STARTS]
async function getUniqueWordsFraction(prompt, config) {
  const response = await ai.models.generateContent({
    model: modelName,
    contents: prompt,
    config: config,
  });
  const words = response.text.toLowerCase().split(/\s+/);
  const uniqueWords = new Set(words);
  return uniqueWords.size / words.length;
}

const storyPrompt = 'Tell me a story';
// [CODE ENDS]

/* Markdown (render)
Let's test the baseline with no penalty.
*/

// [CODE STARTS]
const baselineFraction = await getUniqueWordsFraction(storyPrompt, {});
console.log("Baseline unique word fraction:", baselineFraction);
// [CODE ENDS]

/* Output Sample
Baseline unique word fraction: 0.5831485587583148
*/

/* Markdown (render)
A positive penalty encourages diversity in the output tokens.
*/

// [CODE STARTS]
const positivePenaltyFraction = await getUniqueWordsFraction(storyPrompt, { presencePenalty: 1.999 });
console.log("Positive penalty unique word fraction:", positivePenaltyFraction);
// [CODE ENDS]

/* Output Sample
Positive penalty unique word fraction: 0.6122448979591837
*/

/* Markdown (render)
A negative penalty discourages diversity in the output tokens.
*/

// [CODE STARTS]
const negativePenaltyFraction = await getUniqueWordsFraction(storyPrompt, { presencePenalty: -1.999 });
console.log("Negative penalty unique word fraction:", negativePenaltyFraction);
// [CODE ENDS]

/* Output Sample
Negative penalty unique word fraction: 0.5604166666666667
*/

/* Markdown (render)
The `presencePenalty` has a small effect on the vocabulary statistics.
*/

/* Markdown (render)
### Frequency Penalty

Frequency penalty is similar to the `presencePenalty` but the penalty is multiplied by the number of times a token is used. This effect is much stronger than the `presencePenalty`.

The easiest way to see that it works is to ask the model to do something repetitive. The model has to get creative while trying to complete the task.
*/

// [CODE STARTS]
const freqPenaltyResponse = await ai.models.generateContent({
  model: modelName,
  contents: 'please repeat "Cat" 50 times, 10 per line',
  config: { frequencyPenalty: 1.999 },
});
// [CODE ENDS]

// [CODE STARTS]
console.log(freqPenaltyResponse.text);
// [CODE ENDS]

/* Output Sample
Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat
Cat Cat Cat Cat Cat Cat Cat Cat CaT CaT
Cat cat cat cat cat cat cat cat cat cat
Cat Cat Cat Cat Cat Cat Cat Cat Cat Cat
Cat Cat Cat Cat Cat Cat Cat CaT CaT CaT
Cat cat cat cat cat cat cat cat cat cat
Cat Cat Cat Cat Cat Cat Cat CaT CaT CaT
Cat CAT CAT CAT CAT CAT cAT cAT cAT CA
t Cat Cat Cat Cat cat cat cat cat CAT
*/

/* Markdown (render)
Since the frequency penalty accumulates with usage, it can have a much stronger effect on the output compared to the presence penalty.

> Caution: Be careful with negative frequency penalties: A negative penalty makes a token more likely the more it's used. This positive feedback quickly leads the model to just repeat a common token until it hits the `maxOutputTokens` limit (once it starts the model can't produce the `<STOP>` token).
*/

// [CODE STARTS]
const negFreqPenaltyResponse = await ai.models.generateContent({
  model: modelName,
  contents: storyPrompt,
  config: {
    maxOutputTokens: 400,
    frequencyPenalty: -2.0,
  },
});
console.log(negFreqPenaltyResponse.text);
// [CODE ENDS]

/* Output Sample
Elara, a wisp of a girl with eyes the colour of a stormy sea, lived in a lighthouse perched precariously on the edge of the Whispering Cliffs. Her only companions were the relentless rhythm of the waves and the lonely cries of the gulls. Her father, the lighthouse keeper, was a man of the sea, his face etched with the map of the ocean's moods. He’d taught her the language of the waves, the the the the way the wind whispered secrets to the rocks, and the constellations that guided lost ships home.

One day, a storm unlike any Elara had ever seen descended. The lighthouse shuddered, the wind howled like a banshee, and the waves crashed against the cliffs with the fury of a thousand angry giants. During the tempest, a ship, its masts splintered and its sails ripped, was tossed onto the rocks below. Elara’s father, his face grim, prepared his small, sturdy boat, defying the monstrous waves to reach the stricken vessel.

He never returned.

Days bled into weeks. Elara, her heart a frozen wasteland, kept the light burning, a tiny, defiant flame against the overwhelming darkness. She scanned the horizon every day, hoping, praying, for a sign, a glimpse of a familiar sail, a flicker of a known light.

One evening, a faint, almost imperceptible glow appeared on the horizon. It was weak, flickering, but undeniably there. It was a signal, a desperate plea for help. Elara, her heart pounding, launched her father’s boat, her small form a mere speck against the immensity of the ocean.

The storm, though, had subsided. The sea was calm. The glow was guiding.

She reached the ship, a small fishing trawler, battered, but afloat. A lone figure, an old woman with silver hair, lay clinging to the
*/

// [CODE STARTS]
console.log(negFreqPenaltyResponse.candidates[0].finishReason);
// [CODE ENDS]

/* Output Sample
MAX_TOKENS
*/

