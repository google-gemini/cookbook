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
# Gemini 2.5 Native Image generation

This notebook will show you how to use the native Image-output feature of Gemini, using the model multimodal capabilities to output both images and texts, and iterate on an image through a discussion.

This model is really good at:
* **Maintaining character consistency**: Preserve a subject’s appearance across multiple generated images and scenes
* **Performing intelligent editing**: Enable precise, prompt-based edits like inpainting (adding/changing objects), outpainting, and targeted transformations within an image
* **Compose and merge images**: Intelligently combine elements from multiple images into a single, photorealistic composite
* **Leverage multimodal reasoning**: Build features that understand visual context, such as following complex instructions on a hand-drawn diagram

Following this guide, you'll learn how to do all those things and even more.
*/

/* Markdown (render)
<!-- Princing warning Badge -->
<table>
  <tr>
    <!-- Emoji -->
    <td bgcolor="#f5949e">
      <font size=30>⚠️</font>
    </td>
    <!-- Text Content Cell -->
    <td bgcolor="#f5949e">
      <h3><font color=black>Image generation is a paid-only feature and won't work if you are on the free tier. Check the <a href="https://ai.google.dev/pricing#gemini-2.5-flash-image-preview"><font color='#217bfe'>pricing</font></a> page for more details.</font></h3>
    </td>
  </tr>
</table>
 */

/* Markdown (render)
Imagen models also offer image generaion but in a slightly different way as the Image-out feature has been developed to work iteratively so if you want to make sure certain details are clearly followed, and you are ready to iterate on the image until it's exactly what you envision, Image-out is for you.

Check the [documentation](https://ai.google.dev/gemini-api/docs/image-generation#choose-a-model) for more details on both features and some more advice on when to use each one.
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

MODEL_ID = "gemini-2.5-flash-image-preview"
// [CODE ENDS]

/* Markdown (render)
## Generate images

Using the Gemini Image generation model is the same as using any Gemini model: you simply call `generateContent`.

You can set the `responseModalities` to indicate to the model that you are expecting an image in the output but it's optional as this is expected with this model.
*/

// [CODE STARTS]
Modality = module.Modality

prompt = 'Create a photorealistic image of a siamese cat with a green left eye and a blue right one and red patches on his face and a black and pink nose';

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: prompt,
    config: { responseModalities: [Modality.TEXT, Modality.IMAGE] }
});

for (const part of response.candidates[0].content.parts) {
    if (part.text !== undefined) {
        console.log(part.text);
    } else if (part.inlineData !== undefined) {
        catImage = part.inlineData.data;
        console.image(catImage);
    }
}
// [CODE ENDS]

/* Output Sample

Here is your requested image: 

<img src="https://iili.io/K2AiWvI.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
## Edit images

You can also do image editing, simply pass the original image as part of the prompt. Don't limit yourself to simple edit, Gemini is able to keep the character consistency and reprensent you character in different behaviors or places.
*/

// [CODE STARTS]
textPrompt = "Create a side view picture of that cat, in a tropical forest, eating a nano-banana, under the stars";

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { text: textPrompt },
    {
      inlineData: {
        data: catImage,
        mimeType: "image/png"
      }
    }
  ]
});

for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  } else if (part.inlineData !== undefined) {
    catImage = part.inlineData.data;
    console.image(catImage);
  }
}

// [CODE ENDS]

/* Output Sample

<img src="https://iili.io/K2A4E42.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
As you can see, you can clearly recognize the same cat with its peculiar nose and eyes.

Let's do a second one:
*/

// [CODE STARTS]
textPrompt = "Now the cat should keep the same attitude, but be well dressed in fancy restaurant and eat a fancy nano banana.";

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { text: textPrompt },
    {
      inlineData: {
        data: catImage,
        mimeType: "image/png"
      }
    }
  ]
});

for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  } else if (part.inlineData !== undefined) {
    catImage = part.inlineData.data;
    console.image(catImage);
  }
}

// [CODE ENDS]

/* Output Sample

<img src="https://iili.io/K2AS4sV.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
## Get multiple images (e: tell stories)

So far you've only generated one image per call, but you can request way more than that! Let's try a baking receipe or telling a story.
*/

// [CODE STARTS]
prompt = 'Show me how to bake macarons with images';

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: prompt
});

for (const part of response.candidates[0].content.parts) {
    if (part.text !== undefined) {
        console.log(part.text);
    } else if (part.inlineData !== undefined) {
        imageURL = part.inlineData.data;
        console.image(imageURL);
    }
}
// [CODE ENDS]


/* Markdown (render)
The output of the previous code cell could not be saved in the notebook without making it too big to be managed by Github, but here are some examples of what it should look like when you run it when asking for a story, or for a baking receipe:

----------
**Prompt**: *Create a beautifully entertaining 8 part story with 8 images with two blue characters and their adventures in the 1960s music scene. The story is thrilling throughout with emotional highs and lows and ending on a great twist and high note. Do not include any words or text on the images but tell the story purely through the imagery itself.*
![Azure tone story](https://storage.googleapis.com/generativeai-downloads/images/azuretones.png)
(Images have been stitched together)

----------
**Prompt**: *Show me how to bake macarons with images*


That sounds delicious! Here's a simplified guide on how to bake macarons. While it can be a bit tricky, practice makes perfect!

**Ingredients you'll need:**

*   **For the Macaron Shells:**
    *   100g almond flour
    *   100g powdered sugar
    *   75g granulated sugar
    *   2 egg whites (aged for a day or two at room temp, if possible, for better stability)
    *   Pinch of salt (optional)
    *   Food coloring (gel or powder, not liquid)

*   **For the Filling:** (Buttercream, ganache, or jam are popular choices)

---

**Step 1: Prepare your dry ingredients.**
Sift together the almond flour and powdered sugar into a bowl. This step is crucial for achieving smooth macaron shells, as it removes any lumps.


![Macaron prepartation step 1](https://storage.googleapis.com/generativeai-downloads/images/macaron_step1.png)

**Step 2: Make the meringue.**
In a separate, clean bowl, beat the egg whites with a pinch of salt (if using) until foamy. Gradually add the granulated sugar, continuing to beat until you achieve stiff, glossy peaks. If you're using food coloring, add it now. The meringue should be firm enough that you can turn the bowl upside down without it falling out.

![Macaron prepartation step 2](https://storage.googleapis.com/generativeai-downloads/images/macaron_step2.png)

**Step 3: Combine dry ingredients with meringue (Macaronage).**
Gently fold the sifted almond flour and powdered sugar into the meringue in two or three additions. This is called "macaronage" and is the most critical step. You want to mix until the batter flows like "lava" or a slowly ribboning consistency when you lift your spatula. Be careful not to overmix, or your macarons will be flat; under-mixing will result in lumpy shells.

![Macaron prepartation step 3](https://storage.googleapis.com/generativeai-downloads/images/macaron_step3.png)

**Step 4: Pipe the macarons.**
Transfer the batter to a piping bag fitted with a round tip. Pipe uniform circles onto baking sheets lined with parchment paper or silicone mats. Leave some space between each macaron.

![Macaron prepartation step 4](https://storage.googleapis.com/generativeai-downloads/images/macaron_step4.png)

**Step 5: Tap and Rest.**
Firmly tap the baking sheets on your counter several times to release any air bubbles. Use a toothpick to pop any remaining bubbles. This helps create smooth tops and the characteristic "feet." Let the piped macarons rest at room temperature for 30-60 minutes, or until a skin forms on top. When you gently touch a shell, it shouldn't feel sticky. This "drying" step is essential for the feet to develop properly.

![Macaron prepartation step 5](https://storage.googleapis.com/generativeai-downloads/images/macaron_step5.png)

**Step 6: Bake the macarons.**
Preheat your oven to 300Â°F (150Â°C). Bake one tray at a time for 12-15 minutes. The exact time can vary by oven. They are done when they have developed "feet" and don't wobble when gently touched.

**Step 7: Cool and Fill.**
Once baked, let the macaron shells cool completely on the baking sheet before carefully peeling them off. This prevents them from breaking.  Then, match them up by size and pipe or spread your chosen filling onto one shell before sandwiching it with another.

![Macaron prepartation step 7](https://storage.googleapis.com/generativeai-downloads/images/macaron_step7.png)

Finally, let them mature in the refrigerator for at least 24 hours. This allows the flavors to meld and the shells to soften to the perfect chewy consistency.

Enjoy your homemade macarons!

-----
*/

/* Markdown (render)
## Chat mode (recommended method)

So far you've used unary calls, but Image-out is actually made to work better with chat mode as it's easier to iterate on an image turn after turn.
*/

// [CODE STARTS]
chat = ai.chats.create({
    model: MODEL_ID
})
// [CODE ENDS]

// [CODE STARTS]
message = "create a image of a plastic toy fox figurine in a kid's bedroom, it can have accessories but no weapon";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  }
  if (part.inlineData !== undefined) {
    foxFigurineImage = part.inlineData.data
    console.image(foxFigurineImage);
  }
}

// [CODE ENDS]

/* Output Sample

Here is an image of a plastic toy fox figurine in a kid&#x27;s bedroom, with accessories: 

<img src="https://iili.io/K2A8OAJ.png" style="height:auto; width:100%;" />

*/

// [CODE STARTS]
message = "Add a blue planet on the figuring's helmet or hat (add one if needed)";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  }
  if (part.inlineData !== undefined) {
    console.image(part.inlineData.data);
  }
}

// [CODE ENDS]

/* Output Sample

Here&#x27;s the toy fox figurine with a blue planet on its helmet: 

<img src="https://iili.io/K2A8CyG.png" style="height:auto; width:100%;" />

*/

// [CODE STARTS]
message = "Move that figurine on a beach";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  }
  if (part.inlineData !== undefined) {
    console.image(part.inlineData.data);
  }
}

// [CODE ENDS]

/* Output Sample

Here&#x27;s the figurine on a beach! 

<img src="https://iili.io/K2AvYIR.png" style="height:auto; width:100%;" />

*/

// [CODE STARTS]
message = "Now it should be base-jumping from a spaceship with a wingsuit";

response = await chat.sendMessage({ message });
 
for (const part of response.candidates[0].content.parts) {
  if (part.text !== undefined) {
    console.log(part.text);
  }
  if (part.inlineData !== undefined) {
    console.image(part.inlineData.data);
  }
}

// [CODE ENDS]

/* Output Sample

Here&#x27;s your fox figurine base-jumping from a spaceship in a wingsuit! 

<img src="https://iili.io/K2AkrWN.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
## Mix multiple pictures
You can also mix multiple images (up to 3), either because there are multiple characters in your image, or because you want to hightlight a certain product, or set the background.
*/

// [CODE STARTS]
textPrompt = "Create a picture of that figurine riding that cat in a fantasy world.";

response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
        { text: textPrompt },
        {
            inlineData: {
                data: catImage,
                mimeType: "image/png"
            }
        },
        {
            inlineData: {
                data: foxFigurineImage,
                mimeType: "image/png"
            }
        }
    ]
});

for (const part of response.candidates[0].content.parts) {
    if (part.text !== undefined) {
        console.log(part.text);
    }
    if (part.inlineData !== undefined) {
        console.image(part.inlineData.data);
    }
}

// [CODE ENDS]

/* Output Sample

Certainly! Here is your image: 

<img src="https://iili.io/K2AOpp4.png" style="height:auto; width:100%;" />

*/

/* Markdown (render)
## Next Steps
### Useful documentation references:

Check the [documentation](https://ai.google.dev/gemini-api/docs/image-generation#gemini) for more details about the image generation capabilities of the model. To improve your prompting skills, check out the [prompt guide](https://ai.google.dev/gemini-api/docs/image-generation#prompt-guide) for great advices on creating your prompts.

### Play with the AI Studio apps

Theses 5 AI Studio apps are all great showcases of Gemini image generation capabilities:
* [Past Forward](https://aistudio.google.com/apps/bundled/past_forward) lets you travel through time
* [Home Canvas](https://aistudio.google.com/apps/bundled/home_canvas) lets your try out new furniture
* [Gembooth](https://aistudio.google.com/apps/bundled/gembooth) places you into a comic book or a Renaissance painting
* [Gemini Co-drawing](https://aistudio.google.com/apps/bundled/codrawing) lets you draw alongside with Gemini
* [Pixshop](https://aistudio.google.com/apps/bundled/pixshop), an AI-powered image editor

### Check-out Imagen as well:
The [Imagen](https://ai.google.dev/gemini-api/docs/imagen) model is another way to generate images. Check out the [Get Started with Imagen notebook](./Get_started_imagen.ipynb) to start playing with it too.

Here are some Imagen examples to get your imagination started on how to use it in creative ways:
*  [Illustrate a book](https://github.com/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb): Use Gemini and Imagen to create illustration for an open-source book

### Continue your discovery of the Gemini API

Gemini is not only good at generating images, but also at understanding them. Check the [Spatial understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Spatial_understanding.ipynb) guide for an introduction on those capabilities, and the [Video understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb) one for video examples.

*/