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
# Gemini API: Authentication Quickstart

The Gemini API uses API keys for authentication. This guide walks you through creating an API key and using it with the JavaScript SDK.
*/

/* Markdown (render)
## Create an API key

You can [create](https://aistudio.google.com/app/apikey) your API key using Google AI Studio with a single click.

Remember to treat your API key like a password. Don't accidentally save it in a source file you commit to GitHub. This guide shows you the recommended way to securely store your API key.

It's recommended to store your key as an environment variable. When using the Gemini API client libraries, the key will be automatically detected if set as either `GEMINI_API_KEY` or `GOOGLE_API_KEY`.
*/

/* Markdown (render)
## Setup your API key

### API Key Configuration

To ensure security, avoid hardcoding the API key in frontend code. Instead, set it as an environment variable on the server or local machine.

When using the Gemini API client libraries, the key will be automatically detected if set as either `GEMINI_API_KEY` or `GOOGLE_API_KEY`. If both are set, `GOOGLE_API_KEY` takes precedence.

For instructions on setting environment variables across different operating systems, refer to the official documentation: [Set API Key as Environment Variable](https://ai.google.dev/gemini-api/docs/api-key#set-api-env-var)

In code, the key can then be accessed as:

```js
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
```
*/

/* Markdown (render)
## Configure the SDK with your API key

You create a client using your API key. The SDK will automatically look for the `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variables.
*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
// [CODE ENDS]

/* Markdown (render)
Now choose a model. The Gemini API offers different models that are optimized for specific use cases. For more information check [Gemini models](https://ai.google.dev/gemini-api/docs/models).
*/

// [CODE STARTS]
MODEL_ID = "gemini-2.5-flash"; // @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
And that's it! Now you're ready to call the Gemini API.
*/

// [CODE STARTS]
response = await ai.models.generateContent({
  model: MODEL_ID,
  contents: "Please give me JavaScript code to sort a list.",
});

console.log(response.text);
// [CODE ENDS]

/* Output Sample

Of course! JavaScript provides a built-in `sort()` method for arrays, which is very flexible. Here's how you use it, along with common examples.

---

### 1. Basic Sorting (In-Place)

The `sort()` method sorts the elements of an array *in-place* and returns the sorted array. By default, it sorts elements as strings.

**For Strings:**
```javascript
const fruits = ["banana", "apple", "cherry", "date"];
fruits.sort();
console.log("Sorted fruits:", fruits); 
// Output: ["apple", "banana", "cherry", "date"]
```

**For Numbers (with a Compare Function):**
By default, `sort()` treats numbers as strings ("10" comes before "2"). You **must** provide a compare function to sort numbers correctly.

```javascript
const numbers = [3, 1, 4, 1, 5, 9, 2, 6];

// Ascending order
numbers.sort((a, b) => a - b);
console.log("Sorted numbers (ascending):", numbers); 
// Output: [1, 1, 2, 3, 4, 5, 6, 9]

// Descending order
numbers.sort((a, b) => b - a);
console.log("Sorted numbers (descending):", numbers); 
// Output: [9, 6, 5, 4, 3, 2, 1, 1]
```

---

### 2. Creating a New Sorted Array (Not In-Place)

Often, you want to keep the original array unchanged. You can do this by first creating a copy of the array. The spread syntax (`...`) is a great way to do this.

```javascript
const originalNumbers = [3, 1, 4, 1, 5, 9, 2, 6];

// Create a sorted copy
const sortedNumbers = [...originalNumbers].sort((a, b) => a - b);

console.log("Original numbers:", originalNumbers); 
// Output: [3, 1, 4, 1, 5, 9, 2, 6] (unchanged)
console.log("New sorted numbers:", sortedNumbers);   
// Output: [1, 1, 2, 3, 4, 5, 6, 9]
```

---

### 3. Advanced Sorting with a Compare Function

The power of `sort()` comes from custom compare functions.

**Sorting an Array of Objects:**
You can sort objects based on one of their properties.

```javascript
const people = [
    { name: "Alice", age: 30 },
    { name: "Bob", age: 25 },
    { name: "Charlie", age: 35 },
    { name: "David", age: 25 }
];

// Sort by age (ascending)
people.sort((a, b) => a.age - b.age);
console.log("Sorted people by age:", people);
// Output: [ { name: 'Bob', age: 25 }, { name: 'David', age: 25 }, { name: 'Alice', age: 30 }, { name: 'Charlie', age: 35 } ]
```

**Case-Insensitive String Sorting:**
Use `localeCompare()` for robust string comparison.

```javascript
const names = ["Alice", "bob", "Charlie", "David", "frank"];
names.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }));
console.log("Sorted names case-insensitively:", names); 
// Output: ["Alice", "bob", "Charlie", "David", "frank"]
```

---

### When to use which:

*   Use **`array.sort()`** directly if you don't mind modifying the original array. Remember to always use a compare function for numbers.
*   Use **`[...array].sort()`** when you need to keep the original array intact. This is generally a safer practice.

*/

/* Markdown (render)
## Store your key in an environment variable

If you're not using AI Studio, it's recommended to store your key in an environment variable. In most systems, you can do this from your terminal.

To store your key, open your terminal and run:

```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
```

The JavaScript SDK will automatically find the key from the environment variable if you don't explicitly pass it when creating the `GoogleGenAI` instance.

```javascript
// In your Node.js application
const { GoogleGenerativeAI } = require("@google/generative-ai");

// The SDK will automatically look for the GOOGLE_API_KEY environment variable.
const ai = new GoogleGenerativeAI(); 
```

You can also use this environment variable with `curl` to call the API from your terminal.

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[{
          "text": "Please give me JavaScript code to sort a list."
        }]
      }]
    }'
```

*/

/* Markdown (render)
## Learning more

Now that you know how to manage your API key, you have everything you need to [get started](./Get_Started.js) with Gemini. Check all the [quickstart guides](https://github.com/google-gemini/cookbook/tree/main/quickstarts-js) in the Cookbook, and in particular the [Get Started](./Get_Started.js) guide.
*/