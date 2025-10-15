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
# Gemini API: Prompting Quickstart

This notebook contains examples of how to write and run your first prompts with the Gemini API.

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
## Run your first prompt

Use the `generateContent` method to generate responses to your prompts. You can pass text directly to generateContent, and use the `.text` property to get the text content of the response.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "Give me python code to sort a list"
});

console.log(response.text); 
// [CODE ENDS]

/* Output Sample

Python provides very straightforward and efficient ways to sort lists, using built-in functions and methods. Here are the most common ways:

---

### 1. `list.sort()` (In-place sorting)

This method sorts the list **in place**, meaning it modifies the original list directly and returns `None`.

```python
# Original list
my_list = [3, 1, 4, 1, 5, 9, 2, 6]

print(&quot;Original list:&quot;, my_list)

# Sort the list in ascending order (default)
my_list.sort()

print(&quot;Sorted list (ascending):&quot;, my_list) # Output: [1, 1, 2, 3, 4, 5, 6, 9]

# Sort the list in descending order
my_list.sort(reverse=True)

print(&quot;Sorted list (descending):&quot;, my_list) # Output: [9, 6, 5, 4, 3, 2, 1, 1]

# What happens if you try to assign the result of .sort()?
# It will assign None, because .sort() modifies in place.
another_list = [5, 2, 8]
result = another_list.sort()
print(&quot;Another list:&quot;, another_list) # Output: [2, 5, 8]
print(&quot;Result of sort():&quot;, result)   # Output: None (important to remember!)
```

---

### 2. `sorted()` (Returns a new sorted list)

This built-in function returns a **new sorted list**, leaving the original list unchanged. It can be used on any iterable (lists, tuples, strings, etc.).

```python
# Original list
my_list = [3, 1, 4, 1, 5, 9, 2, 6]

print(&quot;Original list:&quot;, my_list)

# Get a new sorted list in ascending order (default)
sorted_ascending = sorted(my_list)

print(&quot;Original list (unchanged):&quot;, my_list) # Output: [3, 1, 4, 1, 5, 9, 2, 6]
print(&quot;New sorted list (ascending):&quot;, sorted_ascending) # Output: [1, 1, 2, 3, 4, 5, 6, 9]

# Get a new sorted list in descending order
sorted_descending = sorted(my_list, reverse=True)

print(&quot;New sorted list (descending):&quot;, sorted_descending) # Output: [9, 6, 5, 4, 3, 2, 1, 1]

# Example with another iterable (tuple)
my_tuple = (5, 2, 8, 1)
sorted_from_tuple = sorted(my_tuple)
print(&quot;Sorted from tuple:&quot;, sorted_from_tuple) # Output: [1, 2, 5, 8]
print(&quot;Original tuple:&quot;, my_tuple)             # Output: (5, 2, 8, 1) (unchanged)
```

---

### 3. Custom Sorting with `key`

Both `list.sort()` and `sorted()` accept a `key` argument. The `key` argument takes a function that is called on each element of the list, and the elements are sorted based on the return value of this function. This is incredibly powerful for complex sorting scenarios.

#### Example 1: Sorting strings by length

```python
words = [&quot;apple&quot;, &quot;banana&quot;, &quot;cat&quot;, &quot;elephant&quot;, &quot;dog&quot;]

# Sort by the length of the string
sorted_by_length = sorted(words, key=len)
print(&quot;Sorted by length:&quot;, sorted_by_length)
# Output: [&#x27;cat&#x27;, &#x27;dog&#x27;, &#x27;apple&#x27;, &#x27;banana&#x27;, &#x27;elephant&#x27;]

# Sort by length in reverse order
sorted_by_length_desc = sorted(words, key=len, reverse=True)
print(&quot;Sorted by length (descending):&quot;, sorted_by_length_desc)
# Output: [&#x27;elephant&#x27;, &#x27;banana&#x27;, &#x27;apple&#x27;, &#x27;cat&#x27;, &#x27;dog&#x27;]
```

#### Example 2: Sorting a list of dictionaries by a specific value

You can use a `lambda` function for quick, anonymous functions as a key.

```python
students = [
    {&#x27;name&#x27;: &#x27;Alice&#x27;, &#x27;grade&#x27;: 85, &#x27;age&#x27;: 17},
    {&#x27;name&#x27;: &#x27;Bob&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 16},
    {&#x27;name&#x27;: &#x27;Charlie&#x27;, &#x27;grade&#x27;: 78, &#x27;age&#x27;: 17},
    {&#x27;name&#x27;: &#x27;David&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 18}
]

# Sort by &#x27;grade&#x27; in ascending order
sorted_by_grade = sorted(students, key=lambda student: student[&#x27;grade&#x27;])
print(&quot;Sorted by grade:&quot;)
for s in sorted_by_grade:
    print(s)
# Output:
# {&#x27;name&#x27;: &#x27;Charlie&#x27;, &#x27;grade&#x27;: 78, &#x27;age&#x27;: 17}
# {&#x27;name&#x27;: &#x27;Alice&#x27;, &#x27;grade&#x27;: 85, &#x27;age&#x27;: 17}
# {&#x27;name&#x27;: &#x27;Bob&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 16}
# {&#x27;name&#x27;: &#x27;David&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 18}

# Sort by &#x27;grade&#x27; in descending order
sorted_by_grade_desc = sorted(students, key=lambda student: student[&#x27;grade&#x27;], reverse=True)
print(&quot;\nSorted by grade (descending):&quot;)
for s in sorted_by_grade_desc:
    print(s)

# Sort by multiple criteria (grade then age) - Python&#x27;s sort is stable!
# First sort by age, then sort by grade (descending)
# Or more efficiently: sort by a tuple of keys
sorted_by_grade_then_age = sorted(students, key=lambda student: (student[&#x27;grade&#x27;], student[&#x27;age&#x27;]))
print(&quot;\nSorted by grade, then age:&quot;)
for s in sorted_by_grade_then_age:
    print(s)
# Output (Bob comes before David because his age is lower, even though grade is same):
# {&#x27;name&#x27;: &#x27;Charlie&#x27;, &#x27;grade&#x27;: 78, &#x27;age&#x27;: 17}
# {&#x27;name&#x27;: &#x27;Alice&#x27;, &#x27;grade&#x27;: 85, &#x27;age&#x27;: 17}
# {&#x27;name&#x27;: &#x27;Bob&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 16}
# {&#x27;name&#x27;: &#x27;David&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 18}

# To sort by grade descending, then age ascending:
sorted_custom = sorted(students, key=lambda student: (-student[&#x27;grade&#x27;], student[&#x27;age&#x27;]))
print(&quot;\nSorted by grade (descending), then age (ascending):&quot;)
for s in sorted_custom:
    print(s)
# Output:
# {&#x27;name&#x27;: &#x27;Bob&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 16}
# {&#x27;name&#x27;: &#x27;David&#x27;, &#x27;grade&#x27;: 92, &#x27;age&#x27;: 18}
# {&#x27;name&#x27;: &#x27;Alice&#x27;, &#x27;grade&#x27;: 85, &#x27;age&#x27;: 17}
# {&#x27;name&#x27;: &#x27;Charlie&#x27;, &#x27;grade&#x27;: 78, &#x27;age&#x27;: 17}
```

---

### Summary:

*   **`list.sort()`**:
    *   Modifies the list **in-place**.
    *   Returns `None`.
    *   Only works on `list` objects.
    *   Generally more memory-efficient if you don&#x27;t need the original list.
*   **`sorted()`**:
    *   Returns a **new sorted list**.
    *   Leaves the original iterable unchanged.
    *   Works on any iterable (lists, tuples, sets, strings, etc.).
    *   More flexible if you need to preserve the original data.
*   **`key` argument**: Both accept a `key` function for custom sorting logic.
*   **`reverse=True`**: Both accept `reverse=True` to sort in descending order.

Choose the method that best fits your needs based on whether you want to modify the original list or get a new one.

*/

/* Markdown (render)
## Use images in your prompt

Here you will download an image from a URL and pass that image in our prompt.

First, you download the image and load it with PIL:
*/

// [CODE STARTS]
url = "https://storage.googleapis.com/generativeai-downloads/images/jetpack.jpg";

imageBlob = await fetch(url).then(res => res.blob());

imageDataUrl = await new Promise((resolve) => {
  reader = new FileReader();
  reader.onloadend = () => resolve(reader.result.split(',')[1]);
  reader.readAsDataURL(imageBlob);
});

console.image(imageDataUrl);

// [CODE ENDS]

/* Output Sample
<img src="https://storage.googleapis.com/generativeai-downloads/images/jetpack.jpg"/>
*/

// [CODE STARTS]
prompt = `
  This image contains a sketch of a potential product along with some notes.
  Given the product sketch, describe the product as thoroughly as possible based on what you
  see in the image, making sure to note all of the product features. Return output in JSON format:
  {description: description, features: [feature1, feature2, feature3, etc]}
`;

// [CODE ENDS]

/* Markdown (render)
Then you can include the image in our prompt by just passing a list of items to `generateContent`.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: [
    {
      inlineData: {
        data: imageDataUrl,
        mimeType: "image/jpeg"
      }
    },
    prompt
  ]
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

```json
{
  &quot;description&quot;: &quot;The product is a &#x27;Jetpack Backpack,&#x27; a concept design for a backpack that doubles as a personal flying device. It is designed to look like a normal backpack, implying a discreet appearance, but features retractable boosters at the bottom for propulsion. The sketch shows a main compartment and shoulder straps, with text annotations detailing its various features and specifications.&quot;,
  &quot;features&quot;: [
    &quot;Fits 18\&quot; laptop&quot;,
    &quot;Padded strap support&quot;,
    &quot;Lightweight&quot;,
    &quot;Looks like a normal backpack (when not in use as a jetpack)&quot;,
    &quot;USB-C charging&quot;,
    &quot;15-min battery life&quot;,
    &quot;Retractable boosters&quot;,
    &quot;Steam-powered&quot;,
    &quot;Green/Clean (environmentally friendly)&quot;
  ]
}
```

*/

/* Markdown (render)
## Have a chat

The Gemini API enables you to have freeform conversations across multiple turns.

The [ChatSession](https://ai.google.dev/api/python/google/generativeai/ChatSession) class will store the conversation history for multi-turn interactions.
*/

// [CODE STARTS]
chat = await ai.chats.create({ model: MODEL_ID });

response = await chat.sendMessage({
  message: "In one sentence, explain how a computer works to a young child."
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

A computer is like a super-fast helper brain that listens to your instructions and then quickly shows you pictures, makes sounds, and remembers things for you.

*/

/* Markdown (render)
You can see the chat history:
*/

// [CODE STARTS]
messages = await chat.getHistory();

for (message of messages) {
  console.log(`${message.role}: ${message.parts[0].text}`);
}

// [CODE ENDS]

/* Output Sample

user: In one sentence, explain how a computer works to a young child.

model: A computer is like a super-fast helper brain that listens to your instructions and then quickly shows you pictures, makes sounds, and remembers things for you.

*/

/* Markdown (render)
You can keep sending messages to continue the conversation:
*/

// [CODE STARTS]
response = await chat.sendMessage({
  message: "Okay, how about a more detailed explanation to a high schooler?"
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

At its core, a computer processes information by manipulating vast amounts of electrical signals represented as binary digits (bits) Ã¢â‚¬â€œ simply 0s (off) and 1s (on). The **Central Processing Unit (CPU)** acts as the &quot;brain,&quot; executing billions of simple instructions (like adding numbers, comparing values, or moving data) per second.

To do this quickly, the CPU needs immediate access to data, which comes from **Random Access Memory (RAM)** Ã¢â‚¬â€œ the computer&#x27;s temporary, super-fast workspace where active programs and data are loaded. For permanent storage, your operating system, applications, and files are stored on a **Hard Disk Drive (HDD)** or **Solid State Drive (SSD)**, which retains data even when the power is off.

All these components are interconnected via a **motherboard**, which acts like a central nervous system with high-speed data pathways (**buses**). You provide **input** (keyboard, mouse, microphone), which the computer interprets and processes, then generates **output** (screen display, speaker sound, printer) based on programmed instructions. An **Operating System (OS)** like Windows or macOS manages all these resources, allowing different programs (**software**) to run and interact seamlessly with the hardware.

*/

/* Markdown (render)
Every prompt you send to the model includes parameters that control how the model generates responses. Use a `types.GenerateContentConfig` to set these, or omit it to use the defaults.

Temperature controls the degree of randomness in token selection. Use higher values for more creative responses, and lower values for more deterministic responses.
*/

/* Markdown (render)
Note: Although you can set the `candidateCount` in the generationConfig, 2.0 and later models will only return a single candidate at the this time.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "Give me a numbered list of cat facts.",
  config: {
    maxOutputTokens: 2000,
    temperature: 1.9,
    stopSequences: ["\n6"] // Limit to 5 facts
  }
});

console.log(response.text);

// [CODE ENDS]

/* Output Sample

Here&#x27;s a numbered list of cat facts:

1.  **Cats can make over 100 different sounds**, whereas dogs can only make about 10. The most well-known are purrs, meows, trills, hisses, and growls.
2.  **A group of cats is called a clowder.** A group of kittens is known as an &quot;intrigue&quot; or a &quot;kindle.&quot;
3.  **Cats have a special reflective layer in their eyes called the tapetum lucidum.** This acts like a mirror, reflecting light back into the retina, which gives them excellent night vision and is responsible for the &quot;eyeshine&quot; you see in the dark.
4.  **Domestic cats spend about 70% of their day sleeping** and 15% of their day grooming. This sleeping habit is a leftover from their wild ancestors, who conserved energy for hunting.
5.  **A cat&#x27;s purr can have healing properties.** Studies have shown that the frequency of a cat&#x27;s purr (usually between 25 and 150 Hertz) can aid in bone and muscle repair, relieve pain, and help with wound healing.

*/

/* Markdown (render)
## Learn more

There's lots more to learn!

* For more fun prompts, check out [Market a Jetpack](https://github.com/google-gemini/cookbook/blob/main/examples/Market_a_Jet_Backpack.ipynb).
* Check out the [safety quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Safety.ipynb) next to learn about the Gemini API's configurable safety settings, and what to do if your prompt is blocked.
* For lots more details on using the Javascript SDK, check out the [get started notebook](https://github.com/google-gemini/cookbook/blob/main/quickstarts-js/Get_Started.js) or the [documentation's quickstart](https://ai.google.dev/gemini-api/docs/quickstart#javascript).
*/