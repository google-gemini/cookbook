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

import { GoogleGenAI } from "https://esm.sh/@google/genai";

// Get elements from the DOM
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const result = document.getElementById('result');
const snap = document.getElementById('snap');

// Create a new element for the mirror's speech
const speech = document.createElement('p');
document.body.insertBefore(speech, document.body.firstChild);


const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
const MODEL_ID = "gemini-2.5-flash-image-preview";

// Get access to the webcam
async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        video.srcObject = stream;
        video.play();
    } catch (err) {
        console.error("Error accessing webcam: ", err);
    }
}

async function edit_camera_image() {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, 640, 480);
    const dataUrl = canvas.toDataURL('image/png');
    const imageData = dataUrl.split(',')[1]; // Get only base64 string

    const imagePart = {
        inlineData: {
            data: imageData,
            mimeType: "image/png"
        }
    };

    const response = await ai.models.generateContent({
        model: MODEL_ID,
        contents: [imagePart, 'Mirror, mirror on the wall, make me a princess after all!'],
        config: {
            systemInstruction: "You are a magic mirror. You are witty, a bit sassy, and you always speak in rhymes. You are here to make people's dreams come true, but you do it with a bit of flair and humor.",
        }
    });

    for (const part of response.candidates[0].content.parts) {
        if (part.text) {
            speech.textContent = part.text;
        }
        if (part.inlineData) {
            const base64ImageBytes = part.inlineData.data;
            const imageUrl = `data:image/png;base64,${base64ImageBytes}`;
            result.src = imageUrl;
        }
    }
}

// Event listener for the snap button
snap.addEventListener('click', edit_camera_image);

// Start the webcam when the page loads
window.addEventListener('load', startWebcam);
