# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

# To install the dependencies for this script, run:
#  pip install opencv-python pyaudio pillow websockets
# And to run this script, ensure the GOOGLE_API_KEY environment
# variable is set to the key you obtained from Google AI Studio.

import asyncio
import base64
import json
import io
import os
import sys
import traceback

import cv2
import pyaudio
import PIL.Image

from websockets.asyncio.client import connect

if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup
    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 512

host='generativelanguage.googleapis.com'
model = "gemini-2.0-flash-exp"

api_key = os.environ['GOOGLE_API_KEY']
uri = f"wss://{host}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={api_key}"

class AudioLoop:
    def __init__(self):
        self.audio_in_queue = asyncio.Queue()
        self.audio_out_queue = asyncio.Queue()
        self.video_out_queue = asyncio.Queue()

        self.ws = None

        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

    async def startup(self):
        setup_msg = {"setup": {"model": f"models/{model}"}}
        await self.ws.send(json.dumps(setup_msg))
        raw_response = await self.ws.recv(decode=False)
        setup_response = json.loads(raw_response.decode("ascii"))

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "q":
                break

            msg = {
                "client_content": {
                    "turn_complete": True,
                    "turns": [{"role": "user", "parts": [{"text": text}]}],
                }
            }
            await self.ws.send(json.dumps(msg))

    def _get_frame(self, cap):
        # Read the frame
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None

        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)  # Now using RGB frame
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {'mime_type': mime_type, 'data': base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        # This takes about a second, and will block the whole program
        # causing the audio pipeline to overflow if you don't to_thread it.
        cap = await asyncio.to_thread(cv2.VideoCapture,0)  # 0 represents the default camera

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break
            await asyncio.sleep(1.0)

            self.video_out_queue.put_nowait(frame)

        # Release the VideoCapture object
        cap.release()

    async def send_frames(self):
        while True:
            frame = await self.video_out_queue.get()
            msg = {
                "realtime_input": {
                    "media_chunks": [
                        frame
                    ]
                }
            }
            msg = json.dumps(msg)
            await self.ws.send(msg)


    async def listen_audio(self):
        pya = pyaudio.PyAudio()

        mic_info = pya.get_default_input_device_info()
        stream = pya.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        while True:
            data = await asyncio.to_thread(stream.read, CHUNK_SIZE)
            self.audio_out_queue.put_nowait(data)

    async def send_audio(self):
        while True:
            chunk = await self.audio_out_queue.get()
            msg = {
                "realtime_input": {
                    "media_chunks": [
                        {"data": base64.b64encode(chunk).decode(), "mime_type": "audio/pcm"}
                    ]
                }
            }
            msg = json.dumps(msg)
            await self.ws.send(msg)

    async def receive_audio(self):
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        async for raw_response in self.ws:
            # Other things could be returned here, but we'll ignore those for now.
            response = json.loads(raw_response.decode("ascii"))

            try:
                b64data = response["serverContent"]["modelTurn"]["parts"][0]["inlineData"]["data"]
            except KeyError:
                pass
            else:
                pcm_data = base64.b64decode(b64data)
                self.audio_in_queue.put_nowait(pcm_data)

            try:
                turn_complete = response["serverContent"]["turnComplete"]
            except KeyError:
                pass
            else:
                if turn_complete:
                    # If you interrupt the model, it sends an end_of_turn.
                    # For interruptions to work, we need to empty out the audio queue
                    # Because it may have loaded much more audio than has played yet.
                    print("\nEnd of turn")
                    while not self.audio_in_queue.empty():
                        self.audio_in_queue.get_nowait()

    async def play_audio(self):
        pya = pyaudio.PyAudio()
        stream = pya.open(format=FORMAT, channels=CHANNELS, rate=RECEIVE_SAMPLE_RATE, output=True)
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self):
        """Takes audio chunks off the input queue, and writes them to files.

        Splits and displays files if the queue pauses for more than `max_pause`.
        """
        async with await connect(
            uri, additional_headers={"Content-Type": "application/json"}
        ) as ws:
            self.ws = ws

            await self.startup()

            async with asyncio.TaskGroup() as tg:
                send_text_task = tg.create_task(self.send_text())

                def cleanup(task):
                    for t in tg._tasks:
                        t.cancel()

                send_text_task.add_done_callback(cleanup)

                tg.create_task(self.listen_audio())
                tg.create_task(self.send_audio())
                tg.create_task(self.get_frames())
                tg.create_task(self.send_frames())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                def check_error(task):
                    if task.cancelled():
                        return

                    if task.exception() is None:
                        return

                    e = task.exception()
                    traceback.print_exception(None, e, e.__traceback__)
                    sys.exit(1)

                for task in tg._tasks:
                    task.add_done_callback(check_error)


if __name__ == "__main__":
    main = AudioLoop()
    asyncio.run(main.run())
