/**
 * Copyright 2025 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Initialize the client
const client = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

async function run() {
  console.log("--- Sending request to Gemini with Code Execution enabled ---");

  // Bot Suggestion 1: Use MODEL_ID for consistency
  const MODEL_ID = "gemini-2.5-flash-lite"; 
  
  try {
    const response = await client.models.generateContent({
      model: MODEL_ID,
      tools: [
        { codeExecution: {} } 
      ],
      contents: "Calculate the sum of the first 50 prime numbers. Write and run python code to solve this."
    });

    // Bot Suggestion 2: Parse response to show the code and the result separately
    // This loops through the "parts" of the response to show exactly what the model did.
    if (response.candidates && response.candidates[0].content.parts) {
      for (const part of response.candidates[0].content.parts) {
        if (part.text) {
          console.log(part.text);
        } else if (part.executableCode) {
          console.log('\n--- Executable Code ---');
          console.log(part.executableCode.code);
        } else if (part.codeExecutionResult) {
          console.log('\n--- Code Execution Result ---');
          console.log(part.codeExecutionResult.output);
        }
      }
    } else {
      // Fallback if structure is different
      console.log(response.text);
    }
    
  } catch (error) {
    console.error("Error:", error);
  }
}

run();