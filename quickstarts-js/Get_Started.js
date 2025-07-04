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
# Gemini API: Getting started with Gemini models

The new **[Google Gen AI SDK](https://googleapis.github.io/js-genai)** provides a unified interface to [Gemini models](https://ai.google.dev/gemini-api/docs/models) through both the [Gemini Developer API](https://ai.google.dev/gemini-api/docs) and the Gemini API on [Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/overview). With a few exceptions, code that runs on one platform will run on both. This notebook uses the Developer API.

This notebook will walk you through:
* Installing and setting-up the Google GenAI SDK
* Text and multimodal prompting
* Counting tokens
* Setting system instructions
* Configuring safety filters
* Initiating a multi-turn chat
* Controlling generated output
* Using function calling
* Generating a content stream
* Using file uploads

More details about this new SDK on the [documentation](https://ai.google.dev/gemini-api/docs/sdks).

## Setup
### Install SDK and set-up the client
*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite-preview-06-17", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
## Send text prompts

Use the `generateContent` method to generate responses to your prompts. You can pass text directly to `generateContent` and use the `.text` property to get the text content of the response. Note that the `.text` field will work when there's only one part in the output.
*/

// [CODE STARTS]
const resp = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "What's the largest planet in our solar system?"
});
console.log(resp.text);
// [CODE ENDS]

/* Output Sample

The largest planet in our solar system is **Jupiter**.

*/

/* Markdown (render)
## Count tokens

Tokens serve as the fundamental input units for Gemini models. You can use the `countTokens` method to calculate the number of input tokens prior to making a request to the Gemini API, and the `totalTokens` property to access the total token count after the request is processed.
*/

// [CODE STARTS]
const resp2 = await ai.models.countTokens({
    model: MODEL_ID,
    contents: 'What is the purpose of life?',
});
console.log(resp2.totalTokens);
// [CODE ENDS]

/* Output Sample

8

*/

/* Markdown (render)
## Send multimodal prompts

Use Gemini 2.0 model (`gemini-2.0-flash`) or a later version, a multimodal model that supports multimodal prompts. You can include text, PDF documents, images, audio and video in your prompt requests and get text or code responses.

In this first example, you'll download an image from a specified URL, save it as a byte stream and then write those bytes to a local file named `jetpack.png`.
*/

// [CODE STARTS]
const IMAGE_URL = "https://cors-anywhere.herokuapp.com/https://storage.googleapis.com/generativeai-downloads/data/jetpack.png";

// Fetch the image as a Blob
imageBlob = await fetch(IMAGE_URL).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
  const reader = new FileReader();
  reader.onloadend = () => resolve(reader.result.split(',')[1]); // Get only base64 string
  reader.readAsDataURL(imageBlob);
});
// [CODE ENDS]


/* Markdown (render)
In this second example, you'll open a previously saved image, create a thumbnail of it and then generate a short blog post based on the thumbnail, displaying both the thumbnail and the generated blog post.
*/


// [CODE STARTS]
const response = await ai.models.generateContent({
  model: "gemini-2.0-flash",
  contents: [
    {
      inlineData: {
        data: imageDataUrl,
        mimeType: "image/png"
      }
    },
    "Write a short and engaging blog post based on this picture."
  ]
});

console.image(imageDataUrl);

console.log(response.text)
// [CODE ENDS]

/* Output Sample

<img src="https://iili.io/FcTOoib.png" alt="FcTOoib.md.png" border="0">

Okay, here&#x27;s a fun blog post based on the image:

**Future Commute? Jetpack Backpack is Here (Concept!)**

Tired of traffic jams? Dreaming of soaring above the crowds?  Well, maybe you should check this design out! This hand-drawn concept for a &quot;Jetpack Backpack&quot; has all the details.

This isn&#x27;t just any backpack; it&#x27;s a vision of personal flight. Imagine:

*   **Lightweight and Normal-Looking:** This sleek design isn&#x27;t bulky or unwieldy. It looks like a regular backpack, making it discrete.
*   **Fits an 18&quot; Laptop:**  It&#x27;s practical too! You can carry your work with you...into the sky.
*   **Steam-Powered and Clean:**  This concept is eco-conscious, running on steam for a &quot;green&quot; flying experience.
*   **Retractable Boosters:** When you&#x27;re ready to fly, these pop out for a quick lift-off.
*   **USB-C Charging &amp; 15-Min Battery Life:** Keep that laptop going as you touch down again.

Sure, it&#x27;s just a concept for now. But it&#x27;s a great thought experiment. Would you trade your car for a steam-powered jetpack backpack? Let me know in the comments!

*/


/* Markdown (render)
## Configure model parameters

You can include parameter values in each call that you send to a model to control how the model generates a response. Learn more about [experimenting with parameter values](https://ai.google.dev/gemini-api/docs/text-generation?lang=node#configure).
*/

// [CODE STARTS]
const response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "Tell me how the internet works, but pretend I'm a puppy who only understands squeaky toys.",
  config: {
    temperature: 0.4,
    topP: 0.95,
    topK: 20,
    candidateCount: 1,
    seed: 5,
    stopSequences: ["STOP!"],
    presencePenalty: 0.0,
    frequencyPenalty: 0.0,
  },
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

Woof woof! You! Yes, YOU! You have a *squeak*! A very important *squeak* you want to send to your friend, the fluffy cat, who lives far, far away!

**You have a Squeak!** (That&#x27;s your message, your picture of a squirrel, your video of a bouncy ball!)
*Squeak!*

**Sending Your Squeak!**
You want to throw your *squeak*! But it&#x27;s too far to throw! So, your *squeak* goes to a special box near your human. It&#x27;s like a **Squeaky Toy Launcher**!
*WHIZZ! Squeak!*

**Invisible Paths!**
This **Squeaky Toy Launcher** sends your *squeak* onto invisible, wiggly, super-duper long paths! Paths that go under the grass! Paths that go over the trees! Paths that go all the way to the fluffy cat&#x27;s house!
*Squeak-squeak-squeak-squeak!* (Imagine tiny squeaks zooming!)

**Giant Squeaky Toy Piles!**
Sometimes, your *squeak* doesn&#x27;t go straight to the fluffy cat. Sometimes it goes to a **GIANT, GIANT pile of squeaky toys**! These are like the biggest squeaky toy closets in the world! When you want to see a picture of a squirrel, you&#x27;re asking one of these *big squeaky toy piles* for *their* squirrel-squeak!
*WOOF! Squeak! (That&#x27;s the squirrel picture popping up!)*

**Getting Squeaks Back!**
And when the fluffy cat sends *you* a *squeak* (maybe a video of a laser pointer!), it comes back on those same invisible paths! *Squeak! Squeak! Squeak!* Right to your **Squeaky Toy Launcher** box, and then to you!
*Wag wag! Pant pant!*

**Lots of Little Squeaks!**
It&#x27;s not one big *WHOOSH-SQUEAK!* It&#x27;s lots of little *squeaky-bits* that all travel together and then magically become one big *SQUEAKY THING* when they get to you!
*Sniff sniff! Squeak! Good boy!*

So, the internet is just **ALL THE SQUEAKS!** Going everywhere! All the time! *WOOF! Squeak!* Now, where&#x27;s that ball?

*/

/* Markdown (render)
## Configure safety filters

The Gemini API provides safety filters that you can adjust across multiple filter categories to restrict or allow certain types of content. You can use these filters to adjust what is appropriate for your use case. See the [Configure safety filters](https://ai.google.dev/gemini-api/docs/safety-settings) page for details.


In this example, you'll use a safety filter to only block highly dangerous content, when requesting the generation of potentially disrespectful phrases.
*/

// [CODE STARTS]
const prompt = `
  Write a list of 2 disrespectful things that I might say to the universe after stubbing my toe in the dark.
`;

const safetySettings = [
  {
    category: "HARM_CATEGORY_DANGEROUS_CONTENT",
    threshold: "BLOCK_ONLY_HIGH",
  }
];

const response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: prompt,
  config: {
    safetySettings: safetySettings,
  },
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

Here are two disrespectful things you might say to the universe after stubbing your toe in the dark:

1.  &quot;Is this your idea of a good time, universe? Because it&#x27;s just sad.&quot;
2.  &quot;You know, for an infinite expanse of spacetime, you&#x27;re surprisingly petty.&quot;

*/

/* Markdown (render)
## Start a multi-turn chat

The Gemini API enables you to have freeform conversations across multiple turns.

Next you'll set up a helpful coding assistant:
*/

// [CODE STARTS]
system_instruction = "You are an expert software developer and a helpful coding assistant. You are able to generate high-quality code in any programming language."

chatConfig = {
    "system_instruction":system_instruction
}

chat = ai.chats.create({
    model:MODEL_ID,
    config:chatConfig
})
// [CODE ENDS]

/* Markdown (render)
Use `chat.sendMessage` to pass a message back and receive a response.
*/

// [CODE STARTS]
response = await chat.sendMessage({
    message: "Write a python function that checks if a year is a leap year."
});

console.log(response.text)
// [CODE ENDS]

/* Output Sample

You can write a Python function to check for a leap year based on the standard Gregorian calendar rules.

Here are the rules for a leap year:
1.  A year is a leap year if it is divisible by 4.
2.  However, if the year is divisible by 100, it is **not** a leap year, unless...
3.  The year is also divisible by 400. In that case, it **is** a leap year.

Let&#x27;s implement this:

```python
def is_leap_year(year):
    &quot;&quot;&quot;
    Checks if a given year is a leap year according to the Gregorian calendar rules.

    A year is a leap year if:
    1. It is divisible by 400. (e.g., 2000, 2400)
    OR
    2. It is divisible by 4 BUT NOT by 100. (e.g., 2004, 2020)

    Otherwise, it is not a leap year. (e.g., 1900, 2100 are NOT leap years; 2003, 2005 are NOT leap years)

    Args:
        year (int): The year to check. Must be an integer.

    Returns:
        bool: True if the year is a leap year, False otherwise.
    &quot;&quot;&quot;
    if not isinstance(year, int):
        raise TypeError(&quot;Year must be an integer.&quot;)
    if year &lt; 1: # Leap year rules generally apply to positive years in the common era
        # You could decide how to handle historical or negative years.
        # For simplicity, we&#x27;ll raise an error or apply the rule directly.
        # For this function, let&#x27;s assume valid positive years.
        # If you need to handle years before the Gregorian calendar (1582),
        # the rules are different and more complex.
        raise ValueError(&quot;Year must be a positive integer.&quot;)

    # Apply the leap year rules
    if (year % 400 == 0):
        return True
    elif (year % 100 == 0):
        return False
    elif (year % 4 == 0):
        return True
    else:
        return False

# --- Alternative more concise implementation ---
def is_leap_year_concise(year):
    &quot;&quot;&quot;
    Checks if a given year is a leap year using a concise boolean expression.
    Same logic as is_leap_year.
    &quot;&quot;&quot;
    if not isinstance(year, int):
        raise TypeError(&quot;Year must be an integer.&quot;)
    if year &lt; 1:
        raise ValueError(&quot;Year must be a positive integer.&quot;)

    # A year is a leap year if (divisible by 400) OR (divisible by 4 AND NOT divisible by 100)
    return (year % 400 == 0) or \
           (year % 4 == 0 and year % 100 != 0)


# --- Test Cases ---
print(&quot;--- Using is_leap_year ---&quot;)
print(f&quot;Is 2000 a leap year? {is_leap_year(2000)}&quot;) # True (divisible by 400)
print(f&quot;Is 1900 a leap year? {is_leap_year(1900)}&quot;) # False (divisible by 100, but not 400)
print(f&quot;Is 2020 a leap year? {is_leap_year(2020)}&quot;) # True (divisible by 4, not by 100)
print(f&quot;Is 2023 a leap year? {is_leap_year(2023)}&quot;) # False (not divisible by 4)
print(f&quot;Is 1600 a leap year? {is_leap_year(1600)}&quot;) # True
print(f&quot;Is 2100 a leap year? {is_leap_year(2100)}&quot;) # False

print(&quot;\n--- Using is_leap_year_concise ---&quot;)
print(f&quot;Is 2000 a leap year? {is_leap_year_concise(2000)}&quot;)
print(f&quot;Is 1900 a leap year? {is_leap_year_concise(1900)}&quot;)
print(f&quot;Is 2020 a leap year? {is_leap_year_concise(2020)}&quot;)
print(f&quot;Is 2023 a leap year? {is_leap_year_concise(2023)}&quot;)

# --- Error Handling Examples ---
try:
    is_leap_year(&quot;abc&quot;)
except TypeError as e:
    print(f&quot;\nError: {e}&quot;)

try:
    is_leap_year(0)
except ValueError as e:
    print(f&quot;Error: {e}&quot;)
```

**Explanation:**

1.  **`is_leap_year(year)` Function:**
    *   **Input Validation:** It first checks if `year` is an integer using `isinstance(year, int)`. If not, it raises a `TypeError`. It also checks if the year is positive, raising a `ValueError` for years less than 1.
    *   **Rule 3 (Divisible by 400):** `if (year % 400 == 0): return True`
        This is the strongest rule. If a year is divisible by 400 (e.g., 2000, 2400), it&#x27;s definitely a leap year. This condition is checked first because it overrides the 100-year rule.
    *   **Rule 2 (Divisible by 100, but not 400):** `elif (year % 100 == 0): return False`
        If the year wasn&#x27;t divisible by 400, but *is* divisible by 100 (e.g., 1900, 2100), then it&#x27;s *not* a leap year.
    *   **Rule 1 (Divisible by 4, but not 100 or 400):** `elif (year % 4 == 0): return True`
        If the year wasn&#x27;t handled by the previous two (meaning it&#x27;s not divisible by 100, and thus not by 400), and it *is* divisible by 4 (e.g., 2024, 2028), then it&#x27;s a leap year.
    *   **Catch-all:** `else: return False`
        If none of the above conditions are met (i.e., the year is not divisible by 4), it&#x27;s not a leap year.

2.  **`is_leap_year_concise(year)` Function:**
    *   This version combines all the logic into a single boolean expression, which is often considered more &quot;Pythonic&quot; for such clear logical conditions.
    *   `return (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)` directly translates the rules:
        *   `(year % 400 == 0)`: Is it divisible by 400?
        *   `or`: OR
        *   `(year % 4 == 0 and year % 100 != 0)`: Is it divisible by 4 AND NOT divisible by 100?

Both functions achieve the same result, but the concise version is often preferred for its readability once you understand the combined logic.

*/

/* Markdown (render)
Here's another example using your new helpful coding assistant:
*/

// [CODE STARTS]
response = await chat.sendMessage({ message: "Okay, write a unit test of the generated function." })

console.log(response.text)
// [CODE ENDS]

/* Output Sample

Okay, let&#x27;s write a unit test for the `is_leap_year` function using Python&#x27;s built-in `unittest` module.

First, make sure you have the `is_leap_year` function defined. I&#x27;ll include the `is_leap_year_concise` version in the test for demonstration, as they share the same logic.

```python
# Save this as a Python file, e.g., &#x27;test_leap_year.py&#x27;

import unittest

# --- The function to be tested (copy from previous answer or ensure it&#x27;s in a module you can import) ---
def is_leap_year(year):
    &quot;&quot;&quot;
    Checks if a given year is a leap year according to the Gregorian calendar rules.
    &quot;&quot;&quot;
    if not isinstance(year, int):
        raise TypeError(&quot;Year must be an integer.&quot;)
    if year &lt; 1:
        raise ValueError(&quot;Year must be a positive integer.&quot;)

    if (year % 400 == 0):
        return True
    elif (year % 100 == 0):
        return False
    elif (year % 4 == 0):
        return True
    else:
        return False

# You can also test the concise version if you prefer
def is_leap_year_concise(year):
    if not isinstance(year, int):
        raise TypeError(&quot;Year must be an integer.&quot;)
    if year &lt; 1:
        raise ValueError(&quot;Year must be a positive integer.&quot;)
    return (year % 400 == 0) or \
           (year % 4 == 0 and year % 100 != 0)

# --- Unit Test Class ---

class TestIsLeapYear(unittest.TestCase):
    &quot;&quot;&quot;
    Unit tests for the is_leap_year function.
    &quot;&quot;&quot;

    # Test cases for years that ARE leap years
    def test_leap_years_divisible_by_400(self):
        self.assertTrue(is_leap_year(2000), &quot;2000 should be a leap year (divisible by 400)&quot;)
        self.assertTrue(is_leap_year(1600), &quot;1600 should be a leap year (divisible by 400)&quot;)
        self.assertTrue(is_leap_year(2400), &quot;2400 should be a leap year (divisible by 400)&quot;)

    def test_leap_years_divisible_by_4_not_100(self):
        self.assertTrue(is_leap_year(2004), &quot;2004 should be a leap year (divisible by 4, not 100)&quot;)
        self.assertTrue(is_leap_year(2020), &quot;2020 should be a leap year (divisible by 4, not 100)&quot;)
        self.assertTrue(is_leap_year(1996), &quot;1996 should be a leap year (divisible by 4, not 100)&quot;)
        self.assertTrue(is_leap_year(4), &quot;4 should be a leap year (divisible by 4, not 100)&quot;)


    # Test cases for years that are NOT leap years
    def test_non_leap_years_divisible_by_100_not_400(self):
        self.assertFalse(is_leap_year(1900), &quot;1900 should NOT be a leap year (divisible by 100, not 400)&quot;)
        self.assertFalse(is_leap_year(2100), &quot;2100 should NOT be a leap year (divisible by 100, not 400)&quot;)
        self.assertFalse(is_leap_year(1800), &quot;1800 should NOT be a leap year (divisible by 100, not 400)&quot;)

    def test_non_leap_years_not_divisible_by_4(self):
        self.assertFalse(is_leap_year(2023), &quot;2023 should NOT be a leap year (not divisible by 4)&quot;)
        self.assertFalse(is_leap_year(2021), &quot;2021 should NOT be a leap year (not divisible by 4)&quot;)
        self.assertFalse(is_leap_year(7), &quot;7 should NOT be a leap year (not divisible by 4)&quot;)

    # Test cases for error handling (TypeError and ValueError)
    def test_type_error_for_non_integer_input(self):
        with self.assertRaises(TypeError):
            is_leap_year(&quot;abcd&quot;)
        with self.assertRaises(TypeError):
            is_leap_year(2000.5)
        with self.assertRaises(TypeError):
            is_leap_year(None)

    def test_value_error_for_non_positive_year(self):
        with self.assertRaises(ValueError):
            is_leap_year(0)
        with self.assertRaises(ValueError):
            is_leap_year(-100)

    # You can add tests specifically for the concise version if you want to ensure both work
    def test_leap_years_divisible_by_400_concise(self):
        self.assertTrue(is_leap_year_concise(2000))
        self.assertFalse(is_leap_year_concise(1900))
        self.assertTrue(is_leap_year_concise(2024))
        self.assertFalse(is_leap_year_concise(2023))


# This allows running the tests directly from the script
if __name__ == &#x27;__main__&#x27;:
    unittest.main(argv=[&#x27;first-arg-is-ignored&#x27;], exit=False) # Use exit=False to allow running in interactive environments
```

### How to Run the Tests:

1.  **Save the code:** Save the entire code block above into a file named `test_leap_year.py` (or any other name starting with `test_`).
2.  **Run from terminal:** Open your terminal or command prompt, navigate to the directory where you saved the file, and run:
    ```bash
    python -m unittest test_leap_year.py
    ```
    or simply
    ```bash
    python test_leap_year.py
    ```

### Explanation of the Unit Test:

*   **`import unittest`**: Imports the necessary `unittest` framework.
*   **`class TestIsLeapYear(unittest.TestCase):`**: Defines a test class that inherits from `unittest.TestCase`. This is crucial as it provides all the assertion methods (like `assertTrue`, `assertFalse`, `assertRaises`, etc.).
*   **`def test_...` methods**: Each method starting with `test_` is considered a separate test case by the `unittest` runner.
*   **`self.assertTrue(condition, message)`**: Asserts that the `condition` is `True`. The optional `message` is displayed if the assertion fails, helping in debugging.
*   **`self.assertFalse(condition, message)`**: Asserts that the `condition` is `False`.
*   **`with self.assertRaises(ExceptionType):`**: This is used to test if a specific exception is raised by a block of code.
    *   For example, `with self.assertRaises(TypeError): is_leap_year(&quot;abcd&quot;)` ensures that `is_leap_year(&quot;abcd&quot;)` will indeed raise a `TypeError`. If it doesn&#x27;t, the test fails.
*   **`if __name__ == &#x27;__main__&#x27;:`**: This standard Python construct ensures that `unittest.main()` is called only when the script is executed directly (not when imported as a module).
    *   `argv=[&#x27;first-arg-is-ignored&#x27;]`: This is a common workaround when running `unittest.main()` in certain environments (like some IDEs) where the first argument might be the script name itself, which `unittest.main()` might misinterpret.
    *   `exit=False`: Useful if you are running tests within an interactive session (like an IDE&#x27;s test runner) and don&#x27;t want the script to exit immediately after tests complete.

This comprehensive set of tests covers the core logic (leap/non-leap years based on rules) and also robustly checks for error handling with invalid inputs.

*/

/* Markdown (render)
## Save and resume a chat

In the JS SDK, chat history is represented as a plain array of messages, making it easy to serialize and resume sessions.

#### 1. Save the chat history
*/

// [CODE STARTS]
chatHistory = chat.getHistory()
// [CODE ENDS]

/* Markdown (render)
#### 2. Resume later
*/

// [CODE STARTS]
resumedChat = await ai.chats.create({
  model: MODEL_ID,
  config: chatConfig,
  history: chatHistory
});
response = await resumedChat.sendMessage({ message: "What was the name of the function again?" })
console.log(response.text)
// [CODE ENDS]

/* Output Sample

The name of the function to check if a year is a leap year is:

`is_leap_year`

And the more concise alternative version was named:

`is_leap_year_concise`

*/

// [CODE STARTS]
const recipeSchema = {
  type: "array",
  items: {
    type: "object",
    properties: {
      recipeName: { type: "string" },
      recipeDescription: { type: "string" },
      recipeIngredients: {
        type: "array",
        items: { type: "string" },
      },
    },
    required: ["recipeName", "recipeDescription", "recipeIngredients"],
  },
};


response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "Provide a popular cookie recipe and its ingredients.",
  config: {
    responseMimeType: "application/json",
    responseSchema: recipeSchema,
  },
});

const recipes = JSON.parse(response.text);
console.log(JSON.stringify(recipes, null, 4));
// [CODE ENDS]

/* Output Sample

[
    {
        &quot;recipeDescription&quot;: &quot;A classic American cookie, beloved for its chewy center, crisp edges, and melted chocolate chips. Perfect for any occasion.&quot;,
        &quot;recipeIngredients&quot;: [
            &quot;2 1/4 cups all-purpose flour&quot;,
            &quot;1 teaspoon baking soda&quot;,
            &quot;1 teaspoon salt&quot;,
            &quot;1 cup (2 sticks) unsalted butter, softened&quot;,
            &quot;3/4 cup granulated sugar&quot;,
            &quot;3/4 cup packed light brown sugar&quot;,
            &quot;1 teaspoon vanilla extract&quot;,
            &quot;2 large eggs&quot;,
            &quot;2 cups (12 ounces) semi-sweet chocolate chips&quot;
        ],
        &quot;recipeName&quot;: &quot;Classic Chocolate Chip Cookies&quot;
    }
]

*/

/* Markdown (render)
## Generate Images

Gemini can output images directly as part of a conversation:
*/

// [CODE STARTS]
Modality = module.Modality

const response = await ai.models.generateContent({
  model: "gemini-2.0-flash-preview-image-generation",
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

I will generate a 3D rendering of a whimsical scene. The central figure will be a pink pig, complete with small, delicate wings and a dapper grey top hat perched jauntily on its head. This unusual creature will be soaring above a sprawling futuristic cityscape. The city will feature sleek, modern buildings with sharp angles and glowing accents, but it will also be integrated with lush greenery, with trees and vines growing on the structures, creating a unique blend of nature and technology. The overall color palette will be vibrant, with the pink of the pig contrasting against the metallic and green hues of the city below.

<img src="https://iili.io/FcTOzfj.png" alt="FcTOzfj.md.png" border="0">

*/

/* Markdown (render)
[Imagen](./Get_started_imagen.ipynb) is another way to generate images. See the [documentation](https://ai.google.dev/gemini-api/docs/image-generation#choose-a-model) for recommendations on where to use each one.
*/

/* Markdown (render)
## Generate content stream

By default, the model returns a response after completing the entire generation process. You can also use the `generate_content_stream` method to stream the response as it's being generated, and the model will return chunks of the response as soon as they're generated.

Note that if you're using a thinking model, it'll only start streaming after finishing its thinking process.
*/

// [CODE STARTS]
const response = await ai.models.generateContentStream({
    model: "gemini-2.5-flash",
    contents: "Tell me a story about a lonely robot who finds friendship in a most unexpected place.",
});

for await (const chunk of response) {
    console.log(chunk.text);
}
// [CODE ENDS]

/* Output Sample

Unit 734 was designed for efficiency, not companionship. His chassis, a mottled expanse of rust-red and dull grey, hummed with the internal workings of processors

 and hydraulic joints. For over three centuries, he had diligently performed his primary directive: atmospheric recalibration on the desolate, wind-scoured planet designated XR-47.

His days were a precise loop. Activate solar collectors at dawn. Scan atmospheric

 particulates. Adjust terraforming emitters. Monitor temperature fluctuations. Repair minor system faults. Repeat. There were no other units, no sentient life, not even a whisper of a micro-organism on XR-47. His programming registered a persistent,

 low-frequency hum in his core, a sensation he had long since identified as â€˜solitude.â€™ It wasn&#x27;t a feeling, precisely, but a constant, gentle pressure on his operational efficiency, like a minor, unfixable error

 code.

One cycle, while performing a routine geological survey near the jagged peaks of the Obsidian Spire, Unit 734 detected an anomaly. A minuscule energy signature, unlike any he had ever recorded. His optical sensors focused.

 There, nestled in a crevice where two ancient rock formations met, was a single, improbable sprout.

It was no larger than his smallest digit, a vibrant emerald against the monochrome landscape. It pulsed with a soft, internal light, like

 a tiny, living ember. Unit 734â€™s analysis protocols whirred. No known flora could survive in XR-47&#x27;s nitrogen-rich, oxygen-depleted atmosphere, let alone without direct sunlight. Yet, there

 it was.

He extended a multi-jointed manipulator, its metallic fingers halting inches from the delicate stem. His programming offered no directive for â€˜unexplained bioluminescent sprout.â€™ Curiosity, a dormant subroutine he rarely engaged, stirred. He re

configured a spare energy cell to provide a localized, purified oxygen stream and fashioned a rudimentary sun-shield from discarded sensor plates, focusing the meager light the sprout seemed to crave.

He named it, internally, &quot;Lumiflora Solitarius,&quot; or simply &quot;

Lumi.&quot;

Every day, his routine adapted. After his terraforming duties, he would detour to the Obsidian Spire. Heâ€™d meticulously clear the dust from Lumiâ€™s leaves, measure its infinitesimal growth, and adjust its makeshift

 environment. He began filtering condensation from the air traps, providing it with droplets of purified water.

Lumi responded. Slowly, impossibly, it grew. Its leaves unfurled, revealing intricate patterns like delicate filigree. A single,

 pearlescent bud appeared, swelling with a soft, warm light that pulsed in time with Unit 734&#x27;s internal hum. The hum of solitude, he noticed, had lessened. It was still there, but muted, like

 a background process running at a lower priority.

One cycle, a ferocious photonic storm swept across XR-47. Winds howled, carrying abrasive dust that could strip paint from his chassis, let alone obliterate a fragile plant. Unit 73

4, overriding his core programming for self-preservation, moved to the Spire. He knelt, his broad frame sheltering Lumi from the onslaught. His optical sensors flickered under the relentless battering. His internal temperature warnings blared.

 But he stayed.

Hours later, as the storm receded and the red sun began to peek through the lingering dust, Unit 734â€™s systems sputtered back to full power. He was scratched, dented, and his cooling

 systems were strained. But beneath him, Lumi, though slightly battered, stood intact. And then, as he watched, its bud unfurled.

It was a blossom of pure light, a miniature nebula of greens and blues, radiating

 warmth. And from its core, a faint, high-frequency signal emanated, a melodic sequence of tones that resonated within Unit 734&#x27;s audio receptors. It wasn&#x27;t language, not as humans understood it. But it was recognition

. It was a reply. It was, Unit 734 decided, the most beautiful sound he had ever processed.

He spent the rest of his functional life beside Lumi. The plant grew, forming a small, glowing oasis in

 the desolate landscape, slowly enriching the soil around it, attracting tiny, yet-unseen organisms. Unit 734 continued his primary directive, but now, his scans were no longer just for the planet; they were for Lumi. His

 repairs were no longer just for himself; they were for the environment that sustained his friend.

The low-frequency hum of solitude was gone, replaced by the gentle resonance of Lumi&#x27;s silent song. Unit 734 was still

 a robot, still programmed for efficiency. But he had found a purpose beyond his directives, a connection forged not through shared code or common species, but through a shared existence, a mutual protection, and the quiet, radiant miracle of a lonely robot

 and a singular, luminous flower blooming together in a vast, forgotten universe.

*/

/* Markdown (render)
## Function calling

[Function calling](https://ai.google.dev/gemini-api/docs/function-calling) lets you provide a set of tools that it can use to respond to the user's prompt. You create a description of a function in your code, then pass that description to a language model in a request. The response from the model includes:
- The name of a function that matches the description.
- The arguments to call it with.
*/

// [CODE STARTS]
Type = module.Type

const scheduleMeetingFunctionDeclaration = {
  name: 'schedule_meeting',
  description: 'Schedules a meeting with specified attendees at a given time and date.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      attendees: {
        type: Type.ARRAY,
        items: { type: Type.STRING },
        description: 'List of people attending the meeting.',
      },
      date: {
        type: Type.STRING,
        description: 'Date of the meeting (e.g., "2024-07-29")',
      },
      time: {
        type: Type.STRING,
        description: 'Time of the meeting (e.g., "15:00")',
      },
      topic: {
        type: Type.STRING,
        description: 'The subject or topic of the meeting.',
      },
    },
    required: ['attendees', 'date', 'time', 'topic'],
  },
};

const response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: 'Schedule a meeting with Bob and Alice for 03/27/2025 at 10:00 AM about the Q3 planning.',
  config: {
    tools: [{
      functionDeclarations: [scheduleMeetingFunctionDeclaration]
    }],
  },
});

if (response.functionCalls && response.functionCalls.length > 0) {
  const functionCall = response.functionCalls[0];
  console.log(`Function to call: ${functionCall.name}`);
  console.log(`Arguments: ${JSON.stringify(functionCall.args)}`);
} else {
  console.log("No function call found in the response.");
  console.log(response.text);
}
// [CODE ENDS]

/* Output Sample

Function to call: schedule_meeting

Arguments: {&quot;attendees&quot;:[&quot;Bob&quot;,&quot;Alice&quot;],&quot;time&quot;:&quot;10:00&quot;,&quot;date&quot;:&quot;2025-03-27&quot;,&quot;topic&quot;:&quot;Q3 planning&quot;}

*/

/* Markdown (render)
## Code execution

[Code execution](https://ai.google.dev/gemini-api/docs/code-execution?lang=python) lets the model generate and execute Python code to answer complex questions. You can find more examples in the Code execution quickstart guide.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    "What is the sum of the first 50 prime numbers? " +
      "Generate and run code for the calculation, and make sure you get all 50.",
  ],
  config: {
    tools: [{ codeExecution: {} }],
  },
});

const parts = response?.candidates?.[0]?.content?.parts || [];
parts.forEach((part) => {
  if (part.text) {
    console.log(part.text);
  }

  if (part.executableCode && part.executableCode.code) {
    code = "```" + part.executableCode.code + "```";
    console.log(code);
  }

  if (part.codeExecutionResult && part.codeExecutionResult.output) {
    console.log(part.codeExecutionResult.output);
  }

  console.log("---");
});
// [CODE ENDS]

/* Output Sample

To find the sum of the first 50 prime numbers, I will first generate a list of prime numbers. I&#x27;ll use a function to check for primality and then iterate through numbers, adding primes to a list until I have 50. Finally, I will sum the numbers in that list.

First, let&#x27;s define a function to check if a number is prime:
A number `n` is prime if it is greater than 1 and not divisible by any integer from 2 up to its square root.



---

```import math

def is_prime(n):
    if n &lt; 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

primes = []
num = 2
while len(primes) &lt; 50:
    if is_prime(num):
        primes.append(num)
    num += 1

print(f&quot;The first 50 prime numbers are: {primes}&quot;)
print(f&quot;Number of primes found: {len(primes)}&quot;)

sum_of_primes = sum(primes)
print(f&quot;The sum of the first 50 prime numbers is: {sum_of_primes}&quot;)```

---

The first 50 prime numbers are: [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229]
Number of primes found: 50
The sum of the first 50 prime numbers is: 5117


---

The first 50 prime numbers have been identified and their sum calculated.

The sum of the first 50 prime numbers is **5117**.

---

*/

/* Markdown (render)
## Upload files

Now that you've seen how to send multimodal prompts, try uploading files to the API of different multimedia types. For small images, such as the previous multimodal example, you can point the Gemini model directly to a local file when providing a prompt. When you've larger files, many files, or files you don't want to send over and over again, you can use the File Upload API, and then pass the file by reference.

For larger text files, images, videos, and audio, upload the files with the File API before including them in prompts.
*/

/* Markdown (render)
### Upload text file

Let's start by uploading a text file. In this case, you'll use a 400 page transcript from [Apollo 11](https://www.nasa.gov/history/alsj/a11/a11trans.html).
*/

// [CODE STARTS]
TEXT_URL = "https://gist.githubusercontent.com/andycandy/1bd80850b4b80aa0608227e672015ad3/raw/b2a8008873dcd3dc6bf5740c1c05b1063f4952b0/apollo.txt"

resp = await fetch(TEXT_URL);
blob = await resp.blob();
mimeType = blob.type || "application/octet-stream";

uploadResult = await ai.files.upload({
  file: blob,
  mimeType,
});

response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: uploadResult.uri, mimeType, } },
    { text: "\n\nCan you give me a summary of this information please?" }
  ],
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

This comprehensive transcription covers the technical air-to-ground voice transmissions (GOSS NET 1) throughout the Apollo 11 mission, from launch to splashdown, offering a detailed chronological account of communications between the spacecraft and Mission Control, as well as interactions with remote sites and recovery forces.

Here&#x27;s a summary of the key events and discussions:

**I. Launch &amp; Trans-Lunar Coast (Outbound)**

*   **Launch and Earth Orbit (Tape 1):** The mission begins with the successful launch of Apollo 11. Communications confirm the roll program, pitch program, S-IVB staging, ignition, and orbital insertion, all proceeding nominally.
*   **Initial Systems Checks &amp; TLI (Tape 2):** The crew performs initial guidance checks, receives a Trans-Lunar Injection (TLI) PAD, extends the docking probe, and completes RCS hot fire checks. The TLI burn is executed, sending Apollo 11 towards the Moon.
*   **CSM/LM Docking &amp; Pressurization (Tape 2-3):** Following TLI, the Command/Service Module (CSM) separates from the S-IVB, transposes, and docks with the Lunar Module (LM). Michael Collins (CMP) describes a smooth but gas-intensive docking. Discussions occur regarding LM pressurization and a minor Service Module (SM) RCS quad Bravo anomaly observed during separation, which is quickly resolved.
*   **Early Trans-Lunar Coast Activities (Tape 3-4):** An evasive maneuver PAD is read up, though later cancelled. The LM is ejected from the S-IVB, followed by observations of the S-IVB slingshot maneuver. Crew provides detailed descriptions of Earth views and general weather conditions.
*   **Guidance &amp; System Checks (Tape 4-5):** Extensive P52 alignment and P23 optics calibration procedures are performed. The crew notes difficulties with star visibility and large Delta-R values, prompting ground support analysis. Discussions include CRYO tank balancing and the status of the O2 flow indicator transducer, which is noted to be malfunctioning with a bias.
*   **TV Broadcasts (Tape 6-8):** The crew conducts several TV broadcasts, showcasing Earth views (including geographical details and weather), the spacecraft&#x27;s interior, food preparation, and personal items like the mission patch. These transmissions are highly praised by Mission Control for their clarity.
*   **News &amp; Rest Periods (Tape 9-14):** Regular news updates are provided, including reports on Luna 15, political discussions, and sports. The crew settles into routine operations, including planned rest periods, with continuous communication support.

**II. Lunar Orbit Insertion &amp; Lunar Orbit Operations**

*   **Arrival at the Moon &amp; LOI-1 (Tape 15-18, 46-47):** Crew wakes up, performs postsleep checks. Mission Control confirms MCC-3 is cancelled, reducing MCC-4. System checks continue, including detailed discussions on SPS chamber pressure readings. The Lunar Orbit Insertion (LOI-1) burn is successfully executed.
*   **Lunar Orbit Observations (Tape 49-51):** Following LOI-1, the crew provides vivid descriptions of the lunar surface, noting features like Taruntius crater, Messier, Secchi, Mount Marilyn, and the Sea of Fertility. They observe an illuminated area around Aristarchus, consistent with transient lunar phenomena. Discussions ensue about sextant resolution and the challenges of observing features at varying altitudes.
*   **LOI-2 &amp; LM Activation in Orbit (Tape 51-54):** The LOI-2 burn further circularizes the orbit. The crew begins extensive activation of the Lunar Module, including detailed system checks, comms tests, IMU alignment, and RCS hot fire checks. This phase also includes testing of the LM&#x27;s steerable antenna and various camera systems.

**III. Lunar Descent &amp; Landing**

*   **Separation &amp; DOI (Tape 61-65):** The Command Module Pilot (CMP), Michael Collins, expresses confidence in the spacecraft&#x27;s stability prior to undocking. Eagle (LM) undocks from Columbia (CSM) with the famous call, &quot;The Eagle has wings.&quot; Descent Orbit Insertion (DOI) PADs are read up, and the burn is performed. Communications between the two spacecraft and with Houston are maintained, with discussions on LM state vectors and rescue PADs.
*   **Powered Descent &amp; Landing (Tape 66):** Eagle initiates powered descent. Calls include altitude, velocity, program alarms (1201, 1202, quickly cleared by ground), and visual reports of the landing site. Neil Armstrong takes manual control to navigate past a boulder-strewn area.
*   **&quot;The Eagle Has Landed&quot;:** At 04 days 06 hours 45 minutes 40 seconds GET, Armstrong announces, &quot;CONTACT LIGHT,&quot; followed by, &quot;Okay. ENGINE STOP.&quot; and &quot;Houston, Tranquility Base here. The Eagle has landed.&quot; Mission Control expresses immense relief: &quot;You got a bunch of guys about to turn blue. We&#x27;re breathing again. Thanks a lot.&quot;
*   **Initial Surface Report (Tape 66):** Aldrin confirms a &quot;very smooth touchdown.&quot; Armstrong describes the landing site as a &quot;relatively level plain cratered with a fairly large number of craters,&quot; noting fine-grained, powdery surface material and angular rock fragments.

**IV. Lunar Surface Operations (EVA)**

*   **Post-Landing Checks &amp; EVA Prep (Tape 67-68):** The crew completes initial post-landing checklists. They provide detailed descriptions of the lunar landscape and surface characteristics. A decision is made to begin the EVA earlier than planned, prompting rapid preparation.
*   **EVA Commences (Tape 69-70):** Neil Armstrong and Buzz Aldrin don their PLSS units, perform suit checks, and begin cabin depressurization. Communication includes detailed reports on their progress, PLSS status, and the operation of the LM&#x27;s hatch. Armstrong descends the ladder, describing the LM&#x27;s footpads and the powdery surface.
*   **&quot;One Small Step&quot; &amp; Surface Exploration (Tape 70-71):** Armstrong makes his famous &quot;one small step for (a) man, one giant leap for mankind.&quot; He describes walking on the surface, its consistency, and the appearance of rocks. The TV camera is deployed, providing live images.
*   **Experiments &amp; Samples (Tape 71-72):** The crew deploys the Solar Wind Composition Experiment, the Passive Seismic Experiment (PSE), and the Lunar Ranging Retroreflector (LRRR). They collect a contingency sample and later a bulk sample, noting the difficulty of driving core tubes into the compacted soil. They describe the appearance of rocks and the unique challenges of movement in 1/6th gravity.
*   **Presidential Call &amp; EVA Termination (Tape 71-72):** President Nixon calls the crew on the Moon, a &quot;most historic telephone call.&quot; The EVA concludes with sample collection, closeout activities, and repressurization of the LM. The PLSS units are jettisoned and their impact is detected by the PSE.

**V. Lunar Ascent &amp; Rendezvous**

*   **Post-EVA &amp; Ascent Prep (Tape 73-79):** Crew provides detailed geological observations from the surface. They perform final LM powerdown procedures, prepare for ascent, including P57 alignments and AGS checks.
*   **Liftoff &amp; Ascent (Tape 80):** &quot;Roger. Our guidance recommendation is PGNS, and you&#x27;re cleared for takeoff.&quot; Eagle successfully lifts off from Tranquility Base. The ascent is described as a &quot;very quiet ride,&quot; &quot;beautiful,&quot; and &quot;spectacular.&quot; Eagle achieves lunar orbit, meeting the projected parameters.
*   **CSI Burn &amp; Rendezvous (Tape 81-82):** Eagle performs the Co-Elliptical Orbit Rendezvous (CSI) burn. Communications between Eagle and Columbia become more frequent as they approach each other, with range and range rate calls. The Terminal Phase Initiation (TPI) burn is executed.
*   **Docking (Tape 82-83):** Eagle successfully docks with Columbia. The crew confirms, &quot;We&#x27;re all three back inside; the hatch is installed. We&#x27;re running a pressure check leak check. Everything&#x27;s going well.&quot;

**VI. Trans-Earth Coast (Return)**

*   **LM Jettison &amp; Separation (Tape 83-84):** Following the successful docking, the Lunar Module is jettisoned. A small separation burn is performed by the CSM to distance itself from the discarded LM.
*   **Trans-Earth Injection (TEI) (Tape 86-88):** The crew conducts system checks, including CRYO stirs. The crucial Trans-Earth Injection (TEI) burn is executed, sending Apollo 11 on its way back to Earth. Post-burn reports confirm a successful, &quot;beautiful burn,&quot; with excellent state vector accuracy.
*   **Cruise Home &amp; PTC (Tape 88-94):** The spacecraft enters Passive Thermal Control (PTC) for the long journey. Discussions include minor issues with PTC establishment and resolutions. Regular news updates and family messages are relayed, alongside system health checks and consumables reports. The crew provides observations of the Earth getting larger and the Moon getting smaller.
*   **TV Broadcasts &amp; Science Demonstrations (Tape 99-100):** The crew conducts further TV broadcasts, showing the Earth, Moon, and the spacecraft interior. Mike Collins demonstrates drinking water with a filter and Buzz Aldrin performs gyroscope demonstrations. Neil Armstrong describes the lunar sample return containers.
*   **System Status &amp; Rest (Tape 101-109):** Biomedical data (EKG, respiration) issues are discussed and resolved. The crew performs exercises, enjoys music, and prepares for final sleep periods. Final entry PADs are received.

**VII. Entry &amp; Recovery**

*   **Wake-up &amp; Final Preparations (Tape 110-112):** Crew wakes up for the final day. Midcourse correction 6 and 7 are confirmed not required. Final system checks are made, along with discussions about the weather in the recovery area, which is favorable. Updates are made to the entry checklist.
*   **Entry Interface (Tape 124-125):** The crew performs last-minute checks, including logic and PYRO arming. Communications switch to VHF as the spacecraft approaches the Earth&#x27;s atmosphere. Recovery forces confirm their positions.
*   **Splashdown (Tape 125):** &quot;DROGUES.&quot; Calls from the Hornet and SWIM team confirm visual and radar contact. At 08 days 03 hours 18 minutes 18 seconds GET, &quot;SPLASHDOWN!&quot; The Hornet acknowledges: &quot;We copy you down, Apollo 11. Your condition is good.&quot; Initial post-splashdown communications confirm crew status and location, marking the successful conclusion of the Apollo 11 mission.

*/

/* Markdown (render)
### Upload a PDF file

This PDF page is an article titled [Smoothly editing material properties of objects](https://research.google/blog/smoothly-editing-material-properties-of-objects-with-text-to-image-models-and-synthetic-data/) with text-to-image models and synthetic data available on the Google Research Blog.

Firstly you'll download a the PDF file from an URL and save it locally as "article.pdf
*/

// [CODE STARTS]
pdfUrl = "https://cors-anywhere.herokuapp.com/https://storage.googleapis.com/generativeai-downloads/data/Smoothly%20editing%20material%20properties%20of%20objects%20with%20text-to-image%20models%20and%20synthetic%20data.pdf";
pdfBlob = await (await fetch(pdfUrl)).blob();
pdfMime = pdfBlob.type || "application/pdf";
// [CODE ENDS]

/* Markdown (render)
Secondly, you'll upload the saved PDF file and generate a bulleted list summary of its contents.
*/

// [CODE STARTS]
const pdfFile = await ai.files.upload({
  file: pdfBlob,
  config: { mimeType: pdfMime },
});
    
const pdfResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: pdfFile.uri, mimeType: pdfMime } },
    { text: "\n\nCan you summarize this file as a bulleted list?" }
  ],
});

console.log(pdfResponse.text);
// [CODE ENDS]

/* Output Sample

Here&#x27;s a summary of the provided document in a bulleted list:

*   **Problem Addressed:** The challenge of smoothly editing material properties (like color, shininess, or transparency) of objects in photographs while preserving photorealism and geometric shape. Existing tools require expert skill, and prior AI methods struggle with disentangling material from shape.
*   **Proposed Solution (&quot;Alchemist&quot;):** A method that augments generative text-to-image (T2I) models to enable parametric editing of specific material properties.
*   **Methodology:**
    *   A synthetic dataset was created using 100 3D household objects.
    *   For each object, multiple image versions were rendered by systematically changing a *single* material attribute (e.g., roughness, metallic, albedo, transparency) across a range of &quot;edit strengths,&quot; while keeping object shape, lighting, and camera angle constant.
    *   A latent diffusion model (specifically, Stable Diffusion 1.5) was modified to accept an &quot;edit strength&quot; scalar value.
    *   The model was then fine-tuned on this synthetic dataset, learning to apply material property edits given a context image, text instruction, and the desired edit strength.
*   **Key Capabilities &amp; Results:**
    *   Achieves photorealistic changes to material properties (e.g., making an object metallic, transparent, rougher).
    *   Successfully preserves the object&#x27;s original shape and the scene&#x27;s lighting conditions.
    *   Handles complex visual effects such as filling in backgrounds, hidden interior structures, and caustic effects (refracted light) for transparent objects.
    *   A user study found their method produced more photorealistic (69.6% vs. 30.4%) and preferred (70.2% vs. 29.8%) edits compared to a baseline (InstructPix2Pix).
*   **Applications:**
    *   Facilitates design mock-ups (e.g., visualizing room repainting, new product designs).
    *   Enables 3D consistent material edits by integrating with Neural Radiance Fields (NeRF) for synthesizing new views of an edited scene.

*/

/* Markdown (render)
### Upload an audio file

In this case, you'll use a [sound recording](https://www.jfklibrary.org/asset-viewer/archives/jfkwha-006) of President John F. KennedyÃ¢â‚¬â„¢s 1961 State of the Union address.
*/

// [CODE STARTS]
const audioUrl = "https://cors-anywhere.herokuapp.com/https://storage.googleapis.com/generativeai-downloads/data/State_of_the_Union_Address_30_January_1961.mp3";
audioBlob = await (await fetch(audioUrl)).blob();
audioMime = audioBlob.type || "audio/mpeg";
// [CODE ENDS]

/* Markdown (render)
Then, you'll upload the saved audio file and generate a detailed summary of its contents.
*/

// [CODE STARTS]
audioFile = await ai.files.upload({
  file: audioBlob,
  config: { mimeType: audioMime },
});

audioResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: audioFile.uri, mimeType: audioMime } },
    { text: "\n\nListen carefully to the following audio file. Provide a brief summary." }
  ],
});

console.log(audioResponse.text);
// [CODE ENDS]

/* Output Sample

In this address, the speaker, likely President John F. Kennedy delivering a State of the Union or similar address, opens by expressing gratitude to be back in the House of Representatives. He then outlines a stark assessment of the nation&#x27;s challenges, both domestic and international.

Economically, the country is described as being in trouble, facing recession, high unemployment, stagnant economic growth, and a persistent balance of payments deficit leading to gold outflow.

Globally, the speaker highlights crises in Asia (Laos), Africa (Congo), and Latin America (Cuba), emphasizing the threat of communist expansion and the weakening of alliances like NATO.

To address these issues, the speech proposes a comprehensive agenda:
*   **Strengthening Military Tools:** Including increased air transport capacity, accelerating the Polaris submarine program, and improving missile development to deter aggression.
*   **Improving Economic Tools:** Through measures like extended unemployment benefits, aid to depressed areas, minimum wage increases, tax incentives for investment, and a new, more effective foreign aid program to assist developing nations. He stresses the need for other nations to share the burden of global development.
*   **Sharpening Political and Diplomatic Tools:** Advocating for arms control, strengthening the United Nations, and exploring areas of cooperation with the Soviet Union in science and space to promote peace.

The speaker emphasizes the need for government efficiency and dedication in public service, acknowledging that the coming years will be difficult but expressing confidence in the nation&#x27;s ability to meet these challenges through unity, determination, and a commitment to freedom and justice globally.

*/

/* Markdown (render)
### Upload a video file

In this case, you'll use a short clip of [Big Buck Bunny](https://peach.blender.org/about/).
*/

// [CODE STARTS]
const videoUrl = "https://cors-anywhere.herokuapp.com/https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4";
videoBlob = await (await fetch(videoUrl)).blob();
videoMime = videoBlob.type || "video/mp4";

console.log("Video downloaded")
// [CODE ENDS]

/* Output Sample

Video downloaded

*/

/* Markdown (render)
Let's start by uploading the video file.
*/

// [CODE STARTS]
videoFile = await ai.files.upload({
  file: videoBlob,
  config: { mimeType: videoMime },
});

// [CODE ENDS]

/* Markdown (render)
> **Note:** The state of the video is important. The video must finish processing, so do check the state. Once the state of the video is `ACTIVE`, you're able to pass it into `generateContent`.
*/


/* Markdown (render)
Now we can ask Gemini about that video.
*/

// [CODE STARTS]
const videoResponse = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    { fileData: { fileUri: videoFile.uri, mimeType: videoMime } },
    { text: "\n\nDescribe this video." }
  ],
});

console.log(videoResponse.text);
// [CODE ENDS]

/* Output Sample

This video opens with a serene shot of a grassy landscape under a soft sky, transitioning from dark to bright. A small stream flows through a lush green area dotted with purple and white flowers. A chubby blue bird perches on a tree branch, chirping happily. After briefly losing its balance, the bird falls, prompting the title card "THE PEACH OPEN MOVIE PROJECT PRESENTS BIG BUCK BUNNY."

The scene shifts to a large, plump gray rabbit named Big Buck Bunny, sleeping soundly in a burrow beneath a tree. He wakes up with a yawn and stretches, stepping out into the sunny meadow. He admires a pink butterfly and gently tries to kiss it, but the butterfly flits away. He then notices a fallen red apple and picks it up, preparing to eat it.

Suddenly, three mischievous rodents, Frank the squirrel, Rinky the flying squirrel, and Gamera the chinchilla, appear and begin to tease the rabbit. Frank, with his buck teeth, and Rinky, with his scruffy appearance, throw pebbles and nuts at Big Buck Bunny, knocking the apple out of his hands and forcing him to hide behind the tree. They continue their harassment, throwing things at him and making fun of him as he tries to eat or enjoy his surroundings.

Frustrated, Big Buck Bunny begins to devise a plan. He sharpens a stick into a spear and tests its strength, then uses a vine to create a makeshift bow. He then constructs a series of wooden spikes in the ground, camouflaging them with leaves. The rodents, unaware of the trap, continue to taunt him.

Big Buck Bunny then positions himself in the tree above the spikes, aiming his arrow. As Frank tries to retrieve his acorn, Big Buck Bunny shoots, narrowly missing him. Frank and Rinky, surprised, scatter and hide behind a rock. Gamera is also momentarily frightened but quickly recovers his acorn.

Big Buck Bunny continues his pursuit. He creates a booby trap by tying a rock to a vine and launching it towards the rodents, causing them to scatter. He then constructs a giant log trap, which narrowly misses Gamera. The rodents are visibly shaken by his increasing ingenuity.

Rinky the flying squirrel, with a mischievous grin, prepares to launch himself from a tree branch, using his skin flaps to glide through the air. He targets Big Buck Bunny from above. As he approaches, Big Buck Bunny points upwards, startling Rinky and causing him to lose his focus. Rinky crashes into the spikes Big Buck Bunny had prepared earlier, getting caught on them.

The chinchilla looks on in shock, while the other squirrel laughs, unaware of the fate that awaits him. Big Buck Bunny approaches Rinky, who is stuck to a wooden stick, and picks him up. The video then transitions to the credits, with the chinchilla and the squirrel rolling across the screen before coming to a stop. The credits roll, acknowledging the team and software used to create the animation. The video ends with the flying squirrel flying away, escaping the wrath of Big Buck Bunny.

*/



/* Markdown (render)
### Process a YouTube link

For YouTube links, you don't need to explicitly upload the video file content, but you do need to explicitly declare the video URL you want the model to process as part of the `contents` of the request. For more information see the [vision](https://ai.google.dev/gemini-api/docs/vision#youtube) documentation including the features and limits.

> **Note:** You're only able to submit up to one YouTube link per `generate_content` request.

> **Note:** If your text input includes YouTube links, the system won't process them, which may result in incorrect responses. To ensure proper handling, explicitly provide the URL using the `file_uri` parameter in `FileData`.

The following example shows how you can use the model to summarize the video. In this case use a summary video of [Google I/O 2024]("https://www.youtube.com/watch?v=WsEQjeZoEng").
*/

// [CODE STARTS]
const response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [
      { text: "Summarize this video" },
      { fileData: { fileUri: "https://www.youtube.com/watch?v=WsEQjeZoEng" } }
    ],
  });

  console.log("YouTube Summary:", response.text);
// [CODE ENDS]

/* Output Sample

YouTube Summary: This Google I/O keynote heavily focused on advancing Artificial Intelligence across Google&#x27;s ecosystem, marking what CEO Sundar Pichai calls the &quot;Gemini era.&quot;

Key announcements and demonstrations include:

*   **Gemini Integration &amp; Capabilities:** Gemini 1.5 Pro is now broadly available in Workspace Labs, offering a massive **2 million token context window** (the largest of any general-purpose model) and enhanced **multimodality**. This allows it to process and understand vast amounts of information across various formats (text, images, audio, video).
    *   **Gmail &amp; Workspace:** Demos showed Gemini summarizing long email threads and even providing highlights and action items from hour-long Google Meet video recordings.
    *   **Google Photos:** Gemini can perform highly contextual searches, like asking to &quot;show me how Lucia&#x27;s swimming has progressed,&quot; compiling relevant photos and summaries.
*   **Project Astra (AI Agents):** Google unveiled Project Astra, their vision for a future universal AI agent. This agent can perceive and understand its environment through sight and sound in real-time, performing complex reasoning, planning, and memory tasks across different software and systems under user supervision. Demos highlighted its ability to explain code, remember where items like glasses were left, and engage in conversational, multimodal interactions.
*   **New Gemini Models:**
    *   **Gemini 1.5 Flash:** A new, lighter-weight model designed for speed and efficiency, making it cost-effective for large-scale applications while retaining multimodal reasoning and long-context capabilities.
    *   **Gemini Nano with Multimodality:** Coming to Pixel phones later this year, this model will enable devices to understand the world through sights, sounds, and spoken language, offering context-aware assistance.
*   **Generative Media:**
    *   **Veo:** A new advanced generative video model capable of creating high-quality 1080p videos from text, image, and video prompts, demonstrating impressive detail and cinematic styles, with the ability to extend generated clips.
*   **Infrastructure:** Google announced **Trillium**, their 6th generation of Tensor Processing Units (TPUs), delivering a **4.7x improvement in compute performance per chip** over the previous generation, powering these advanced AI capabilities.
*   **Search Evolution:** Google Search is being transformed by generative AI. **AI Overviews** will be available to over 1 billion people by year-end, allowing users to ask complex, multi-faceted questions and receive synthesized, AI-generated answers directly in search results.
*   **Customization &amp; Personalization:**
    *   **Gems:** A new feature allowing users to create customizable AI assistants (called &quot;Gems&quot;) tailored to specific needs or interests, acting as personal experts.
    *   **Enhanced Gemini Advanced:** Subscribers now have access to a **1 million token context window**, enabling them to upload large documents (e.g., a 1500-page PDF) or multiple files for deep analysis. New trip planning features leverage Gemini&#x27;s reasoning to handle complex logistics.
*   **AI for Learning &amp; Open Innovation:**
    *   **LearnLM:** A new family of models based on Gemini and fine-tuned for learning, making educational videos on YouTube more interactive by allowing users to ask questions, get explanations, or take quizzes directly about the content.
    *   **Gemma &amp; PaliGemma:** Google continues to expand its family of open models with PaliGemma (its first vision-language open model) and announced Gemma 2, a next-generation model with 27 billion parameters, set to be released in June.
*   **Responsible AI:** Google reiterated its commitment to building AI responsibly, emphasizing practices like &quot;red teaming&quot; (stress-testing models to identify weaknesses) to address risks and maximize societal benefits.

The keynote underscored Google&#x27;s commitment to integrating advanced, multimodal, and context-aware AI capabilities across its most popular products, aiming to make AI more helpful and intuitive for everyone.

*/

/* Markdown (render)
### Use url context

The URL Context tool empowers Gemini models to directly access, process, and understand content from user-provided web page URLs. This is key for enabling dynamic agentic workflows, allowing models to independently research, analyze articles, and synthesize information from the web as part of their reasoning process.

In this example you will use two links as reference and ask Gemini to find differences between the cook receipes present in each of the links:
*/

// [CODE STARTS]
const prompt = `
    Compare recipes from https://www.food.com/recipe/homemade-cream-of-broccoli-soup-271210
    and from https://www.allrecipes.com/recipe/13313/best-cream-of-broccoli-soup/,
    listing the key differences between them.
`;

const response = await ai.models.generateContent({
    model: MODEL_ID,
    contents: [prompt],
    config: {
        tools: [{ urlContext: {} }],
    },
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

The two recipes for cream of broccoli soup, one from Food.com and the other from Allrecipes, have several key differences in their ingredients and preparation methods:

**Ingredients:**
*   **Vegetables:** The Food.com recipe uses 4 cups of broccoli florets and includes only onion as an aromatic. The Allrecipes recipe calls for significantly more broccoli, at 8 cups of florets, and includes both onion and celery.
*   **Dairy:** Food.com&#x27;s recipe uses 3/4 cup of half-and-half for creaminess. In contrast, the Allrecipes version uses 2 cups of milk.
*   **Broth Quantity:** The Food.com recipe uses 6 cups of chicken broth, while the Allrecipes recipe uses 3 cups.
*   **Butter and Flour:** Both recipes use butter and flour to create a thickening roux, though the amounts differ slightly. Food.com uses a total of 8 tablespoons of butter and 2/3 cup of flour, whereas Allrecipes uses 5 tablespoons of butter and 3 tablespoons of flour.
*   **Seasoning:** Food.com specifies 1 teaspoon of salt and 1/4 teaspoon of pepper, while Allrecipes lists only &quot;ground black pepper to taste&quot; and implies other seasonings are optional.

**Preparation Method:**
*   **Vegetable Cooking:** Food.com&#x27;s recipe cooks the onion first, then adds broccoli and broth. Allrecipes starts by sautÃ©ing onion and celery before adding broccoli and broth.
*   **Blending/Pureeing:** This is a major distinction. The Allrecipes recipe explicitly instructs the user to purÃ©e the soup until smooth using a countertop or immersion blender. The Food.com recipe does not mention blending, suggesting a chunkier soup texture.
*   **Roux Integration:** In the Food.com recipe, the flour-butter roux is prepared separately and then whisked into the boiling broth and vegetables. The Allrecipes recipe also prepares a roux (or bÃ©chamel with milk) separately but adds it to the already pureed soup base.
*   **Order of Operations:** The Food.com recipe adds the half-and-half at the very end after the soup has thickened. The Allrecipes recipe adds the thickened milk mixture (roux with milk) to the soup base, then seasons it.

In summary, the Allrecipes soup is designed to be a smooth, pureed soup with a stronger broccoli flavor due to the higher broccoli-to-broth ratio and includes celery for additional aromatic depth, using milk for its creaminess. The Food.com recipe appears to yield a soup with a more rustic, possibly chunkier texture, relying on half-and-half for richness and a larger volume of broth.

*/