# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
pip install google-genai opencv-python pyaudio pillow mss
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

Important: **Use headphones**. This script uses the system default audio
input and output, which often won't include echo cancellation. So to prevent
the model from interrupting itself it is important that you use headphones. 

## Run

To run the script:

```
python Get_started_LiveAPI.py
```

The script takes a video-mode flag `--mode`, this can be "camera", "screen", or "none".
The default is "camera". To share your screen run:

```
python Get_started_LiveAPI.py --mode screen
```
"""

import asyncio
import base64
import io
import os
import sys
import traceback
import argparse

import cv2
import pyaudio
import PIL.Image
import mss

from google import genai
from google.genai import types

if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

# --- Audio Configuration ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

# --- Model Configuration ---
MODEL = "models/gemini-2.5-flash-native-audio-preview-12-2025"
DEFAULT_MODE = "camera"


client = genai.Client(
    api_key=os.environ.get("GEMINI_API_KEY"),
    http_options={"api_version": "v1beta"},
)

# Live session configuration
# Trigger tokens sent so that model does not hallucinate in long conversations
# Sliding window to retain the context within the context window limit
CONFIG = types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name = "Zephyr")
        )
    ),
    context_window_compression=types.ContextWindowCompressionConfig(
        trigger_tokens = 25600,
        sliding_window = types.SlidingWindow(target_tokens=12800),
    ),
)

pya = pyaudio.PyAudio()


class AudioVideoLoop:
    def __init__(self, video_mode=DEFAULT_MODE):
        self.video_mode = video_mode

        self.audio_in_queue = asyncio.Queue()
        self.out_queue = asyncio.Queue(maxsize = 5) # Limit size to avoid excess memory use

        self.session = None
        self.audio_stream = None

    # --- Audio Handling ---

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        
        try:
            while True:
                data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
                payload = {
                    "data": data,
                    "mime_type": "audio/pcm"
                }
                # To reduce latency instead of watiing to push in queue we pop oldest item in queue if its full
                # This helps to keep the audio stream real time
                try:
                    self.out_queue.put_nowait(payload)
                except asyncio.QueueFull:
                    _ = self.out_queue.get_nowait()  
                    self.out_queue.put_nowait(payload)

        except asyncio.CancelledError:
            pass
        finally:
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        try:
            while True:
                bytestream = await self.audio_in_queue.get()
                await asyncio.to_thread(stream.write, bytestream)
        except asyncio.CancelledError:
            pass
        finally:
            if stream:
                stream.stop_stream()
                stream.close()

    async def receive_audio(self):
        """Read from the websocket and write PCM chunks to the output queue."""
        try:
            while True:
                turn = self.session.receive()
                async for response in turn:
                    if data := response.data:
                        self.audio_in_queue.put_nowait(data)
                        continue
                    if text := response.text:
                        print(text, end="")

                # If you interrupt the model, it sends a turn_complete.
                # For interruptions to work, we need to stop playback.
                # So empty out the audio queue because it may have loaded
                # much more audio than has played yet.
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()
        except asyncio.CancelledError:
            pass

    # --- Video Handling ---

    def _capture_frame(self, cap):
        """Capture frame from camera and convert to base64 JPEG."""
        # Read the frame
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None
        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def capture_frames(self):
        cap = await asyncio.to_thread(
            cv2.VideoCapture, 0
        )  # 0 represents the default camera

        try:
            while True:
                frame = await asyncio.to_thread(self._capture_frame, cap)
                if frame is None:
                    break

                await asyncio.sleep(1.0)
                await self.out_queue.put(frame)
        except asyncio.CancelledError:
            pass
        finally:
            cap.release()

    def _capture_screen(self):
        sct = mss.mss()
        monitor = sct.monitors[0]
        
        i = sct.grab(monitor)
        
        img = PIL.Image.frombytes("RGB", i.size, i.rgb)

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def capture_screen(self):
        try:
            while True:
                frame = await asyncio.to_thread(self._capture_screen)
                if frame is None:
                    break

                await asyncio.sleep(1.0)
                await self.out_queue.put(frame)
        except asyncio.CancelledError:
            pass

    # --- Text & Main Loop ---

    async def send_text(self):
        try:
            while True:
                text = await asyncio.to_thread(
                    input,
                    "message > ",
                )
                if text.lower() == "q":
                    print("👋 Exiting on user request...")
                    break
                await self.session.send_client_content(
                    turns=types.Content(parts=[types.Part(text=text or "")]),
                    turn_complete=True,
                )
        except asyncio.CancelledError:
            pass

    async def send_realtime(self):
        try:
            while True:
                msg = await self.out_queue.get()
                if msg["mime_type"].startswith("audio/"):
                    await self.session.send_realtime_input(audio=msg)
                else:
                    await self.session.send_realtime_input(media=msg)
        except asyncio.CancelledError:
            pass

    async def run(self):
        """Run all tasks to handle audio/video/text interaction"""
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                # Re-initialize queue for fresh session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                
                if self.video_mode == "camera":
                    tg.create_task(self.capture_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.capture_screen())

                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            self.audio_stream.close()
            traceback.print_exception(EG)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    args = parser.parse_args()
    main = AudioVideoLoop(video_mode=args.mode)
    asyncio.run(main.run())
