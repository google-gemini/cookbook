# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Written by:
#   - Freddy Boulton (https://github.com/freddyaboulton)
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

This script launches a pure-python web-based UI for the Gen AI SDK Voice Chat.

To install the dependencies for this script, run:

```
pip install fastrtc google-genai python-dotenv
```

If the `GOOGLE_API_KEY` environment variable is set,
it will automatically be used. Otherwise, you will be prompted
to enter it.


## Run

To run the script:

```
python live_api_ui.py
```
"""

import asyncio
import base64
import os
from typing import Literal

import gradio as gr
import numpy as np
from fastrtc import (
    AsyncStreamHandler,
    WebRTC,
    wait_for_item,
)
from google import genai
from google.genai.types import (
    LiveConnectConfig,
    PrebuiltVoiceConfig,
    SpeechConfig,
    VoiceConfig,
)

try:
    from dotenv import load_dotenv

    load_dotenv()
except (ImportError, ModuleNotFoundError):
    pass


class GeminiHandler(AsyncStreamHandler):
    """Handler for the Gemini API"""

    def __init__(
        self,
        expected_layout: Literal["mono"] = "mono",
        output_sample_rate: int = 24000,
        output_frame_size: int = 480,
    ) -> None:
        super().__init__(
            expected_layout,
            output_sample_rate,
            output_frame_size,
            input_sample_rate=16000,
        )
        self.input_queue: asyncio.Queue = asyncio.Queue()
        self.output_queue: asyncio.Queue = asyncio.Queue()
        self.quit: asyncio.Event = asyncio.Event()

    def copy(self) -> "GeminiHandler":
        return GeminiHandler(
            expected_layout="mono",
            output_sample_rate=self.output_sample_rate,
            output_frame_size=self.output_frame_size,
        )

    async def start_up(self):
        await self.wait_for_args()
        api_key, voice_name = self.latest_args[1:]

        client = genai.Client(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            http_options={"api_version": "v1alpha"},
        )

        config = LiveConnectConfig(
            response_modalities=["AUDIO"],  # type: ignore
            speech_config=SpeechConfig(
                voice_config=VoiceConfig(
                    prebuilt_voice_config=PrebuiltVoiceConfig(
                        voice_name=voice_name,
                    )
                )
            ),
        )
        async with client.aio.live.connect(
            model="gemini-2.0-flash-exp", config=config
        ) as session:
            async for audio in session.start_stream(
                stream=self.stream(), mime_type="audio/pcm"
            ):
                if audio.data:
                    array = np.frombuffer(audio.data, dtype=np.int16)
                    self.output_queue.put_nowait((self.output_sample_rate, array))

    async def stream(self):
        while not self.quit.is_set():
            yield await wait_for_item(self.input_queue)

    async def receive(self, frame: tuple[int, np.ndarray]) -> None:
        _, array = frame
        array = array.squeeze()
        audio_message = base64.b64encode(array.tobytes()).decode("UTF-8")
        self.input_queue.put_nowait(audio_message)

    async def emit(self) -> tuple[int, np.ndarray] | None:
        return await wait_for_item(self.output_queue)

    def shutdown(self) -> None:
        self.quit.set()


with gr.Blocks() as demo:
    gr.HTML(
        """
        <div style='text-align: center'>
            <h1>Gen AI SDK Voice Chat</h1>
            <p>Speak with Gemini using real-time audio streaming</p>
            <p>Get an API Key <a href="https://support.google.com/googleapi/answer/6158862?hl=en">here</a></p>
        </div>
    """
    )
    with gr.Row() as api_key_row:
        api_key = gr.Textbox(
            label="API Key",
            placeholder="Enter your API Key",
            value=os.getenv("GOOGLE_API_KEY", ""),
            type="password",
        )
    with gr.Row(visible=False) as row:
        with gr.Column():
            webrtc = WebRTC(
                label="Audio",
                modality="audio",
                mode="send-receive",
                pulse_color="rgb(35, 157, 225)",
                icon_button_color="rgb(255, 255, 255)",
                icon="https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png",
            )
            voice = gr.Dropdown(
                label="Voice",
                choices=[
                    "Puck",
                    "Charon",
                    "Kore",
                    "Fenrir",
                    "Aoede",
                ],
                value="Puck",
            )
    webrtc.stream(
        GeminiHandler(),
        inputs=[webrtc, api_key, voice],
        outputs=[webrtc],
        time_limit=90,
        concurrency_limit=2,
    )
    api_key.submit(
        lambda: (gr.update(visible=False), gr.update(visible=True)),
        None,
        [api_key_row, row],
    )


if __name__ == "__main__":
    demo.launch()
