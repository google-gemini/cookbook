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
# Gemini API: Gemini 2.0 Image output
*/

/* Markdown (render)
This notebook will show you how to use the Image-out feature of Gemini, using the model multimodal capabilities to output both images and texts, and iterate on an image through a discussion.

This feature is very close to what [Imagen](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_imagen.ipynb) offers but in a slightly different way as the Image-out feature has been developed to work iteratively so if you want to make sure certain details are clearly followed, and you are ready to iterate on the image until it's exactly what you envision, Image-out is for you.

Check the [documentation](https://ai.google.dev/gemini-api/docs/image-generation#choose-a-model) for more details on both features and some more advice on when to use each one.
*/

/* Markdown (render)
<!-- Notice Badge -->
<table align="left" border="3">
  <tr>
    <!-- Emoji -->
    <td bgcolor="#DCE2FF">
      <font size=30>🪧</font>
    </td>
    <!-- Text Content Cell -->
    <td bgcolor="#DCE2FF">
      <h4><font color=black>Image-out is a preview feature. It's free to use with quota limitations, but subject to change. See <a href="https://ai.google.dev/gemini-api/docs/pricing#gemini-2.0-flash"><font color='#217bfe'>pricing</font></a> and <a href="https://ai.google.dev/gemini-api/docs/rate-limits#current-rate-limits"><font color='#217bfe'>rate limit</font></a> pages for more details.</font></h4>
    </td>
  </tr>
</table>
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
// [CODE ENDS]

/* Markdown (render)
### Select a model

Image-out is available through the `gemini-2.0-flash-preview-image-generation` model.

For more information about all Gemini models, check the [documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for extended information.

*/

// [CODE STARTS]
MODEL_ID = "gemini-2.0-flash-preview-image-generation"
// [CODE ENDS]

/* Markdown (render)
## Generate images

Use `responseModalities` to indicate to the model that you are expecting an image in the output. You'll need to specify both `"text"` and `"image"` in your generation configuration. If you set only `"image"` in `responseModalities`, you'll get an error.

If you want to generate image only outputs, you can use Imagen.

Remember that generating people is not allowed at the moment.
*/

// [CODE STARTS]
Modality = module.Modality

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: `A 3D rendered pig with wings and a top hat flying over
             a futuristic sci-fi city filled with greenery.`,
  config: { responseModalities: [Modality.TEXT, Modality.IMAGE] }
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

I will generate a 3D rendering of a whimsical scene. Imagine a pink pig with small, delicate wings sprouting from its back, wearing a tall, elegant black top hat perched jauntily on its head. This flying pig soars above a vibrant, futuristic metropolis. The city below is characterized by sleek, silver skyscrapers with glowing blue accents, interwoven with lush green parks and elevated gardens, creating a harmonious blend of technology and nature.



<img src="https://i.ibb.co/n88Lw9YQ/pig.png" alt="pig" border="0">

*/

/* Markdown (render)
## Edit images

You can also do image editing, simply save the original image and pass it as inline data in the next prompt.
*/

// [CODE STARTS]
responseInlineMime = null;
responseInlineData = null;

for (const part of response.candidates[0].content.parts) {
  if (part.inlineData !== undefined) {
    responseInlineMime = part.inlineData.mimeType;
    responseInlineData = part.inlineData.data;
  }
}

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { text: "could you edit this image to make it a cat instead of a pig?"},
    {
      inlineData: {
        data: responseInlineData,
        mimeType: responseInlineMime
      }
    }
  ],
  config: {
    responseModalities: ["Text", "Image"]
  }
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}



// [CODE ENDS]

/* Output Sample

Okay, I will edit the image so that the flying pig is replaced with a flying cat that retains the tiger stripes, wings, and top hat, keeping the same overall style and perspective within the futuristic cityscape.


<img src="https://i.ibb.co/j98mSjMh/catpig.png" alt="catpig" border="0">

*/

/* Markdown (render)
## Get multiple images

So far you've only generated one image per call, but you can request way more than that! Let's try a baking receipe.
*/

// [CODE STARTS]
contents = "Show me how to bake a macaron with images.";

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: contents,
  config: {
    responseModalities: ["Text", "Image"]
  }
});

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

Okay! Let's embark on the delightful (and sometimes challenging!) journey of making macarons.  I'll provide step-by-step instructions with images to guide you.  

**Important Note:** Macarons are finicky. Success depends on accuracy and patience. Follow the instructions closely, especially with measurements.

**Recipe: Classic French Macarons**

**Ingredients:**

*   **For the Macaron Shells:**
    *   100 grams (about 1 cup) finely ground almond flour (almond meal is NOT the same)
    *   100 grams (about 1 cup) powdered sugar (also called confectioners' sugar or icing sugar)
    *   100 grams (about 1/2 cup) aged egg whites (about 3-4 large egg whites, separated a day or two in advance and stored in an airtight container in the fridge). Room temperature when using.
    *   50 grams (about 1/4 cup) granulated sugar
    *   Pinch of salt
    *   Optional: gel food coloring (not liquid!)

*   **For the Filling (you can choose your favorite, this is for a simple vanilla buttercream):**
    *   100 grams (about 1/2 cup) unsalted butter, softened
    *   200 grams (about 1 3/4 cups) powdered sugar, sifted
    *   1-2 tablespoons milk or cream
    *   1 teaspoon vanilla extract

**Equipment:**

*   Kitchen scale (highly recommended for accuracy)
*   Fine-mesh sieve
*   Stand mixer or hand mixer with whisk attachment
*   Rubber spatula
*   Piping bag fitted with a round tip (about 8-10mm)
*   Baking sheets
*   Parchment paper or silicone baking mats
*   Toothpick or scribe

**Let's Begin!**

**Step 1: Prepare the Dry Ingredients**

![Macaron prepartation step 1](https://storage.googleapis.com/generativeai-downloads/images/macaron_step1.png)


1.  In a large bowl, combine the **almond flour** and **powdered sugar**.
2.  Sift the mixture through a fine-mesh sieve into another bowl. This removes any lumps and ensures a smooth batter. Discard any large pieces left in the sieve.
3. Set the bowl aside.

**Step 2: Whip the Egg Whites**

![Macaron prepartation step 2](https://storage.googleapis.com/generativeai-downloads/images/macaron_step2.png)

1. In a clean and dry mixing bowl, add the room-temperature **egg whites** and **salt**.
2. Using a stand mixer or hand mixer with the whisk attachment, beat on medium speed until soft peaks form.
3. Gradually add the **granulated sugar** a little at a time while continuing to beat. Increase the speed to medium-high.
4. Beat until stiff, glossy peaks form. The meringue should hold its shape and have a shiny appearance. If using gel food coloring, add a couple of drops now and beat until combined.

**Step 3: The Macaronage (Folding)**

![Macaron prepartation step 3](https://storage.googleapis.com/generativeai-downloads/images/macaron_step3.png)

1. Add about 1/3 of the sifted dry ingredient mixture to the meringue.
2. Using a rubber spatula, gently fold the dry ingredients into the meringue. You want to cut through the center, rotate your bowl slightly and pull up from the bottom and over. This is a technique to incorporate air and flatten it.
3. Add the remaining dry ingredients in two more additions, folding each time.
4. Continue the folding process until the batter is smooth, shiny, and flows like lava. When you lift the spatula, it should form a ribbon that slowly falls back into the bowl and disappears in about 20 seconds. This is often referred to as achieving the "ribbon stage" or "lava consistency". Do not over-mix.

**Step 4: Piping**

![Macaron prepartation step 4](https://storage.googleapis.com/generativeai-downloads/images/macaron_step4.png)

1. Line your baking sheets with parchment paper or silicone mats. It might help to trace circles on the parchment paper beforehand.
2. Transfer the batter to your piping bag.
3. Holding the piping bag straight above the baking sheet, pipe even circles about 1.5 inches (3.8 cm) in diameter, leaving some space between each one.
4. Once you finish piping, gently tap the baking sheet on your counter to remove air bubbles in the batter.  
5. If you see a few small bubbles, use a toothpick or scribe to gently pop them.

**Step 5: Drying (Skin Formation)**

![Macaron prepartation step ](https://storage.googleapis.com/generativeai-downloads/images/macaron_step5.png)

1. Allow the piped macaron shells to sit at room temperature for 30-60 minutes, or until a thin skin forms on top. You should be able to gently touch them without the batter sticking to your finger. If your environment is humid, the drying time will be longer.

**Step 6: Baking**

And that's it folk!

*/

/* Markdown (render)
## Chat (recommended)

So far you've used unary calls, but Image-out is actually made to work better with chat mode as it's easier to iterate on an image turn after turn.
*/

// [CODE STARTS]
chat = await ai.chats.create({
  model: MODEL_ID,
  config: {
    responseModalities: ["Text", "Image"]
  }
});

message = "create a photorealistic image of a giraffe with a tiny bird on its head";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

I will generate a photorealistic image of a tall giraffe standing in a sunny savanna, with a small, bright yellow bird perched comfortably on the very top of its head, creating a charming and slightly humorous scene.


<img src="https://i.ibb.co/h1cb0wSw/gir.png" alt="gir" border="0">

*/

// [CODE STARTS]
message = "use a cartoon style instead of photorealistic";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

I will generate a cartoon-style image of a smiling giraffe with long eyelashes and a friendly expression, standing in a vibrantly colored savanna. On the top of its head, a small, cheerful bluebird with big, round eyes is perched, looking equally happy.


<img src="https://i.ibb.co/HDKn0yp6/cartoongir.png" alt="cartoongir" border="0">


*/

// [CODE STARTS]
message = "add a rainbow and some colorful birds";

response = await chat.sendMessage({ message: message });

for (const part of response.candidates[0].content.parts) {
  if (part.text) {
    console.log(part.text);
  } else if (part.inlineData) {
    console.image(part.inlineData.data, "image/png");
  }
}
// [CODE ENDS]

/* Output Sample

I will add a vibrant rainbow arcing across the sky behind the cartoon giraffe and bluebird from the previous image. Several more colorful cartoon birds of different shapes and sizes, such as a red cardinal, a green parrot, and an orange robin, will be flying around the giraffe and perched on its neck and back, creating a whimsical scene.


<img src="https://i.ibb.co/gLRfL32S/cartoongir2.png" alt="cartoongir2" border="0">

*/

/* Markdown (render)
## Next Steps
### Useful documentation references:

Check the [documentation](https://ai.google.dev/gemini-api/docs/image-generation#gemini) for more details about the image generation capabilities of the model. To improve your prompting skills, check out the [Imagen prompt guide](https://ai.google.dev/gemini-api/docs/imagen-prompt-guide) for great advices on creating your prompts.

### Check-out Imagen as well:
The [Imagen](https://ai.google.dev/gemini-api/docs/image-generation#imagen) model is another way to generate images. Check out the [Get Started with Imagen notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_imagen.ipynb) to start playing with it too.

Here are some Imagen examples to get your imagination started on how to use it in creative ways:
*  [Illustrate a book](https://github.com/google-gemini/cookbook/blob/main/examples/Book_illustration.ipynb): Use Gemini and Imagen to create illustration for an open-source book

### Continue your discovery of the Gemini API

Gemini is not only good at generating images, but also at understanding them. Check the [Spatial understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Spatial_understanding.ipynb) guide for an introduction on those capabilities, and the [Video understanding](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb) one for video examples.

*/