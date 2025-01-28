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

The gradio-webrtc install fails unless you have ffmpeg@6, on mac:

```
brew uninstall ffmpeg
brew install ffmpeg@6
brew link ffmpeg@6
```

Create a virtual python environment, then install the dependencies for this script:

```
pip install websockets numpy gradio-webrtc "gradio>=5.9.1"
```

If installation fails it may be

Before running this script, ensure the `GOOGLE_API_KEY` environment

```
$ export GOOGLE_API_KEY ='add your key here'
```

You can get an api-key from Google AI Studio (https://aistudio.google.com/apikey)

## Run

To run the script:

```
python gemini_gradio_audio.py
```

On the gradio page (http://127.0.0.1:7860/) click record, and talk, gemini will reply. But note that interruptions
don't work.

"""

import os
import base64
import json
import numpy as np
import gradio as gr
import websockets.sync.client
from gradio_webrtc import StreamHandler, WebRTC

__version__ = "0.0.3"

KEY_NAME="GOOGLE_API_KEY"

# Configuration and Utilities
class GeminiConfig:
    """Configuration settings for Gemini API."""
    def __init__(self):
        self.api_key = os.getenv(KEY_NAME)
        self.host = "generativelanguage.googleapis.com"
        self.model = "models/gemini-2.0-flash-exp"
        self.ws_url = f"wss://{self.host}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key={self.api_key}"

class AudioProcessor:
    """Handles encoding and decoding of audio data."""
    @staticmethod
    def encode_audio(data, sample_rate):
        """Encodes audio data to base64."""
        encoded = base64.b64encode(data.tobytes()).decode("UTF-8")
        return {
            "realtimeInput": {
                "mediaChunks": [
                    {
                        "mimeType": f"audio/pcm;rate={sample_rate}",
                        "data": encoded,
                    }
                ],
            },
        }

    @staticmethod
    def process_audio_response(data):
        """Decodes audio data from base64."""
        audio_data = base64.b64decode(data)
        return np.frombuffer(audio_data, dtype=np.int16)

# Gemini Interaction Handler
class GeminiHandler(StreamHandler):
    """Handles streaming interactions with the Gemini API."""
    def __init__(self, expected_layout="mono", output_sample_rate=24000, output_frame_size=480) -> None:
        super().__init__(expected_layout, output_sample_rate, output_frame_size, input_sample_rate=24000)
        self.config = GeminiConfig()
        self.ws = None
        self.all_output_data = None
        self.audio_processor = AudioProcessor()

    def copy(self):
        """Creates a copy of the GeminiHandler instance."""
        return GeminiHandler(
            expected_layout=self.expected_layout,
            output_sample_rate=self.output_sample_rate,
            output_frame_size=self.output_frame_size,
        )

    def _initialize_websocket(self):
        """Initializes the WebSocket connection to the Gemini API."""
        try:
            self.ws = websockets.sync.client.connect(self.config.ws_url, timeout=3000)
            initial_request = {"setup": {"model": self.config.model,"tools":[{"google_search": {}}]}}
            self.ws.send(json.dumps(initial_request))
            setup_response = json.loads(self.ws.recv())
            print(f"Setup response: {setup_response}")
        except websockets.exceptions.WebSocketException as e:
            print(f"WebSocket connection failed: {str(e)}")
            self.ws = None
        except Exception as e:
            print(f"Setup failed: {str(e)}")
            self.ws = None

    def receive(self, frame: tuple[int, np.ndarray]) -> None:
        """Receives audio/video data, encodes it, and sends it to the Gemini API."""
        try:
            if not self.ws:
                self._initialize_websocket()

            sample_rate, array = frame
            message = {"realtimeInput": {"mediaChunks": []}}

            if sample_rate > 0 and array is not None:
                array = array.squeeze()
                audio_data = self.audio_processor.encode_audio(array, self.output_sample_rate)
                message["realtimeInput"]["mediaChunks"].append({
                    "mimeType": f"audio/pcm;rate={self.output_sample_rate}",
                    "data": audio_data["realtimeInput"]["mediaChunks"][0]["data"],
                })

            if message["realtimeInput"]["mediaChunks"]:
                self.ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            if self.ws:
                self.ws.close()
            self.ws = None

    def _process_server_content(self, content):
        """Processes audio output data from the WebSocket response."""
        for part in content.get("parts", []):
            data = part.get("inlineData", {}).get("data", "")
            if data:
                audio_array = self.audio_processor.process_audio_response(data)
                if self.all_output_data is None:
                    self.all_output_data = audio_array
                else:
                    self.all_output_data = np.concatenate((self.all_output_data, audio_array))

                while self.all_output_data.shape[-1] >= self.output_frame_size:
                    yield (self.output_sample_rate, self.all_output_data[: self.output_frame_size].reshape(1, -1))
                    self.all_output_data = self.all_output_data[self.output_frame_size :]

    def generator(self):
        """Generates audio output from the WebSocket stream."""
        while True:
            if not self.ws:
                print("WebSocket not connected")
                yield None
                continue

            try:
                message = self.ws.recv(timeout=30)
                msg = json.loads(message)
                if "serverContent" in msg:
                    content = msg["serverContent"].get("modelTurn", {})
                    yield from self._process_server_content(content)
            except TimeoutError:
                print("Timeout waiting for server response")
                yield None
            except Exception as e:
                yield None

    def emit(self) -> tuple[int, np.ndarray] | None:
        """Emits the next audio chunk from the generator."""
        if not self.ws:
            return None
        if not hasattr(self, "_generator"):
            self._generator = self.generator()
        try:
            return next(self._generator)
        except StopIteration:
            self.reset()
            return None

    def reset(self) -> None:
        """Resets the generator and output data."""
        if hasattr(self, "_generator"):
            delattr(self, "_generator")
        self.all_output_data = None

    def shutdown(self) -> None:
        """Closes the WebSocket connection."""
        if self.ws:
            self.ws.close()

    def check_connection(self):
        """Checks if the WebSocket connection is active."""
        try:
            if not self.ws or self.ws.closed:
                self._initialize_websocket()
            return True
        except Exception as e:
            print(f"Connection check failed: {str(e)}")
            return False

# Main Gradio Interface
def registry(
        name: str,
        token: str | None = None,
        **kwargs
):
    """Sets up and returns the Gradio interface."""
    api_key = token or os.environ.get(KEY_NAME)
    if not api_key:
        raise ValueError(f"{KEY_NAME} environment variable is not set.")

    interface = gr.Blocks()
    with interface:
        with gr.Tabs():
            with gr.TabItem("Voice Chat"):
                gr.HTML(
                    """
                    <div style='text-align: left'>
                        <h1>Gemini API Voice Chat</h1>
                    </div>
                    """
                )
                gemini_handler = GeminiHandler()
                with gr.Row():
                    audio = WebRTC(label="Voice Chat", modality="audio", mode="send-receive")

                audio.stream(
                    gemini_handler,
                    inputs=[audio],
                    outputs=[audio],
                    time_limit=600,
                    concurrency_limit=10
                )
    return interface

# Launch the Gradio interface
gr.load(
    name='gemini-2.0-flash-exp',
    src=registry,
).launch()
