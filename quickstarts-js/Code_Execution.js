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

  const model = "gemini-2.5-flash-lite"; 
  
  try {
    const response = await client.models.generateContent({
      model: model,
      // 🚨 THIS IS THE KEY PART: Enabling the Code Execution Tool
      tools: [
        { codeExecution: {} } 
      ],
      contents: "Calculate the sum of the first 50 prime numbers. Write and run python code to solve this."
    });

    // The response includes the model's thought process, the code it ran, and the final answer.
    console.log(response.text);
    
  } catch (error) {
    console.error("Error:", error);
  }
}

run();