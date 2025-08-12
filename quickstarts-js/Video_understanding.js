/* Markdown (render)
# Video understanding with Gemini

Gemini has from the begining been a multimodal model, capable of analyzing all sorts of medias using its [long context window](https://developers.googleblog.com/en/new-features-for-the-gemini-api-and-google-ai-studio/).

[Gemini models](https://ai.google.dev/gemini-api/docs/models/) bring video analysis to a whole new level as illustrated in [this video](https://www.youtube.com/watch?v=Mot-JEU26GQ):

This notebook will show you how to easily use Gemini to perform the same kind of video analysis. Each of them has different prompts that you can select using the dropdown, also feel free to experiment with your own.

You can also check the [live demo](https://aistudio.google.com/apps/bundled/video_analyzer) and try it on your own videos on [AI Studio](https://aistudio.google.com/apps/bundled/video_analyzer).

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
### Select the Gemini model

Video understanding works best with Gemini 2.5 models. You can also select former models to compare their behavior but it is recommended to use at least the 2.0 ones.

For more information about all Gemini models, check the [documentation](https://ai.google.dev/gemini-api/docs/models/gemini) for extended information on each of them.

*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash" // "gemini-2.5-flash", "gemini-2.5-pro","gemini-2.0-flash","gemini-2.5-flash-lite-preview-06-17" 
// [CODE ENDS]

/* Markdown (render)
### Get sample videos

You will start with uploaded videos, as it's a more common use-case, but you will also see later that you can also use Youtube videos.
*/

// [CODE STARTS]
videoUrls = {
  pottery: "https://storage.googleapis.com/generativeai-downloads/videos/Pottery.mp4",
  trailcam: "https://storage.googleapis.com/generativeai-downloads/videos/Jukin_Trailcam_Videounderstanding.mp4",
  postIts: "https://storage.googleapis.com/generativeai-downloads/videos/post_its.mp4",
  userStudy: "https://storage.googleapis.com/generativeai-downloads/videos/user_study.mp4",
};
// [CODE ENDS]

/* Markdown (render)
### Upload the videos

Upload all the videos using the File API. You can find modre details about how to use it in the [Get Started](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Get_Started.js) notebook.

This can take a couple of minutes as the videos will need to be processed and tokenized.
*/

// [CODE STARTS]
async function uploadVideo(name, url) {
  const blob = await fetch(url).then(res => res.blob());
  
  let file = await ai.files.upload({
    file: new File([blob], `${name}.mp4`, { type: blob.type }),
    config: { displayName: `${name}.mp4`, mimeType: blob.type }
  });

  while (file.state === "PROCESSING") {
    console.log(`${name} is PROCESSING...`);
    await new Promise(r => setTimeout(r, 10000));
    file = await ai.files.get({ name: file.name });
  }

  if (file.state === "FAILED") {
    throw new Error(`${name} upload failed: ${file.state}`);
  }

  console.log(`Video processing complete: ${file.uri}`);
  return file;
}

potteryVideo = await uploadVideo("Pottery", videoUrls.pottery);
trailcamVideo = await uploadVideo("Trailcam", videoUrls.trailcam);
postItsVideo = await uploadVideo("Post_its", videoUrls.postIts);
userStudyVideo = await uploadVideo("User_study", videoUrls.userStudy);
// [CODE ENDS]

/* Output Sample

Pottery is PROCESSING...

Video processing complete: https://generativelanguage.googleapis.com/v1main/files/4gab3p11zrk8

Trailcam is PROCESSING...

Trailcam is PROCESSING...

Video processing complete: https://generativelanguage.googleapis.com/v1main/files/it7xrrzjv7ji

Post_its is PROCESSING...

Video processing complete: https://generativelanguage.googleapis.com/v1main/files/coovzle13nh0

User_study is PROCESSING...

Video processing complete: https://generativelanguage.googleapis.com/v1main/files/oj94xg27i9m0

*/

/* Markdown (render)
# Search within videos

First, try using the model to search within your videos and describe all the animal sightings in the trailcam video.

<video controls width="500"><source src="https://storage.googleapis.com/generativeai-downloads/videos/Jukin_Trailcam_Videounderstanding.mp4" type="video/mp4"></video>
*/

// [CODE STARTS]
prompt = `For each scene in this video, generate captions that describe the scene along with any spoken text placed in quotation marks. Place each caption into an object with the timecode of the caption in the video.`;

video = trailcamVideo; // or potteryVideo, postItsVideo, userStudyVideo

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: video.uri, mimeType: "video/mp4" } },
    { text: prompt }
  ]
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

- **00:00 - 00:17**: Two grey foxes are seen foraging on the ground among rocks and leaves.
- **00:17 - 00:35**: A cougar walks through the woods, stopping to sniff the ground before continuing on.
- **00:35 - 00:49**: Two grey foxes are seen at night. One appears to be chasing the other.
- **00:49 - 01:04**: Two grey foxes are seen at night near some rocks. They move quickly, and one appears to be chasing the other around the rocks.
- **01:04 - 01:17**: A cougar walks into the frame from the right and then exits to the left.
- **01:17 - 01:29**: Two cougars are seen at night walking across the frame from right to left.
- **01:29 - 01:51**: A bobcat is seen at night, walking into the frame, then pauses and leaves.
- **01:51 - 01:56**: A brown bear walks slowly through the forest, pausing to sniff the ground, then moves out of the frame.
- **01:56 - 02:04**: A cougar walks through the forest at night.
- **02:04 - 02:23**: Two brown bears, one larger and one smaller, are seen walking together through the forest.
- **02:23 - 02:35**: A grey fox is seen at night, with a city lights in the background. It sniffs the ground and then sits up, looking at the city.
- **02:35 - 02:42**: A bear walks into the frame, sniffing the ground, and then exits to the right.
- **02:42 - 02:51**: A cougar walks through the frame at night, with city lights in the background.
- **02:51 - 03:05**: A cougar walks through the forest at night.
- **03:05 - 03:22**: A large brown bear stands in the forest, looking around, and then walks away.
- **03:22 - 03:55**: Two brown bears, one lighter colored, are seen walking and sniffing the ground in the forest.
- **03:55 - 04:22**: Three brown bears, appearing to be a mother and two cubs, are seen walking and sniffing the ground in the forest.
- **04:22 - 04:29**: A bobcat is seen at night, walking from left to right.
- **04:29 - 04:44**: A bobcat walks towards the camera at night and then exits the frame to the right.
- **04:44 - 04:57**: A bobcat walks towards the camera at night and then exits the frame to the right.
- **04:57 - 05:10**: A cougar is seen at night, sniffing the ground and walking through the forest.

*/

/* Markdown (render)
The prompt used is quite a generic one, but you can get even better results if you cutomize it to your needs (like asking specifically for foxes).

The [live demo on AI Studio](https://aistudio.google.com/apps/bundled/video_analyzer) shows how you can postprocess this output to jump directly to the the specific part of the video by clicking on the timecodes. If you are interested, you can check the [code of that demo on Github](https://github.com/google-gemini/starter-applets/tree/main/video).
*/

/* Markdown (render)
# Extract and organize text

Gemini models can also read what's in the video and extract it in an organized way. You can even use Gemini reasoning capabilities to generate new ideas for you.

<video controls width="400"><source src="https://storage.googleapis.com/generativeai-downloads/videos/post_its.mp4" type="video/mp4"></video>
*/

// [CODE STARTS]
prompt = `Transcribe the sticky notes, organize them and put it in a table. Can you come up with a few more ideas?`;

video = postItsVideo;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: video.uri, mimeType: "video/mp4" } },
    { text: prompt }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

The image shows a whiteboard with &quot;Brainstorm: Project Name&quot; written in red marker at the top. Below it, numerous yellow sticky notes are attached, each with a potential project name written on it in black marker.

Here&#x27;s the transcription of the sticky notes, organized into categories:

**Transcription of Project Names:**

| Category                  | Project Name(s)                                                                                                              |
| :------------------------ | :--------------------------------------------------------------------------------------------------------------------------- |
| **Astronomy/Space**       | Lunar Eclipse, Canis Major, Leo Minor, Andromeda&#x27;s Reach, Stellar Nexus, Orion&#x27;s Belt, Lyra, Sagitta, Celestial Drift, Comet&#x27;s Tail, Astral Forge, Draco, Lynx, Supernova Echo, Galactic Core, Titan, Orion&#x27;s Sword |
| **Mythology/Legend**      | Medusa, Hera, Athena&#x27;s Eye, Athena, Cerberus, Phoenix, Aether, Odin, Prometheus Rising, Chimera Dream, Delphinus, Serpens, Centaurus, Persius Shield |
| **Mathematics/Science**   | Bayes Theorem, Chaos Theory, Riemann&#x27;s Hypothesis, Stokes Theorem, Fractal, Symmetry, Golden Ratio, Infinity Loop, Euler&#x27;s Path, Equilibrium |
| **Abstract/Conceptual**   | Convergence, Chaos Field, Echo, Zephyr, Vector, Pandora&#x27;s Box                                                                |

**A Few More Project Name Ideas:**

1.  **Orion Protocol:** Combines an astronomical reference with a procedural/technical feel.
2.  **Quantum Cascade:** Suggests rapid, powerful progression, leaning into physics.
3.  **Vanguard Zenith:** Evokes leadership and reaching a peak or high point.
4.  **Aetherflux:** Combines a mythological element (aether) with a dynamic, flowing concept.
5.  **Cynosure Engine:** &quot;Cynosure&quot; means a focal point or guiding star, implying direction and a core system.

*/

/* Markdown (render)
# Structure information

Gemini 2.0 is not only able to read text but also to reason and structure about real world objects. Like in this video about a display of ceramics with handwritten prices and notes.

<video controls width="500"><source src="https://storage.googleapis.com/generativeai-downloads/videos/Pottery.mp4" type="video/mp4"></video>
*/

// [CODE STARTS]
prompt = "Give me a table of my items and notes";

video = potteryVideo;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: video.uri, mimeType: "video/mp4" } },
    { text: prompt }
  ],
  systemInstruction: "Don't forget to escape the dollar signs"
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Below is a list of the items and notes observed in the image:

| Item Type | Details                                                                                                          |
| :-------- | :--------------------------------------------------------------------------------------------------------------- |
| Tumblers  | Stack of tumblers (5 total), 2 individual tumblers. Note: &quot;#5 ARTICHOKE DOUBLE DIP, TUMBLERS # 4&quot;h x 3&quot;d -ISH $20&quot; |
| Bowls     | 2 small bowls. Note: &quot;small bowls 3.5&quot;h x 6.5&quot;d $35&quot;                                                           |
| Bowls     | 2 medium bowls. Note: &quot;med bowls 4&quot;h x 7&quot;d $40&quot;                                                              |
| Glaze Test | Small ceramic piece. Note: &quot;#6 GEMINI DOUBLE DIP SLOW COOL&quot;                                                      |

*/

/* Markdown (render)
# Analyze screen recordings for key moments

You can also use the model to analyze screen recordings. Let's say you're doing user studies on how people use your product, so you end up with lots of screen recordings, like this one, that you have to manually comb through.
With just one prompt, the model can describe all the actions in your video.

<video controls width="400"><source src="https://storage.googleapis.com/generativeai-downloads/videos/user_study.mp4" type="video/mp4"></video>
*/

// [CODE STARTS]
prompt = "Generate a paragraph that summarizes this video. Keep it to 3 to 5 sentences with corresponding timecodes.";

video = userStudyVideo;

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: video.uri, mimeType: "video/mp4" } },
    { text: prompt }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

The video demonstrates the features of a &quot;My Garden App,&quot; displaying a list of plants with prices, &quot;Like,&quot; and &quot;Add to Cart&quot; options (0:00-0:09). The user interacts with the app by liking several plants, including Rose Plant, Fern, Cactus, and Hibiscus (0:10-0:23). They then proceed to add Fern, Cactus, and Hibiscus to the shopping cart (0:13-0:25).

Navigating to the &quot;Cart&quot; tab reveals the added items and their total cost (0:30-0:33). Subsequently, the &quot;Profile&quot; tab confirms the number of liked plants and cart items based on these actions (0:33-0:35). The video concludes with the user returning to the home screen to like another plant and add an Orchid to the cart, though the cart&#x27;s content isn&#x27;t shown updated with these last additions (0:37-0:48).

*/

/* Markdown (render)
# Analyze youtube videos

On top of using your own videos you can also ask Gemini to get a video from Youtube and analyze it. He's an example using the keynote from Google IO 2023. Guess what the main theme was?

*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      text: "Find all the instances where Sundar says \"AI\". Provide timestamps and broader context for each instance."
    },
    {
      fileData: {
        fileUri: "https://www.youtube.com/watch?v=ixRanV-rdAQ"
      }
    }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Sundar Pichai says &quot;AI&quot; in the video at the following instances:

1.  **0:29:** &quot;As you may have heard, **AI** is having a very busy year.&quot;
    *   **Context:** Sundar opens the keynote, immediately highlighting the prominence of AI in the current technological landscape.

2.  **0:38:** &quot;Seven years into our journey as an **AI**-first company...&quot;
    *   **Context:** Sundar emphasizes Google&#x27;s long-term commitment and strategic focus on Artificial Intelligence.

3.  **0:45:** &quot;We have an opportunity to make **AI** even more helpful...&quot;
    *   **Context:** Sundar outlines the broad vision for AI, aiming to enhance its utility for individuals, businesses, and communities.

4.  **0:54:** &quot;We&#x27;ve been applying **AI** to make our products radically more helpful for a while.&quot;
    *   **Context:** Sundar refers to Google&#x27;s historical integration of AI into its products to improve their functionality.

5.  **0:59:** &quot;With generative **AI**, we are taking the next step.&quot;
    *   **Context:** Sundar introduces the specific focus on generative AI as the frontier for new product innovations.

6.  **1:16:** &quot;...how generative **AI** is helping to evolve our products...&quot;
    *   **Context:** Sundar transitions to showcasing practical applications of generative AI within Google&#x27;s product suite.

7.  **1:41:** &quot;...advanced writing features powered by **AI**.&quot;
    *   **Context:** Sundar explains how AI underpins features like Smart Compose, improving writing assistance in Gmail.

8.  **3:02:** &quot;...the early days of Street View, **AI** has stitched together billions of panoramic images...&quot;
    *   **Context:** Sundar details AI&#x27;s role in creating the immersive Street View experience in Google Maps.

9.  **3:15:** &quot;...which uses **AI** to create a high-fidelity representation of a place...&quot;
    *   **Context:** Sundar elaborates on Immersive View in Maps, highlighting AI&#x27;s function in generating realistic virtual environments.

10. **5:09:** &quot;Another product made better by **AI** is Google Photos.&quot;
    *   **Context:** Sundar introduces Google Photos as another example of a product significantly enhanced by AI.

11. **5:15:** &quot;It was one of our first **AI**-native products.&quot;
    *   **Context:** Sundar describes Google Photos as a pioneering product built with AI at its core since its inception.

12. **5:41:** &quot;**AI** advancements give us more powerful ways to do this.&quot;
    *   **Context:** Sundar explains that breakthroughs in AI enable more sophisticated photo editing capabilities.

13. **5:49:** &quot;...uses **AI**-powered computational photography to remove unwanted distractions.&quot;
    *   **Context:** Sundar specifically mentions Magic Eraser&#x27;s use of AI to intelligently clean up photos.

14. **5:59:** &quot;...semantic understanding and generative **AI**, you can do much more...&quot;
    *   **Context:** Sundar refers to Magic Editor&#x27;s advanced capabilities, powered by both semantic understanding and generative AI.

15. **7:41:** &quot;...how **AI** can help you in moments that matter.&quot;
    *   **Context:** Sundar summarizes the collective impact of AI-powered features across various Google products.

16. **7:49:** &quot;...deliver the full potential of **AI** across the products you know and love.&quot;
    *   **Context:** Sundar expresses Google&#x27;s commitment to broadly integrating AI into its existing popular products.

17. **8:24:** &quot;Making **AI** helpful for everyone is the most profound way we will advance our mission.&quot;
    *   **Context:** Sundar reiterates Google&#x27;s core mission, emphasizing that AI is central to making information universally accessible and useful.

18. **8:52:** &quot;...building and deploying **AI** responsibly so that everyone can benefit equally.&quot;
    *   **Context:** Sundar highlights the critical importance of ethical and responsible development and deployment of AI.

19. **9:03:** &quot;Our ability to make **AI** helpful for everyone relies on continuously advancing our foundation models.&quot;
    *   **Context:** Sundar connects the goal of helpful AI directly to ongoing progress in developing powerful foundation models.

20. **11:27:** &quot;It uses **AI** to better detect malicious scripts...&quot;
    *   **Context:** Sundar discusses Sec-PaLM 2&#x27;s application of AI to improve cybersecurity threat detection.

21. **12:14:** &quot;You can imagine an **AI** collaborator that helps radiologists interpret images and communicate the results.&quot;
    *   **Context:** Sundar envisions future applications of Med-PaLM 2, where AI acts as a collaborative tool for medical professionals.

22. **12:46:** &quot;...decade-long journey to bring **AI** in responsible ways to billions of people.&quot;
    *   **Context:** Sundar reinforces Google&#x27;s long-term commitment to making AI accessible and beneficial to a global audience.

23. **12:58:** &quot;Looking back at the defining **AI** breakthroughs over the last decade...&quot;
    *   **Context:** Sundar reflects on Google&#x27;s significant contributions and foundational advancements in the field of Artificial Intelligence.

24. **14:10:** &quot;We&#x27;re also deeply investing in **AI** responsibility.&quot;
    *   **Context:** Sundar emphasizes Google&#x27;s dedicated focus on ensuring AI is developed and used ethically and safely.

25. **15:11:** &quot;James will talk about our responsible approach to **AI** later.&quot;
    *   **Context:** Sundar introduces the next segment of the keynote, which will delve deeper into Google&#x27;s ethical framework for AI.

*/

/* Markdown (render)
## Analyze specific parts of videos using clipping intervals

Sometimes you want to look for specific parts of your videos. You can define time offsets on your request, pointing to the model which specific video interval you are more interested about.

**Note:** The `videoMetadata` that you will inform must be representing the time offsets in seconds.

In this example, you are using this video, from [Google I/O 2025 keynote](https://www.youtube.com/watch?v=XEzRZ35urlk) and asking the model to consider specifically the time offset between 20min50s and 26min10s.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      fileData: {
        fileUri: "https://www.youtube.com/watch?v=XEzRZ35urlk"
      },
      videoMetadata: {
        startOffset: "1250s",
        endOffset: "1570s"
      }
    },
    {
      text: "Please summarize the video in 3 sentences."
    }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Demis Hassabis, co-founder of DeepMind, introduces Google DeepMind and its mission to build Artificial General Intelligence (AGI) to benefit humanity, showcasing recent advancements like AlphaFold 3 and GNoME enabled by Google&#x27;s powerful AI infrastructure. He then announces Gemini 1.5 Flash, a new, lighter-weight model designed for speed, efficiency, and multimodal reasoning, with a large context window now available to developers. Finally, he unveils &quot;Project Astra,&quot; a long-term endeavor to create a universal AI agent that can understand and respond to the complex and dynamic world in real-time, aiming for natural, proactive, teachable, and personal interactions.

*/

/* Markdown (render)
You can also use clipping intervals for videos uploaded to the File API as also inline videos on your prompts (remembering that inline data cannot exceed 20MB in size).
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      fileData: {
        fileUri: trailcamVideo.uri,
        mimeType: trailcamVideo.mimeType
      },
      videoMetadata: {
        startOffset: "60s",
        endOffset: "120s"
      }
    },
    {
      text: "Summarize this video in few short bullets"
    }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Here&#x27;s a summary of the video in a few short bullet points:

*   Multiple mountain lions (also known as pumas or cougars) are seen, including what appears to be an adult and a smaller individual (possibly a cub).
*   A bobcat (or possibly a lynx) is captured several times, notably moving quickly in one instance and sniffing the ground in another.
*   A large black bear makes an appearance, walking through the forest in daylight.
*   Most of the footage is captured at night using an infrared camera, with the animals&#x27; eyes reflecting brightly in the light.
*   The animals are generally seen walking or casually moving through the natural habitat.

*/

/* Markdown (render)
## Customize the number of video frames per second (FPS) analyzed

By default, the Gemini API extract 1 (one) FPS to analyze your videos. But this amount may be too much (for videos with less activities, like a lecture) or to preserve more detail in fast-changing visuals, a higher FPS should be selected.

In this scenario, you are using one specific interval of one Nascar pit-stop as also you will capture a higher number of FPS (in this case, 24 FPS).
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      fileData: {
        fileUri: 'https://www.youtube.com/watch?v=McN0-DpyHzE'
      },
      videoMetadata: {
        startOffset: '15s',
        endOffset: '35s',
        fps: 24
      }
    },
    {
      text: 'How many tires were changed? Front tires or rear tires?'
    }
  ]
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Two tires were changed in the video:
*   One front tire (specifically, the front right tire) was changed from approximately 00:18.000 to 00:22.292.
*   One rear tire (specifically, the rear right tire) was changed from approximately 00:28.292 to 00:31.750.

*/

/* Markdown (render)
Once again, you can check the  [live demo on AI Studio](https://aistudio.google.com/apps/bundled/video_analyzer) shows an example on how to postprocess this output. Check the [code of that demo](https://github.com/google-gemini/starter-applets/tree/main/video) for more details.
*/

/* Markdown (render)
# Next Steps

Try with you own videos using the [AI Studio's live demo](https://aistudio.google.com/apps/bundled/video_analyzer) or play with the examples from this notebook (in case you haven't seen, there are other prompts you can try in the dropdowns).

For more examples of the Gemini capabilities, check the other guide from the [Cookbook](https://github.com/google-gemini/cookbook/). You'll learn how to use the [Live API](https://github.com/google-gemini/cookbook/tree/main/quickstarts/Get_started_LiveAPI.ipynb), juggle with [multiple tools](https://github.com/google-gemini/cookbook/tree/main/quickstarts/Get_started_LiveAPI_tools.ipynb) or use Gemini for [spatial understanding](https://github.com/google-gemini/cookbook/tree/main/quickstarts/Spatial_understanding.ipynb) abilities.

The [examples](https://github.com/google-gemini/cookbook/tree/main/examples/) folder from the cookbook is also full of nice code samples illustrating creative ways to use Gemini multimodal capabilities and long-context.
*/