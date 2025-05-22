# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
## Setup

To install the dependencies for this script, run:

```
pip install pyaudio websockets
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

## Run

To run the script:

```
python LyriaRealTime_EAP.py
```

The script takes a prompt from the command line and streams the audio back over
websockets.
"""
import asyncio
import pyaudio
import os
from google import genai
from google.genai import types

# Longer buffer reduces chance of audio drop, but also delays audio and user commands.
BUFFER_SECONDS=1
CHUNK=4200
FORMAT=pyaudio.paInt16
CHANNELS=2
MODEL='models/lyria-realtime-exp'
OUTPUT_RATE=48000

api_key = os.environ.get("GOOGLE_API_KEY")

if api_key is None:
    print("Please enter your API key")
    api_key = input("API Key: ").strip()

client = genai.Client(
    api_key=api_key,
    http_options={'api_version': 'v1alpha',}, # v1alpha since Lyria RealTime is only experimental
)

async def main():
    p = pyaudio.PyAudio()
    config = types.LiveMusicGenerationConfig()
    async with client.aio.live.music.connect(model=MODEL) as session:
        async def receive():
            chunks_count = 0
            output_stream = p.open(
                format=FORMAT, channels=CHANNELS, rate=OUTPUT_RATE, output=True, frames_per_buffer=CHUNK)
            async for message in session.receive():
                chunks_count += 1
                if chunks_count == 1:
                    # Introduce a delay before starting playback to have a buffer for network jitter.
                    await asyncio.sleep(BUFFER_SECONDS)
                # print("Received chunk: ", message)
                if message.server_content:
                # print("Received chunk with metadata: ", message.server_content.audio_chunks[0].source_metadata)
                    audio_data = message.server_content.audio_chunks[0].data
                    output_stream.write(audio_data)
                elif message.filtered_prompt:
                    print("Prompt was filtered out: ", message.filtered_prompt)
                else:
                    print("Unknown error occured with message: ", message)
                await asyncio.sleep(10**-12)

        async def send():
            await asyncio.sleep(5) # Allow initial prompt to play a bit

            while True:
                print("Set new prompt ((bpm=<number|'AUTO'>, scale=<enum|'AUTO'>, top_k=<number|'AUTO'>, 'play', 'pause', 'prompt1:w1,prompt2:w2,...', or single text prompt)")
                prompt_str = await asyncio.to_thread(
                    input,
                    " > "
                )

                if not prompt_str: # Skip empty input
                    continue

                if prompt_str.lower() == 'q':
                    print("Sending STOP command.")
                    await session.stop();
                    return False

                if prompt_str.lower() == 'play':
                    print("Sending PLAY command.")
                    await session.play()
                    continue

                if prompt_str.lower() == 'pause':
                    print("Sending PAUSE command.")
                    await session.pause()
                    continue

                if prompt_str.startswith('bpm='):
                  if prompt_str.strip().endswith('AUTO'):
                    del config.bpm
                    print(f"Setting BPM to AUTO, which requires resetting context.")
                  else:
                    bpm_value = int(prompt_str.removeprefix('bpm='))
                    print(f"Setting BPM to {bpm_value}, which requires resetting context.")
                    config.bpm=bpm_value
                  await session.set_music_generation_config(config=config)
                  await session.reset_context()
                  continue

                if prompt_str.startswith('scale='):
                  if prompt_str.strip().endswith('AUTO'):
                    del config.scale
                    print(f"Setting Scale to AUTO, which requires resetting context.")
                  else:
                    found_scale_enum_member = None
                    for scale_member in types.Scale: # types.Scale is an enum
                        if scale_member.name.lower() == prompt_str.lower():
                            found_scale_enum_member = scale_member
                            break
                    if found_scale_enum_member:
                        print(f"Setting scale to {found_scale_enum_member.name}, which requires resetting context.")
                        config.scale = found_scale_enum_member
                    else:
                        print("Error: Matching enum not found.")
                  await session.set_music_generation_config(config=config)
                  await session.reset_context()
                  continue

                if prompt_str.startswith('top_k='):
                    top_k_value = int(prompt_str.removeprefix('top_k='))
                    print(f"Setting TopK to {top_k_value}.")
                    config.top_k = top_k_value
                    await session.set_music_generation_config(config=config)
                    await session.reset_context()
                    continue

                # Check for multiple weighted prompts "prompt1:number1, prompt2:number2, ..."
                if ":" in prompt_str:
                    parsed_prompts = []
                    segments = prompt_str.split(',')
                    malformed_segment_exists = False # Tracks if any segment had a parsing error

                    for segment_str_raw in segments:
                        segment_str = segment_str_raw.strip()
                        if not segment_str: # Skip empty segments (e.g., from "text1:1, , text2:2")
                            continue

                        # Split on the first colon only, in case prompt text itself contains colons
                        parts = segment_str.split(':', 1)

                        if len(parts) == 2:
                            text_p = parts[0].strip()
                            weight_s = parts[1].strip()

                            if not text_p: # Prompt text should not be empty
                                print(f"Error: Empty prompt text in segment '{segment_str_raw}'. Skipping this segment.")
                                malformed_segment_exists = True
                                continue # Skip this malformed segment
                            try:
                                weight_f = float(weight_s) # Weights are floats
                                parsed_prompts.append(types.WeightedPrompt(text=text_p, weight=weight_f))
                            except ValueError:
                                print(f"Error: Invalid weight '{weight_s}' in segment '{segment_str_raw}'. Must be a number. Skipping this segment.")
                                malformed_segment_exists = True
                                continue # Skip this malformed segment
                        else:
                            # This segment is not in "text:weight" format.
                            print(f"Error: Segment '{segment_str_raw}' is not in 'text:weight' format. Skipping this segment.")
                            malformed_segment_exists = True
                            continue # Skip this malformed segment

                    if parsed_prompts: # If at least one prompt was successfully parsed.
                        prompt_repr = [f"'{p.text}':{p.weight}" for p in parsed_prompts]
                        if malformed_segment_exists:
                            print(f"Partially sending {len(parsed_prompts)} valid weighted prompt(s) due to errors in other segments: {', '.join(prompt_repr)}")
                        else:
                            print(f"Sending multiple weighted prompts: {', '.join(prompt_repr)}")
                        await session.set_weighted_prompts(prompts=parsed_prompts)
                    else: # No valid prompts were parsed from the input string that contained ":"
                        print("Error: Input contained ':' suggesting multi-prompt format, but no valid 'text:weight' segments were successfully parsed. No action taken.")

                    continue

                # If none of the above, treat as a regular single text prompt
                print(f"Sending single text prompt: \"{prompt_str}\"")
                await session.set_weighted_prompts(
                    prompts=[types.WeightedPrompt(text=prompt_str, weight=1.0)]
                )

        print("Starting with some piano")
        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text="Piano", weight=1.0)]
        )

        # Set initial BPM and Scale
        config.bpm = 120
        config.scale = types.Scale.A_FLAT_MAJOR_F_MINOR # Example initial scale
        print(f"Setting initial BPM to {config.bpm} and scale to {config.scale.name}")
        await session.set_music_generation_config(config=config)

        print(f"Let's get the party started!")
        await session.play()

        send_task = asyncio.create_task(send())
        receive_task = asyncio.create_task(receive())

        # Don't quit the loop until tasks are done
        await asyncio.gather(send_task, receive_task)

    # Clean up PyAudio
    p.terminate()

asyncio.run(main())
