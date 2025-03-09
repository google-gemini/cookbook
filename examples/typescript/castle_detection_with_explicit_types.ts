/**
 * @license
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { 
    ChatSession, 
    Content, 
    GenerateContentStreamResult, 
    GenerativeContentBlob, 
    GenerativeModel, 
    GoogleGenerativeAI,
    GoogleGenerativeAIError
} from "@google/generative-ai";
import fs from "fs";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const mediaPath = __dirname + "/../assets";

if (!process.env.API_KEY) {
  throw new Error('API_KEY environment variable is required. You can get one from https://makersuite.google.com/app/apikey');
}

/**
 * This example demonstrates how to use the Gemini API for a medieval castle analysis chat tool
 * It shows how to:
 * 1. Set up a chat session with explicit TypeScript types
 * 2. Include conversation history and system instruction
 * 3. Send images for analysis
 * 4. Handle streaming responses
 */
async function chatWithExplicitTypes(): Promise<void> {
  // Make sure to import the Google Generative AI Node.js SDK
  // import { GoogleGenerativeAI } from "@google/generative-ai";
  // Initialize the Gemini API with your API key.
  const genAI: GoogleGenerativeAI = new GoogleGenerativeAI(process.env.API_KEY);
  
  // Create a specialized castle expert model using the system instruction.
  const model: GenerativeModel = genAI.getGenerativeModel({ 
    model: "gemini-1.5-flash",
    systemInstruction: "You are a medieval castle expert."
  });

  /* 
  * Set up the initial conversation with the castle expert. 
  * If you leave out the history, the model will start with a blank slate. 
  */
  const history: Content[] = [
    {
      role: "user",
      parts: [{ text: "Hello. Would you like to see my medieval castle?" }],
    },
    {
      role: "model",
      parts: [{ text: "Yes, I would love to see your medieval castle! Please tell me about it or describe it to me." }],
    },
  ];

  // Start a new chat session with our conversation history
  const chat: ChatSession = model.startChat({ history });

  // Prepare the castle image for analysis
  const image: GenerativeContentBlob = {
    data: Buffer.from(fs.readFileSync(`${mediaPath}/castle.png`)).toString("base64"),
    mimeType: "image/png"
  };

  // Send the image to the model and stream its analysis
  // For a non-streaming response, use sendMessage instead of sendMessageStream
  try {
    const resultStream: GenerateContentStreamResult = await chat.sendMessageStream([
      "Here it is! My medieval castle.", 
      { inlineData: image }
    ]);

    // Print the streaming response
    process.stdout.write('\n\nModel response:\n');
    for await (const chunk of resultStream.stream) {
        const chunkText = chunk.text();
        process.stdout.write(chunkText);
    }
  } catch (error) {
    if (error instanceof GoogleGenerativeAIError) {
        console.error('A Gemini-specific error occurred: ', error.message);
    } else {
        console.error('An error occurred: ', error);
    }
  }
}

chatWithExplicitTypes().catch(error => {
    console.error('Error running examples: ', error);
    process.exit(1);
});