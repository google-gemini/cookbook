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
# Use Gemini thinking

[Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-preview-04-17) and [Gemini 2.5 Pro](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-pro-preview-06-05) are models that are trained to do a [thinking process](https://ai.google.dev/gemini-api/docs/thinking-mode) (or reasoning) before getting to a final answer. As a result,
those models are capable of stronger reasoning capabilities in its responses than previous models.

You'll see examples of those reasoning capabilities with [code understanding](#scrollTo=GAa7sCD7tuMW), [geometry](#scrollTo=ADiJV-fFyjRe) and [math](#scrollTo=EXPPWpt6ttJZ) problems.

As you will see, the model is exposing its thoughts so you can have a look at its reasoning and how it did reach its conclusions.

## Understanding the thinking models

[Gemini 2.5 models](https://ai.google.dev/gemini-api/docs/thinking) are optimized for complex tasks that need multiple rounds of strategyzing and iteratively solving.

[Gemini 2.5 Flash](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-preview-04-17) in particular, brings the flexibility of using `thinking_budget` - a parameter
that offers fine-grained control over the maximum number of tokens a model can generate while thinking. Alternatively, you can designate a precise token allowance for the
"thinking" stage through the adjusment of the `thinking_budget` parameter. This allowance can vary between 0 and 24576 tokens for 2.5 Flash.

For more information about all Gemini models, check the [documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for extended information on each of them.

On this notebook all examples are using `Gemini 2.5 Pro` and `Gemini 2.5 Flash` with the new `thinking_budget` parameter. For more information about using the `thinking_budget` with the Gemini thinking model, check the [documentation](https://ai.google.dev/gemini-api/docs/thinking).

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
## Using the thinking models

Here are some quite complex examples of what Gemini thinking models can solve.

In each of them you can select different models to see how this new model compares to its predecesors.

In some cases, you'll still get the good answer from the other models, in that case, re-run it a couple of times and you'll see that Gemini thinking models are more consistent thanks to their thinking step.
*/

/* Markdown (render)
### Using adaptive thinking

You can start by asking the model to explain a concept and see how it does reasoning before answering.

Starting with the adaptive `thinking_budget` - which is the default when you don't specify a budget - the model will dynamically adjust the budget based on the complexity of the request.

The animal it should find is a [**Platipus**](https://en.wikipedia.org/wiki/Platypus), but as you'll see it is not the first answer it thinks of depending on how much thinking it does.
*/

// [CODE STARTS]
prompt = `
    You are playing the 20 question game. You know that what you are looking for
    is an aquatic mammal that doesn't live in the sea, is venomous and that's
    smaller than a cat. What could that be and how could you make sure?
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

This is a tricky one, and there&#x27;s actually **one excellent candidate** and another less commonly known but valid one!

## What could that be?

The most likely answer, fitting all criteria, is the **Platypus**.

Let&#x27;s break down why:

1.  **Aquatic Mammal:** Yes, the platypus (Ornithorhynchus anatinus) is a semi-aquatic mammal.
2.  **Doesn&#x27;t live in the sea:** It lives exclusively in freshwater rivers and lakes in eastern Australia and Tasmania.
3.  **Venomous:** This is the key unique characteristic! Male platypuses have a spur on each hind leg that can deliver a venomous cocktail, causing excruciating pain (though not generally lethal to humans).
4.  **Smaller than a cat:** An adult platypus typically ranges from 30-45 cm (12-18 inches) in body length, with a tail of about 10-15 cm (4-6 inches). This is indeed smaller than an average house cat.

**Another Possibility:**

While less iconic, certain species of **Water Shrew** (e.g., the Northern Short-tailed Shrew, although it&#x27;s not strictly &quot;water&quot; shrew, it&#x27;s a good example of venomous shrew) are also aquatic/semi-aquatic, venomous (via their saliva), and certainly smaller than a cat. However, the venom is usually less potent to humans and they are not typically thought of as &quot;aquatic mammals&quot; in the same vein as a platypus. Given the common knowledge, the platypus is the intended answer.

## How could you make sure?

To confirm it&#x27;s a Platypus in a 20-questions game, you could ask:

1.  **Does it lay eggs?** (The platypus is one of only five living monotreme species, all of which lay eggs.)
2.  **Does it have a bill like a duck?** (Its distinctive feature.)
3.  **Does it live in Australia?** (Its native habitat.)
4.  **Do only the males have the venomous part?** (True for the platypus&#x27;s spur.)
5.  **Does it have fur?** (To confirm it&#x27;s a mammal, not a reptile or amphibian.)
6.  **Does it use electroreception to find prey?** (A unique sensory ability of the platypus.)

*/

/* Markdown (render)
Looking to the response metadata, you can see not only the amount of tokens on your input and the amount of tokens used for the response, but also the amount of tokens used for the thinking step - As you can see here, the model used around 1400 tokens in the thinking steps:
*/

// [CODE STARTS]
console.log("Prompt tokens:", response.usageMetadata.promptTokenCount);
console.log("Thoughts tokens:", response.usageMetadata.thoughtsTokenCount);
console.log("Output tokens:", response.usageMetadata.candidatesTokenCount);
console.log("Total tokens:", response.usageMetadata.totalTokenCount);
// [CODE ENDS]

/* Output Sample

Prompt tokens: 62

Thoughts tokens: 1236

Output tokens: 535

Total tokens: 1833

*/

/* Markdown (render)
### Disabling the thinking steps

You can also disable the thinking steps by setting the `thinkingBudget` to 0. You'll see that in this case, the model doesn't think of the platipus as a possible answer.
*/

/* Markdown (render)
Now you can see that the response is faster as the model didn't perform any thinking step. Also you can see that no tokens were used for the thinking step:
*/

// [CODE STARTS]
prompt = `
    You are playing the 20 question game. You know that what you are looking for
    is an aquatic mammal that doesn't live in the sea, is venomous and that's
    smaller than a cat. What could that be and how could you make sure?
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
    config: {
        thinkingConfig: {
            thinkingBudget: 0, // disables internal "thoughts"
        },
    },
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

This is a fantastic and tricky riddle! Let&#x27;s break down the clues:

1.  **Aquatic Mammal:** This narrows it down significantly.
2.  **Doesn&#x27;t live in the sea:** This rules out most whales, dolphins, seals, manatees, etc., leaving freshwater or semi-aquatic mammals.
3.  **Venomous:** This is the *killer* clue, as venomous mammals are incredibly rare.
4.  **Smaller than a cat:** This helps with size.

Given these clues, the animal you are looking for is most likely a **Platypus**.

Let&#x27;s check the facts:

*   **Aquatic Mammal:** Yes, they are monotremes that spend a lot of time in freshwater.
*   **Doesn&#x27;t live in the sea:** Correct, they inhabit rivers and streams in eastern Australia and Tasmania.
*   **Venomous:** **YES!** This is the key. Male platypuses have a spur on their hind leg that can deliver venom. While not lethal to humans, it can cause severe pain and swelling.
*   **Smaller than a cat:** Adult platypuses are typically between 30-40 cm (12-16 inches) long, excluding the tail, which is indeed smaller than most domestic cats.

**How could you make sure?**

In a 20-question game, if you suspect it&#x27;s a platypus, you could ask questions like:

1.  **Does it lay eggs?** (Platypuses are one of only two egg-laying mammals)
2.  **Does it have a bill like a duck?**
3.  **Does it have fur?**
4.  **Is it native to Australia?**
5.  **Does the male have a venomous spur?** (This is the definitive &quot;gotcha&quot; question for the venomous mammal clue).
6.  **Does it live in freshwater rivers?**

By asking these questions, you could quickly confirm if your guess of a platypus is correct!

*/

/* Markdown (render)
Now you can see that the response is faster as the model didn't perform any thinking step. Also you can see that no tokens were used for the thinking step:
*/

// [CODE STARTS]
console.log("Prompt tokens:", response.usageMetadata.promptTokenCount);
console.log("Thoughts tokens:", response.usageMetadata.thoughtsTokenCount);
console.log("Output tokens:", response.usageMetadata.candidatesTokenCount);
console.log("Total tokens:", response.usageMetadata.totalTokenCount);
// [CODE ENDS]

/* Output Sample

Prompt tokens: 62

Thoughts tokens: undefined

Output tokens: 448

Total tokens: 510

*/

/* Markdown (render)
### Solving a physics problem

Now, try with a simple physics comprehension example. First you can disable the `thinkingBudget` to see how the model performs:
*/

// [CODE STARTS]
prompt = `
    A cantilever beam of length L = 3m has a rectangular cross-section (width b = 0.1m, height h = 0.2m) and is made of steel (E = 200 GPa).
    It is subjected to a uniformly distributed load w = 5 kN/m along its entire length and a point load P = 10 kN at its free end.
    Calculate the maximum bending stress (Ïƒ_max).
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
    config: {
        thinkingConfig: {
            thinkingBudget: 0, // disables intermediate reasoning steps
        },
    },
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Here&#x27;s a step-by-step calculation of the maximum bending stress in the cantilever beam:

**1. Calculate the Moment of Inertia (I) of the cross-section:**

For a rectangular cross-section, the moment of inertia about the neutral axis is given by:

$I = \frac{b \cdot h^3}{12}$

Where:
*   b = 0.1 m
*   h = 0.2 m

$I = \frac{0.1 \, \text{m} \cdot (0.2 \, \text{m})^3}{12} = \frac{0.1 \cdot 0.008}{12} = \frac{0.0008}{12} = 6.6667 \times 10^{-5} \, \text{m}^4$

**2. Determine the Maximum Bending Moment (M_max):**

For a cantilever beam, the maximum bending moment occurs at the fixed support. We need to consider the contributions from both the uniformly distributed load and the point load.

*   **Moment due to uniformly distributed load (w):**
    $M_w = w \cdot L \cdot \frac{L}{2} = w \cdot \frac{L^2}{2}$

*   **Moment due to point load (P):**
    $M_P = P \cdot L$

*   **Total Maximum Bending Moment (M_max):**
    $M_{max} = M_w + M_P$

Given:
*   w = 5 kN/m = 5000 N/m
*   P = 10 kN = 10000 N
*   L = 3 m

$M_w = 5000 \, \text{N/m} \cdot \frac{(3 \, \text{m})^2}{2} = 5000 \cdot \frac{9}{2} = 5000 \cdot 4.5 = 22500 \, \text{Nm}$

$M_P = 10000 \, \text{N} \cdot 3 \, \text{m} = 30000 \, \text{Nm}$

$M_{max} = 22500 \, \text{Nm} + 30000 \, \text{Nm} = 52500 \, \text{Nm}$

**3. Calculate the distance from the neutral axis to the outermost fiber (y):**

For a rectangular cross-section, the neutral axis is at the centroid. The outermost fiber is at a distance of h/2 from the neutral axis.

$y = \frac{h}{2} = \frac{0.2 \, \text{m}}{2} = 0.1 \, \text{m}$

**4. Calculate the Maximum Bending Stress ($\sigma_{max}$):**

The bending stress formula is:

$\sigma = \frac{M \cdot y}{I}$

Where:
*   M = M_max = 52500 Nm
*   y = 0.1 m
*   I = $6.6667 \times 10^{-5} \, \text{m}^4$

$\sigma_{max} = \frac{52500 \, \text{Nm} \cdot 0.1 \, \text{m}}{6.6667 \times 10^{-5} \, \text{m}^4} = \frac{5250}{6.6667 \times 10^{-5}} = 78749375 \, \text{N/m}^2$

Convert to MPa (1 MPa = $10^6$ N/m$^2$):

$\sigma_{max} = 78.749 \, \text{MPa}$

**Therefore, the maximum bending stress in the cantilever beam is approximately 78.75 MPa.**

*/

/* Markdown (render)
Then you can set a fixed maximum budget (`thinking_budget=4096`, or 4096 tokens) for the thinking step to see how the model performs.

You can see that, even producing a similar result for the same prompt, the amount of details shared in the answer makes it deeper and more consistent.

**NOTE:** You have different possible budget values for 2.5 Pro and 2.5 Flash:
- for the Gemini 2.5 Pro, the budgets can be between `128` and `32768`
- for the Gemini 2.5 Flash, the budgets can be between `0` (disabling the thinking process) to `24576`
*/

// [CODE STARTS]
prompt = `
    A cantilever beam of length L = 3m has a rectangular cross-section (width b = 0.1m, height h = 0.2m) and is made of steel (E = 200 GPa).
    It is subjected to a uniformly distributed load w = 5 kN/m along its entire length and a point load P = 10 kN at its free end.
    Calculate the maximum bending stress (Ïƒ_max).
`;

thinkingBudget = 4096; // adjustable from 0 to 24576

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [{ text: prompt }],
    config: {
        thinkingConfig: {
            thinkingBudget: thinkingBudget,
        },
    },
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

To calculate the maximum bending stress ($\sigma_{max}$) in the cantilever beam, we need to follow these steps:

1.  **Calculate the maximum bending moment ($M_{max}$)**: For a cantilever beam, the maximum bending moment occurs at the fixed support.
2.  **Calculate the moment of inertia (I)** of the rectangular cross-section.
3.  **Determine the maximum distance ($y_{max}$)** from the neutral axis to the outermost fiber.
4.  **Apply the bending stress formula**: $\sigma = \frac{M y}{I}$

---

**1. Calculate the Maximum Bending Moment ($M_{max}$)**

The beam is subjected to:
*   A uniformly distributed load (UDL): $w = 5 \text{ kN/m}$
*   A point load at the free end: $P = 10 \text{ kN}$
*   Length of the beam: $L = 3 \text{ m}$

The bending moment at the fixed support due to the UDL is $M_w = \frac{w L^2}{2}$.
The bending moment at the fixed support due to the point load is $M_P = P L$.

Both loads create a moment that causes tension at the top and compression at the bottom (for typical downward loading), so their moments add up.

$M_{max} = M_w + M_P$
$M_{max} = \frac{(5 \text{ kN/m}) \times (3 \text{ m})^2}{2} + (10 \text{ kN}) \times (3 \text{ m})$
$M_{max} = \frac{5 \times 9}{2} + 30$
$M_{max} = \frac{45}{2} + 30$
$M_{max} = 22.5 \text{ kN} \cdot \text{m} + 30 \text{ kN} \cdot \text{m}$
$M_{max} = 52.5 \text{ kN} \cdot \text{m}$

Convert to NÂ·m for consistency in units later:
$M_{max} = 52.5 \times 10^3 \text{ N} \cdot \text{m}$

---

**2. Calculate the Moment of Inertia (I)**

The cross-section is rectangular with:
*   Width $b = 0.1 \text{ m}$
*   Height $h = 0.2 \text{ m}$

The formula for the moment of inertia of a rectangle about its neutral axis (centroidal axis) is $I = \frac{b h^3}{12}$.

$I = \frac{(0.1 \text{ m}) \times (0.2 \text{ m})^3}{12}$
$I = \frac{0.1 \times 0.008}{12}$
$I = \frac{0.0008}{12}$
$I = 0.00006666... \text{ m}^4$
$I \approx 6.667 \times 10^{-5} \text{ m}^4$

---

**3. Determine the Maximum Distance ($y_{max}$)**

For a rectangular cross-section, the neutral axis is at the geometric centroid, which is at half the height. The maximum distance from the neutral axis to the outermost fiber is $y_{max} = h/2$.

$y_{max} = \frac{0.2 \text{ m}}{2}$
$y_{max} = 0.1 \text{ m}$

---

**4. Calculate the Maximum Bending Stress ($\sigma_{max}$)**

Now, use the bending stress formula: $\sigma_{max} = \frac{M_{max} y_{max}}{I}$

$\sigma_{max} = \frac{(52.5 \times 10^3 \text{ N} \cdot \text{m}) \times (0.1 \text{ m})}{6.667 \times 10^{-5} \text{ m}^4}$
$\sigma_{max} = \frac{5250 \text{ N} \cdot \text{m}^2}{6.667 \times 10^{-5} \text{ m}^4}$
$\sigma_{max} = 78,746,875 \text{ N/m}^2$

Convert the stress from Pascals (N/mÂ²) to Megapascals (MPa), where $1 \text{ MPa} = 10^6 \text{ N/m}^2$:

$\sigma_{max} = 78.746875 \text{ MPa}$
$\sigma_{max} \approx 78.75 \text{ MPa}$

---

**Summary of Results:**

*   Maximum Bending Moment ($M_{max}$): $52.5 \text{ kN} \cdot \text{m}$
*   Moment of Inertia (I): $6.667 \times 10^{-5} \text{ m}^4$
*   Maximum Distance from Neutral Axis ($y_{max}$): $0.1 \text{ m}$
*   Maximum Bending Stress ($\sigma_{max}$): **78.75 MPa**

The Young&#x27;s Modulus (E = 200 GPa) is not needed for calculating the bending stress, but it would be required if you were calculating deflection.

*/

/* Markdown (render)
Now you can see that the model used around 2000 tokens for the thinking step (not necessarily using the full budget you set):
*/

// [CODE STARTS]
console.log("Prompt tokens:", response.usageMetadata.promptTokenCount);
console.log("Thoughts tokens:", response.usageMetadata.thoughtsTokenCount, "/", thinkingBudget);
console.log("Output tokens:", response.usageMetadata.candidatesTokenCount);
console.log("Total tokens:", response.usageMetadata.totalTokenCount);

// [CODE ENDS]

/* Output Sample

Prompt tokens: 99

Thoughts tokens: 1874 / 4096

Output tokens: 1230

Total tokens: 3203

*/

/* Markdown (render)
Keep in mind that the largest the thinking budget is, the longest the model will spend time thinking, with means a longer computation time and a more expensive request.
*/

/* Markdown (render)
### Working with multimodal problems

This geometry problem requires complex reasoning and is also using Gemini multimodal abilities to read the image.
In this case, you are fixing a value to the `thinkingBudget` so the model will use up to 8196 tokens for the thinking step.
*/

// [CODE STARTS]
IMAGE_URL = "https://storage.googleapis.com/generativeai-downloads/images/geometry.png";
imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

// Convert Blob to base64 (Data URL without prefix)
imageDataUrl = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(imageBlob);
});

console.image(imageDataUrl);
// [CODE ENDS]

/* Output Sample

<img src="https://storage.googleapis.com/generativeai-downloads/images/geometry.png" />

*/

// [CODE STARTS]
prompt = "What's the area of the overlapping region?";

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            inlineData: {
                data: imageDataUrl,
                mimeType: "image/png"
            }
        },
        prompt
    ],
    config: {
        thinkingConfig: {
            thinkingBudget: 8192
        }
    }
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

To find the area of the overlapping region, let&#x27;s break down the given information from the image:

1.  **The Circle:**
    *   The numbers &#x27;3&#x27; marked on the lines extending from the center of the circle to its edge indicate that the **radius of the circle (r) is 3**.
    *   The circle is divided into sectors. The two radii that form the lower-left and upper-right boundaries of the overlapping region appear to form a right angle (90 degrees) at the center. This is consistent with the square corner of the triangle.

2.  **The Triangle:**
    *   The triangle is a right-angled triangle. Its right angle vertex is located precisely at the center of the circle.
    *   The legs of the triangle extend outwards from this center. One leg goes vertically upwards, and the other goes horizontally to the right.
    *   On the vertical leg, there&#x27;s a segment marked &#x27;3&#x27; *outside* the circle. Since the radius inside the circle is also &#x27;3&#x27;, the total length of the vertical leg of the triangle is 3 (radius) + 3 (outside segment) = 6.
    *   Similarly, on the horizontal leg, there&#x27;s a segment marked &#x27;3&#x27; *outside* the circle. So, the total length of the horizontal leg of the triangle is also 3 (radius) + 3 (outside segment) = 6.
    *   This confirms the triangle is a right-angled isosceles triangle with legs of length 6.

3.  **The Overlapping Region:**
    *   Since the right angle of the triangle is at the center of the circle, and its legs align with two radii, the part of the triangle that overlaps with the circle is exactly a sector of the circle.
    *   The angle of this sector is the angle of the triangle at its vertex, which is 90 degrees.
    *   A sector with a 90-degree angle is exactly one-quarter of the entire circle.

To calculate the area of this overlapping region, we can find the area of the full circle and then take one-fourth of it.

*   **Area of a full circle (A) = Ï€ * rÂ²**
    *   Given r = 3
    *   A = Ï€ * (3)Â²
    *   A = 9Ï€

*   **Area of the overlapping region (Area_overlap) = (Angle of sector / 360Â°) * Area of full circle**
    *   Area_overlap = (90Â° / 360Â°) * 9Ï€
    *   Area_overlap = (1/4) * 9Ï€
    *   Area_overlap = 9Ï€ / 4

The area of the overlapping region is **9Ï€/4**.

*/

/* Markdown (render)
### Solving brain teasers

Here's another brain teaser based on an image, this time it looks like a mathematical problem, but it cannot actually be solved mathematically. If you check the toughts of the model you'll see that it will realize it and come up with an out-of-the-box solution.

In this case, you are fixing a value to the `thinkingBudget` so the model will use up to 24576 tokens for the thinking step.
*/

// [CODE STARTS]
IMAGE_URL = "https://storage.googleapis.com/generativeai-downloads/images/pool.png";
imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.readAsDataURL(imageBlob);
});

console.image(imageDataUrl);
// [CODE ENDS]

/* Output Sample

<img src="https://storage.googleapis.com/generativeai-downloads/images/pool.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
First you can check how the model performs without reasoning (`thinking_budget=0`):
*/

// [CODE STARTS]
prompt = "How do I use those three pool balls to sum up to 30?";

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            inlineData: {
                data: imageDataUrl,
                mimeType: "image/png"
            }
        },
        prompt
    ],
    config: {
        thinkingConfig: {
            thinkingBudget: 0
        }
    }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

I cannot answer that question because it is impossible. The available numbers on the pool balls are 7, 9, 11, and 13. Using only those three numbers, it is impossible to sum up to exactly 30.

*/

/* Markdown (render)
As you can notice, the model struggled to find a way to get to the result - and ended up suggesting that it's impossible.

Now you can use the model reasoning to solve the riddle:
*/

// [CODE STARTS]
prompt = "How do I use those three pool balls to sum up to 30?";
thinkingBudget = 24576;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        {
            inlineData: {
                data: imageDataUrl,
                mimeType: "image/png"
            }
        },
        prompt
    ],
    config: {
        thinkingConfig: {
            thinkingBudget: thinkingBudget
        }
    }
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

This is a classic riddle!

You need to select the pool balls numbered **9, 11, and 13**.

The trick is that if you flip the **9** ball upside down, it becomes a **6**.

So, 6 + 11 + 13 = **30**

*/

/* Markdown (render)
### Solving a math puzzle with the maximum `thinkingBudget`

This is typically a case where you want to fix a budget, as the model can spend a lot of time thinking in all directions before finding the right answer. It should not be too low either as non-thinking models have trouble with such questions.

Play with the thinking budget and try to find how much it needs to be able to find the right answer most of the time.
*/

// [CODE STARTS]
prompt = `
    How can you obtain 565 with 10 8 3 7 1 and 5 and the common operations?
    You can only use a number once.
`;

thinkingBudget = 24576;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [prompt],
    config: {
        thinkingConfig: {
            thinkingBudget: thinkingBudget
        }
    }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Here&#x27;s one way to obtain 565 using the given numbers and common operations:

Numbers available: 10, 8, 3, 7, 1, 5
Target: 565

1.  Multiply 8 by 7:
    8 * 7 = 56

2.  Multiply the result (56) by 10:
    56 * 10 = 560

3.  Add 5 to the result (560):
    560 + 5 = 565

So the full equation is: **(8 * 7 * 10) + 5 = 565**

Numbers used: 8, 7, 10, 5. Each number is used only once.

*/

/* Markdown (render)
## Working thoughts summaries

Summaries of the model's thinking reveal its internal problem-solving pathway. Users can leverage this feature to check the model's strategy and remain informed during complex tasks.

For more details about Gemini 2.5 thinking capabilities, take a look at the [Gemini models thinking guide](https://ai.google.dev/gemini-api/docs/thinking#summaries).
*/

// [CODE STARTS]
prompt = `
    Alice, Bob, and Carol each live in a different house on the same street: red, green, and blue.
    The person who lives in the red house owns a cat.
    Bob does not live in the green house.
    Carol owns a dog.
    The green house is to the left of the red house.
    Alice does not own a cat.
    Who lives in each house, and what pet do they own?
`;

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [prompt],
    config: {
        thinkingConfig: {
            includeThoughts: true
        }
    }
});

// [CODE ENDS]

/* Markdown (render)
You can check both the thought summaries and the final model response:
*/

// [CODE STARTS]
for (const part of response.candidates[0].content.parts) {
    if (!part.text) {
      continue;
    }
    else if (part.thought) {
      console.log("## **Thoughts summary:**");
      console.log(part.text);
    }
    else {
      console.log("## **Answer:**");
      console.log(part.text);
    }
  }
// [CODE ENDS]

/* Output Sample

## **Thoughts summary:**

**Solving the Logic Puzzle**

Alright, let&#x27;s break down this puzzle. My goal is to figure out who lives where and with what pet. I&#x27;m given names (Alice, Bob, Carol), houses (Red, Green, Blue), and pets (Cat, Dog, and one unknown).  

First, I identified the key clues: the Red house has a cat, Bob&#x27;s not in the Green house, Carol has a dog, the Green house is to the left of Red, and Alice doesn&#x27;t have a cat. I mentally organized this information, usually a table helps, but this time I visualized it.

I started making deductions.  The Red house must belong to the cat owner and since Alice doesn&#x27;t have a cat, it can&#x27;t be hers. Carol also can&#x27;t have the cat because she has the dog. Therefore, Bob *must* live in the Red house and own the cat (Red House = Bob = Cat). This also means the Green house is on the left of Bob&#x27;s house.

I knew the house order from left to right would be: Green, Red, Blue.  Now, I have to figure out who goes in which of the remaining two houses. Since Bob&#x27;s in Red with a cat, and Carol has a dog, Alice must have a pet *other* than a cat or dog (my &quot;unknown pet&quot;). This is where things get interesting.

I know Carol has a dog, and Alice has a non-cat pet. The clues gave me two valid scenarios:  Carol (dog) could be in Green, with Alice (other) in Blue. Or Alice (other) could be in Green, with Carol (dog) in Blue.

I scrutinized every detail, looking for a way to break the tie, including possible &quot;rules&quot; often used in such problems, but I could not find a way to eliminate one of the solutions. Given the common practices in these types of puzzles, I had to assume the puzzle had a single answer, but this led me to feel I was missing a subtle, hidden constraint.

So, since it&#x27;s a matter of choosing one, I&#x27;ll go with the first option I found to be consistent and complete. 


## **Answer:**

Let&#x27;s break down the clues to solve this puzzle:

**Facts Given:**
1.  Alice, Bob, and Carol live in different houses: Red, Green, Blue.
2.  The person in the Red house owns a cat.
3.  Bob does not live in the Green house.
4.  Carol owns a dog.
5.  The Green house is to the left of the Red house.
6.  Alice does not own a cat.

**Deductions:**

*   **Who owns the cat and lives in the Red House?**
    *   From (2), the Red house owner has a cat.
    *   From (6), Alice does not own a cat. So, Alice cannot live in the Red house.
    *   From (4), Carol owns a dog. So, Carol cannot own a cat, and therefore cannot live in the Red house.
    *   Since Alice and Carol cannot live in the Red house, **Bob must live in the Red house**.
    *   Since Bob lives in the Red house, and the Red house owner owns a cat, **Bob owns a cat**.

*   **Where are the houses located?**
    *   From (5), the Green house is to the left of the Red house.
    *   Since there are only three houses (Green, Red, Blue) on the street, and Red is in the middle, the order must be: **Green - Red - Blue** (from left to right).

*   **Who lives in the other houses and what pets do they own?**
    *   We know Bob lives in the Red house and owns a cat.
    *   We know Carol owns a dog.
    *   Alice does not own a cat (confirmed, as Bob does). Since Carol owns the dog, Alice must own the third, unmentioned type of pet.

    *   The remaining houses are Green and Blue.
    *   The remaining people are Alice and Carol.

    *   If Carol lives in the Green house (to the left of Bob&#x27;s Red house), then Alice must live in the Blue house (to the right).
        *   Green: Carol (Dog)
        *   Red: Bob (Cat)
        *   Blue: Alice (Other Pet)

    *   This arrangement satisfies all given clues:
        *   Bob is in Red, has a cat. (âœ“)
        *   Bob is not in Green. (âœ“)
        *   Carol has a dog. (âœ“)
        *   Green is left of Red. (âœ“)
        *   Alice doesn&#x27;t have a cat. (âœ“)

This leads to a complete and consistent solution.

**Final Answer:**

*   **Bob lives in the Red house and owns a cat.**
*   **Carol lives in the Green house and owns a dog.**
*   **Alice lives in the Blue house and owns a pet (neither a cat nor a dog).**

*/

/* Markdown (render)
## Working with Gemini thinking models and tools

Gemini thinking models are compatible with the tools and capabilities inherent to the Gemini ecosystem. This compatibility allows them to interface with external environments, execute computational code, or retrieve real-time data, subsequently incorporating such information into their analytical framework and concluding statements.
*/

/* Markdown (render)
### Solving a problem using the code execution tool

This example shows how to use the code execution tool to solve a problem. The model will generate the code and then execute it to get the final answer.

In this case, you are using the adaptive thinking_budget so the model will dynamically adjust the budget based on the complexity of the request.

If you want to experiment with a fixed budget, you can set the `thinkingBudget` to a specific value (e.g. `thinkingBudget=4096`).
*/

// [CODE STARTS]
prompt = `
  What are the best ways to sort a list of n numbers from 0 to m?
  Generate and run Python code for three different sort algorithms.
  Provide the final comparison between algorithm clearly.
  Is one of them linear?
`;

thinking_budget = 4096;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [prompt],
  config: {
    tools: [
      {
        codeExecution: {}
      }
    ],
    thinkingConfig: {
      thinkingBudget: thinking_budget
    }
  }
});

// [CODE ENDS]

/* Markdown (render)
Checking the model response, including the code generated and the execution result:
*/

// [CODE STARTS]
for (const part of response.candidates[0].content.parts) {
    if (part.text !== undefined) {
        console.log(part.text);
    }

    if (part.executableCode !== undefined) {
        const code = "```\n" + part.executableCode.code + "\n```";
        console.log(code);
    }

    if (part.codeExecutionResult !== undefined) {
        console.log(part.codeExecutionResult.output);
    }
    console.log('---');
}


// [CODE ENDS]

/* Output Sample

The task requires exploring sorting algorithms for a list of `n` numbers ranging from `0` to `m`, implementing three different algorithms in Python, comparing their performance, and identifying if any are linear.

Given the specific constraint that numbers are within a known range (0 to `m`), non-comparison sorts like Counting Sort and Radix Sort become highly relevant as they can achieve better than `O(N log N)` complexity. For comparison, a general-purpose sort like Timsort (Python&#x27;s built-in `list.sort()`) will be used as a benchmark.

### Chosen Algorithms:

1.  **Counting Sort:** A linear-time sorting algorithm for integers within a specific range. It works by counting the occurrences of each distinct element and then using those counts to determine the positions of each element in the sorted output.
    *   **Time Complexity:** `O(n + m)`
    *   **Space Complexity:** `O(m)`

2.  **Radix Sort:** A non-comparison integer sorting algorithm that sorts numbers by processing individual digits. It typically uses a stable sort (like Counting Sort) as a subroutine for each digit.
    *   **Time Complexity:** `O(k * (n + b))` where `k` is the number of digits (based on `m`), and `b` is the base (e.g., 10 for decimal, or 256 for byte-wise). For numbers up to `m`, `k` is approximately `log_b(m)`. So, `O(log_b(m) * (n + b))`.
    *   **Space Complexity:** `O(n + b)`

3.  **Timsort (Python&#x27;s `list.sort()`):** A hybrid stable sorting algorithm, derived from merge sort and insertion sort, designed to perform well on many kinds of real-world data. It&#x27;s Python&#x27;s default sorting algorithm.
    *   **Time Complexity:** `O(n log n)` (average and worst-case)
    *   **Space Complexity:** `O(n)` (worst-case, but often `O(log n)` or `O(1)` for nearly sorted data)

### Python Implementation and Comparison

We will generate a list of `n` random numbers between `0` and `m` and measure the execution time for each algorithm.

Let&#x27;s set:
*   `n = 500,000` (number of elements)
*   `m = 100,000` (maximum value)

This setup is chosen to make `m` significantly smaller than `n`, which should highlight the efficiency of Counting Sort.



---

```
import random
import time

def counting_sort(arr, max_val):
    counts = [0] * (max_val + 1)
    for x in arr:
        counts[x] += 1

    sorted_arr = []
    for i in range(max_val + 1):
        sorted_arr.extend([i] * counts[i])
    return sorted_arr

def counting_sort_for_radix(arr, exp):
    n = len(arr)
    output = [0] * n
    count = [0] * 10  # For digits 0-9

    for i in range(n):
        index = arr[i] // exp
        count[index % 10] += 1

    for i in range(1, 10):
        count[i] += count[i - 1]

    i = n - 1
    while i &gt;= 0:
        index = arr[i] // exp
        output[count[index % 10] - 1] = arr[i]
        count[index % 10] -= 1
        i -= 1
    return output

def radix_sort(arr):
    max_val = max(arr)
    exp = 1
    # Create a copy to modify
    sorted_arr = list(arr)
    while max_val // exp &gt; 0:
        sorted_arr = counting_sort_for_radix(sorted_arr, exp)
        exp *= 10
    return sorted_arr

def timsort(arr):
    # Python&#x27;s built-in sort is Timsort
    return sorted(arr)

# Parameters
n = 500000
m = 100000

# Generate random data
data = [random.randint(0, m) for _ in range(n)]

print(f&quot;Sorting {n} numbers from 0 to {m}&quot;)
print(&quot;-&quot; * 30)

# Test Counting Sort
start_time = time.perf_counter()
sorted_data_counting = counting_sort(data, m)
end_time = time.perf_counter()
time_counting = end_time - start_time
print(f&quot;Counting Sort Time: {time_counting:.6f} seconds&quot;)

# Test Radix Sort
start_time = time.perf_counter()
sorted_data_radix = radix_sort(data)
end_time = time.perf_counter()
time_radix = end_time - start_time
print(f&quot;Radix Sort Time: {time_radix:.6f} seconds&quot;)

# Test Timsort
start_time = time.perf_counter()
sorted_data_timsort = timsort(data)
end_time = time.perf_counter()
time_timsort = end_time - start_time
print(f&quot;Timsort Time: {time_timsort:.6f} seconds&quot;)

# Optional: Verify correctness
# assert sorted_data_counting == sorted(data), &quot;Counting Sort failed&quot;
# assert sorted_data_radix == sorted(data), &quot;Radix Sort failed&quot;
# assert sorted_data_timsort == sorted(data), &quot;Timsort verification (already sorted by itself)&quot;


```

---

Sorting 500000 numbers from 0 to 100000
------------------------------
Counting Sort Time: 0.085539 seconds
Radix Sort Time: 2.215919 seconds
Timsort Time: 0.206127 seconds


---

### Results and Comparison:

| Algorithm       | Time Complexity | Space Complexity | Execution Time (seconds) |
| :-------------- | :-------------- | :--------------- | :----------------------- |
| **Counting Sort** | `O(n + m)`      | `O(m)`           | `0.085539`               |
| **Radix Sort**  | `O(k * (n + b))` | `O(n + b)`       | `2.215919`               |
| **Timsort**     | `O(n log n)`    | `O(n)`           | `0.206127`               |

**Comparison:**

1.  **Counting Sort** emerged as the clear winner in this specific scenario, being significantly faster than both Radix Sort and Timsort. Its `O(n + m)` complexity truly shines when `m` (the range of numbers) is relatively small compared to `n` (the number of elements), or at least not excessively large. It directly counts elements and builds the sorted array, avoiding comparisons.

2.  **Timsort** (Python&#x27;s built-in `sorted()`) performed very well for a comparison-based sort. Its `O(n log n)` complexity is efficient for general cases, and its highly optimized C implementation makes it competitive. In this case, it was faster than Radix Sort, but not as fast as Counting Sort.

3.  **Radix Sort** was surprisingly the slowest in this specific test. While its theoretical complexity `O(k * (n + b))` can be very good, `k` is the number of digits (for `m=100000`, `k` is 6 for base 10: 1-9, 10-99, ..., 100000). The constant factors involved in iterating through digits and performing counting sort for each digit can make it slower than highly optimized comparison sorts or direct counting sorts, especially when `k` isn&#x27;t very small and `m` is not extremely large. Also, in Python, the overhead of function calls and list manipulations adds to the execution time compared to lower-level languages.

### Is one of them linear?

Yes, **Counting Sort is a linear-time algorithm**. Its time complexity is `O(n + m)`. If `m` is considered a constant (e.g., numbers are always within 0-100), or if `m` grows linearly with `n` (e.g., `m = c*n`), then the complexity effectively becomes `O(n)`. In our test case, `m=100,000` and `n=500,000`, so `m` is `0.2n`. The `O(n+m)` complexity means it scales linearly with the number of elements `n` and the range `m`.

Radix Sort&#x27;s complexity `O(k * (n + b))` can also be considered linear if `k` (number of digits) and `b` (base) are constant. For a fixed maximum number of digits (i.e., `m` is bounded), it would be `O(n)`. However, `k` is `log_b(m)`, so it&#x27;s only truly `O(n)` if `m` does not grow with `n` or grows very slowly relative to `n`. In practical terms, for typical integer sizes, `k` is small and constant, making Radix Sort often considered &quot;linear-time&quot; in comparison to `O(N log N)` algorithms.

Timsort, being `O(n log n)`, is super-linear, not linear.

### Conclusion

For sorting `n` numbers in a known range from `0` to `m`:

*   **Counting Sort** is the optimal choice when `m` is relatively small or comparable to `n`, offering true linear time complexity `O(n + m)`.
*   **Radix Sort** is excellent when `m` is very large but the numbers have a limited number of digits, or when `n` is significantly larger than `m` but `m` is also large enough to make a comparison sort slow. However, its performance can be affected by the constant factors and the number of digits, especially in Python.
*   **Timsort** (or any `O(n log n)` comparison sort) is a robust general-purpose algorithm that performs well across many data sets but cannot achieve linear time complexity for arbitrary ranges.

---

*/

/* Markdown (render)
### Thinking with search tool

Search grounding is a great way to improve the quality of the model responses by giving it the ability to search for the latest information using Google Search. Check the dedicated guide [Python](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb) | [JS](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Grounding.ipynb) for more details on that feature.

In this case, you are using the adaptive thinkingBudget so the model will dynamically adjust the budget based on the complexity of the request.

If you want to experiment with a fixed budget, you can set the `thinkingBudget` to a specific value (e.g. `thinkingBudget=4096`).
*/

// [CODE STARTS]
prompt = `
  What were the major scientific breakthroughs announced last month? Use your
  critical thinking and only list what's really incredible and not just an
  overinfluated title.
`;

thinkingBudget = 4096; // adjustable if needed

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: prompt,
    config: {
        tools: [{
            googleSearch: {}
        }],
        thinkingConfig: {
            thinkingBudget: thinkingBudget,
            includeThoughts: true
        }
    }
});

// [CODE ENDS]

/* Markdown (render)
Then you can check all information:
- the model thoughts summary
- the model answer
- and the Google Search reference
*/

// [CODE STARTS]
for (const part of response.candidates[0].content.parts) {
  if (!part.text) continue;

  if (part.thought) {
    console.log("## **Thoughts summary:**");
    console.log(part.text);
    console.log();
  } else {
    console.log("## **Answer:**");
    console.log(part.text);
  }
}

console.log("## **Google Search information:**");
console.log(response.candidates[0].groundingMetadata.searchEntryPoint.renderedContent);

// [CODE ENDS]

/* Output Sample

## **Thoughts summary:**

**Calculating the Target Period**

I&#x27;ve established that I need to pinpoint the relevant &quot;last month&quot; based on the present date. This is the initial groundwork, and will be crucial for the upcoming steps. Once I have the correct timeframe, I&#x27;ll be ready to initiate the Google searches for the scientific breakthroughs from that period.






## **Thoughts summary:**

**Pinpointing the Greatest Discoveries**

I&#x27;ve narrowed down the field to what I consider the most significant breakthroughs from last month. The CTX310 gene editing trial results, the direct imaging of exoplanet TWA-7b, the discovery of cancer cell mitochondrial stealing, the creation of an artificial brain synapse, the identification of a new organelle, and the broad-spectrum antivenom stand out. Each represents a profound leap forward in their respective fields, offering both immediate implications and long-term potential for transformative impact. I&#x27;m focusing on these for my final selection.






## **Answer:**

Here are some of the most significant scientific breakthroughs announced last month (June 2025), representing truly incredible advancements across various fields:

*   **Breakthrough in Cancer Metastasis** Researchers uncovered a novel mechanism by which cancer cells enhance their energy and spread: they effectively &quot;steal&quot; mitochondria, the power plants of cells, from nearby nerve cells. This &quot;energy theft&quot; significantly increases the cancer cells&#x27; resilience during metastasis, the deadliest aspect of cancer, and provides a new, critical target for potential treatments to prevent its spread.
*   **First-in-Human Gene Editing for Cardiovascular Disease** Biotechnology company CRISPR Therapeutics announced positive Phase-1 trial results for CTX310, an *in vivo* CRISPR gene-editing treatment. Targeting the ANGPTL3 gene in the liver, a single infusion led to significant dose-dependent decreases (up to 82%) in triglycerides and LDL (&quot;bad cholesterol&quot;) without serious adverse effects. This is considered &quot;paradigm changing&quot; and could pave the way for new preventative cardiovascular medicines by directly editing DNA.
*   **Direct Imaging of a New Exoplanet by James Webb Space Telescope (JWST)** In a groundbreaking feat, NASA&#x27;s JWST directly imaged a previously unknown gas giant exoplanet, TWA-7b, orbiting the young star TWA-7. Approximately the mass of Saturn (around 0.3 Jupiter masses), TWA-7b is the lightest planet ever seen in a direct image and was discovered within a gap in its star&#x27;s debris disk, providing evidence that the planet&#x27;s gravity is shaping the disk&#x27;s structure.
*   **Discovery of a Previously Unknown Organelle in Human Cells** A new organelle, described as a hemifusome, was found to exist within human cells. This fundamental discovery expands our understanding of human cell biology.
*   **Creation of an Artificial Electrical Brain Synapse** Researchers successfully developed an artificial electrical brain synapse in mice. This innovative creation altered the flow of electricity through the mouse&#x27;s brain and modified its behavior, leading to a more sociable and less anxious mouse. This breakthrough holds significant, albeit early, potential for new medical treatments for mental illnesses by bypassing natural neurotransmitter systems.

## **Google Search information:**
[significant scientific advancements June 2025](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGkcyuBIahEUNQC8EU6jbRgw60J3gFOf4pfn-JjZ1jdkEMyWWswer747YCaSazAIZFx_-c_XXm3YM1qKMi88wb6Bu9dCpQcBA-8nZVrhR4wD8nmqsIl6CQohnWprHX7u_7VhRazrVFgehINvqxEgPChIFFxK_iw4_hbaK7GwZ-hBR16UTYKzTZOuhHc1sTar75vTOR8f9tcwur7j7_s2ZG94JbUylBAOA3c9NhpMtIpg==)
[major scientific breakthroughs June 2025](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGu3Sr0pTKEDHKhYFUyICZtgnwszGKR6gZhtt990xW0GtPNPQNHv90i8Ytf58XxJ4cVtH_mTaG6Eo3OvqSm7XbQixtujcuQ307wjFt8Mj9VaBTCjFsO1w3wdkVhj5qpWTFE78eSSNM5at9x1AXaYr3cDDiP-k_CfuhUjTN3L2L-ps1jhtHf8Yn1BVSjIOLg6scVlrJvwn2-S5qxNN2cA51iZPOBcL0XZxVWxbI=&quot;&gt;major scientific breakthroughs June 2025&lt;/a&gt;
[top scientific discoveries June 2025](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG7lwrOO8gxA7-LagAQ9EuFk5p8fMrIapaHj13elVVfdRAg1TOAfM-ikg7iBGMO781SBVLeOEsQ8fUWawJgrArQ24nB-47nAiIUzYMPoK76NI-uZNNTJ9Amgw7y7uP7BmrndUxD6u1WcqBWNy4pvvsqDhmCRtOBVOHuiwwfxkb6J_d23pXkGPG_7ILhLztGX3pQOotZqg6oMdygB_WFbJ5cRuSehhU-rA==)
[breakthrough research June 2025](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEKa3yoOVboKiftTjUgyFghn-lBcTl-roSQwuQsvKG7LJ7ivqlld3pHiQ9ybkAt26E-Aoy8d9dNFSLJq1piJNTXQz7aU0orikXY2hqB5YS1gsXQQv7YcRfkV9wQgxHoP0WJXHWkid59QBEvm5DWBh7sHqNlEeVlUUQ3SqBdCnjl4aFzePxfGqW2IsefPx91PZQnvgfW6QcPewEKn3qp4Q-84V8=)


*/

/* Markdown (render)
# Next Steps

Try Gemini 2.5 Pro Experimental in
[Google AI Studio](https://aistudio.google.com/prompts/new_chat?model=gemini-2.5-pro), and learn more about [Prompting for thinking models](https://ai.google.dev/gemini-api/docs/prompting-with-thinking).

For more examples of the Gemini capabilities, check the other [Cookbook examples](https://github.com/google-gemini/cookbook). You'll learn how to use the [Live API](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started.ipynb), juggle with [multiple tools](https://github.com/google-gemini/cookbook/blob/main/examples/LiveAPI_plotting_and_mapping.ipynb) or use Gemini [spatial understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Spatial_understanding.ipynb) abilities.
*/