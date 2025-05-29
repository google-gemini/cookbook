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
pip install pyaudio websockets python-osc
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

## Run

To run the script:

```
python LyriaRealTime_EAP.py
```

The script takes a prompt from the command line and streams the audio back over
websockets. It now also includes an OSC server for real-time control.
"""
import asyncio
import pyaudio
import os
from google import genai
from google.genai import types
import threading
from pythonosc import dispatcher
from pythonosc import osc_server
# asyncio.Queue is used, so asyncio import is sufficient.

# OSC Server Parameters
OSC_IP = "127.0.0.1"
OSC_PORT = 5005

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
    osc_queue = asyncio.Queue() # Queue for OSC messages

    # OSC Server Thread Function
    def osc_server_thread_func(event_loop, message_queue):
        osc_dispatcher = dispatcher.Dispatcher()

        def default_handler(address, *args):
            print(f"OSC Server received: {address} {args}")
            # Put the message onto the asyncio.Queue in a thread-safe way
            event_loop.call_soon_threadsafe(message_queue.put_nowait, (address, args))

        osc_dispatcher.set_default_handler(default_handler)

        server = osc_server.ThreadingOSCUDPServer((OSC_IP, OSC_PORT), osc_dispatcher)
        print(f"OSC Server listening on {OSC_IP}:{OSC_PORT}")
        server.serve_forever() # This is a blocking call

    # Start the OSC server in a separate thread
    main_event_loop = asyncio.get_event_loop()
    osc_thread = threading.Thread(target=osc_server_thread_func, args=(main_event_loop, osc_queue), daemon=True)
    osc_thread.start()

    async with client.aio.live.music.connect(model=MODEL) as session:
        async def receive():
            chunks_count = 0
            output_stream = p.open(
                format=FORMAT, channels=CHANNELS, rate=OUTPUT_RATE, output=True, frames_per_buffer=CHUNK)
            async for message in session.receive():
                chunks_count += 1
                if chunks_count == 1:
                    await asyncio.sleep(BUFFER_SECONDS)
                if message.server_content:
                    audio_data = message.server_content.audio_chunks[0].data
                    output_stream.write(audio_data)
                elif message.filtered_prompt:
                    print("Prompt was filtered out: ", message.filtered_prompt)
                else:
                    print("Unknown error occured with message: ", message)
                await asyncio.sleep(10**-12)

        async def send():
            print("OSC message handler ready. Waiting for messages on the queue...")
            while True:
                address, args = await osc_queue.get()
                # Minimal logging for every message, detailed logging within handlers
                # print(f"OSC message received: {address} {args}")

                if address == "/lyria/setPrompts":
                    if not args or not isinstance(args[0], str):
                        print("Error: /lyria/setPrompts expects a single string argument (e.g., 'Piano:1,Drums:0.5').")
                        osc_queue.task_done()
                        continue
                    
                    prompt_str = args[0]
                    print(f"Received /lyria/setPrompts with \"{prompt_str}\". Parsing...")
                    parsed_prompts = []
                    segments = prompt_str.split(',')
                    malformed_segment_exists = False

                    for segment_str_raw in segments:
                        segment_str = segment_str_raw.strip()
                        if not segment_str: continue

                        parts = segment_str.split(':', 1)
                        if len(parts) == 2:
                            text_p = parts[0].strip()
                            weight_s = parts[1].strip()
                            if not text_p:
                                print(f"Error: Empty prompt text in segment '{segment_str_raw}'.")
                                malformed_segment_exists = True
                                continue
                            try:
                                weight_f = float(weight_s)
                                parsed_prompts.append(types.WeightedPrompt(text=text_p, weight=weight_f))
                            except ValueError:
                                print(f"Error: Invalid weight '{weight_s}' in segment '{segment_str_raw}'. Must be a number.")
                                malformed_segment_exists = True
                        else:
                            print(f"Error: Segment '{segment_str_raw}' is not in 'text:weight' format.")
                            malformed_segment_exists = True
                    
                    if parsed_prompts:
                        prompt_repr = [f"'{p.text}':{p.weight}" for p in parsed_prompts]
                        if malformed_segment_exists:
                            print(f"Partially sending {len(parsed_prompts)} valid weighted prompt(s) due to errors: {', '.join(prompt_repr)}")
                        else:
                            print(f"Sending multiple weighted prompts: {', '.join(prompt_repr)}")
                        await session.set_weighted_prompts(prompts=parsed_prompts)
                    else:
                        print("Error: No valid prompts parsed from input. No action taken.")

                elif address == "/lyria/play":
                    print("Received /lyria/play. Calling session.play().")
                    await session.play()

                elif address == "/lyria/pause":
                    print("Received /lyria/pause. Calling session.pause().")
                    await session.pause()

                elif address == "/lyria/stop":
                    print("Received /lyria/stop. Calling session.stop().")
                    await session.stop()
                    osc_queue.task_done()
                    print("Send loop is terminating due to /lyria/stop command.")
                    return # Exit the send loop

                elif address == "/lyria/bpm":
                    if not args:
                        print("Error: /lyria/bpm expects one argument (number or 'AUTO').")
                        osc_queue.task_done()
                        continue
                    
                    bpm_arg = args[0]
                    if isinstance(bpm_arg, str) and bpm_arg.upper() == 'AUTO':
                        if hasattr(config, 'bpm'):
                            del config.bpm
                        print(f"Setting BPM to AUTO, requires resetting context.")
                    else:
                        try:
                            bpm_value = int(bpm_arg)
                            config.bpm = bpm_value
                            print(f"Setting BPM to {bpm_value}, requires resetting context.")
                        except ValueError:
                            print(f"Error: Invalid BPM value '{bpm_arg}'. Must be a number or 'AUTO'.")
                            osc_queue.task_done()
                            continue
                    await session.set_music_generation_config(config=config)
                    await session.reset_context()

                elif address == "/lyria/scale":
                    if not args or not isinstance(args[0], str):
                        print("Error: /lyria/scale expects one string argument (scale name or 'AUTO').")
                        osc_queue.task_done()
                        continue

                    scale_arg = args[0]
                    if scale_arg.upper() == 'AUTO':
                        if hasattr(config, 'scale'):
                            del config.scale
                        print(f"Setting Scale to AUTO, requires resetting context.")
                    else:
                        found_scale_enum_member = None
                        for scale_member in types.Scale: # types.Scale is an enum
                            if scale_member.name.lower() == scale_arg.lower():
                                found_scale_enum_member = scale_member
                                break
                        if found_scale_enum_member:
                            config.scale = found_scale_enum_member
                            print(f"Setting scale to {found_scale_enum_member.name}, requires resetting context.")
                        else:
                            print(f"Error: Scale name '{scale_arg}' not found in types.Scale. Available: {[m.name for m in types.Scale]}")
                            osc_queue.task_done()
                            continue
                    await session.set_music_generation_config(config=config)
                    await session.reset_context()
                
                else:
                    print(f"Unrecognized OSC address: {address}")

                osc_queue.task_done()

        print("Starting with some piano")
        await session.set_weighted_prompts(
            prompts=[types.WeightedPrompt(text="Piano", weight=1.0)]
        )

        config.bpm = 120
        config.scale = types.Scale.A_FLAT_MAJOR_F_MINOR
        print(f"Setting initial BPM to {config.bpm} and scale to {config.scale.name}")
        await session.set_music_generation_config(config=config)

        print(f"Let's get the party started!")
        await session.play()

        send_task = asyncio.create_task(send())
        receive_task = asyncio.create_task(receive())

        try:
            await asyncio.gather(send_task, receive_task)
        except Exception as e:
            print(f"Error in main tasks: {e}")
        finally:
            print("Cleaning up PyAudio...")
            p.terminate()
            # Server thread is daemon, so it will exit when main program exits.
            # If server was not daemon, you might need server.shutdown() here.
            print("Exiting main function.")

asyncio.run(main())
