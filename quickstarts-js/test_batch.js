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
# Gemini API: testing batch


*/

// [CODE STARTS]
module = await import("https://esm.sh/@google/genai@1.4.0");
GoogleGenAI = module.GoogleGenAI;
ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

MODEL_ID = "gemini-2.5-flash" // ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]
// [CODE ENDS]

/* Markdown (render)
##  Create batch job with inline requests

*/

// [CODE STARTS]
    const inlinedRequests = [
        {
            contents: [{parts: [{text: 'A big letter A surrounded by animals starting with the A letter'}]}],
            config: {responseModalities: ['TEXT', 'IMAGE']}
        },
        {
            contents: [{parts: [{text: 'A big letter B surrounded by animals starting with the B letter'}]}],
            config: {responseModalities: ['TEXT', 'IMAGE']}
        }
    ]

    const inlineBatchJob = await ai.batches.create({
        model: 'gemini-2.5-flash-image',
        src: inlinedRequests,
        config: {
            displayName: 'inlined-image-requests-job-1',
        }
    });

    console.log(inlineBatchJob);

// [CODE ENDS]
/* Markdown (render)
##  Monitor job status

*/
// [CODE STARTS]
    let batchJob;
    const completedStates = new Set([
        'JOB_STATE_SUCCEEDED',
        'JOB_STATE_FAILED',
        'JOB_STATE_CANCELLED',
        'JOB_STATE_EXPIRED',
    ]);

    try {
        batchJob = await ai.batches.get({name: inlineBatchJob.name});
        while (!completedStates.has(batchJob.state)) {
            console.log(`Current state: ${batchJob.state}`);
            // Wait for 10 seconds before polling again
            await new Promise(resolve => setTimeout(resolve, 10000));
            batchJob = await ai.batches.get({ name: batchJob.name });
        }
        console.log(`Job finished with state: ${batchJob.state}`);
    } catch (error) {
        console.error(`An error occurred while polling job ${inlineBatchJob.name}:`, error);
        return;
    }

// [CODE ENDS]
/* Markdown (render)
##  Retrieve results

*/
// [CODE STARTS]
    if (batchJob.state === 'JOB_STATE_SUCCEEDED') {
        if (batchJob.dest?.inlinedResponses) {
            console.log("Results are inline:");
            for (let i = 0; i < batchJob.dest.inlinedResponses.length; i++) {
                const inlineResponse = batchJob.dest.inlinedResponses[i];
                console.log(`Response ${i + 1}:`);
                if (inlineResponse.response) {
                    for (const part of inlineResponse.response.candidates[0].content.parts) {
                        if (part.text) {
                            console.log(part.text);
                        } else if (part.inlineData) {
                            console.log(`Image mime type: ${part.inlineData.mimeType}`);
                        }
                    }
                } else if (inlineResponse.error) {
                    console.error(`Error: ${inlineResponse.error}`);
                }
            }
        } else {
            console.log("No inline results found.");
        }
    } else if (batchJob.state === 'JOB_STATE_FAILED') {
         console.error(`Error: ${typeof batchJob.error === 'string' ? batchJob.error : batchJob.error.message || JSON.stringify(batchJob.error)}`);
    }
}
run();

// [CODE ENDS]
