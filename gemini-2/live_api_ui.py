"""
## Setup

This script launches a pure-python web-based UI for the Gen AI SDK Voice Chat.

To install the dependencies for this script, run:

``` 
pip install gradio-webrtc>=0.0.27 google-genai
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

import gradio as gr
import numpy as np
from google import genai
from gradio_webrtc import (
    AsyncStreamHandler,
    WebRTC,
    async_aggregate_bytes_to_16bit,
)

try:
    from dotenv import load_dotenv
    load_dotenv()
except (ImportError, ModuleNotFoundError):
    pass

class GeminiHandler(AsyncStreamHandler):
    def __init__(
        self, expected_layout="mono", output_sample_rate=24000, output_frame_size=480
    ) -> None:
        super().__init__(
            expected_layout,
            output_sample_rate,
            output_frame_size,
            input_sample_rate=16000,
        )
        self.client: genai.Client | None = None
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()
        self.quit = asyncio.Event()

    def copy(self) -> "GeminiHandler":
        return GeminiHandler(
            expected_layout=self.expected_layout,
            output_sample_rate=self.output_sample_rate,
            output_frame_size=self.output_frame_size,
        )

    async def stream(self):
        while not self.quit.is_set():
            audio = await self.input_queue.get()
            yield audio

    async def connect(self, api_key: str):
        client = genai.Client(api_key=api_key, http_options={"api_version": "v1alpha"})
        config = {"response_modalities": ["AUDIO"]}
        async with client.aio.live.connect(
            model="models/gemini-2.0-flash-exp", config=config
        ) as session:
            async for audio in session.start_stream(
                stream=self.stream(), mime_type="audio/pcm"
            ):
                if audio.data:
                    yield audio.data

    async def receive(self, frame: tuple[int, np.ndarray]) -> None:
        _, array = frame
        array = array.squeeze()
        audio_message = base64.b64encode(array.tobytes()).decode("UTF-8")
        self.input_queue.put_nowait(audio_message)

    async def generator(self):
        async for audio_response in async_aggregate_bytes_to_16bit(
            self.connect(self.latest_args[1])
        ):
            self.output_queue.put_nowait(audio_response)

    async def emit(self):
        if not self.args_set.is_set():
            await self.wait_for_args()
            asyncio.create_task(self.generator())

        array = await self.output_queue.get()
        return (self.output_sample_rate, array)

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
        webrtc = WebRTC(
            label="Audio",
            modality="audio",
            mode="send-receive",
            pulse_color="rgb(35, 157, 225)",
            icon_button_color="rgb(35, 157, 225)",
            icon="https://www.gstatic.com/lamda/images/gemini_favicon_f069958c85030456e93de685481c559f160ea06b.png",
        )

    webrtc.stream(
        GeminiHandler(),
        inputs=[webrtc, api_key],
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
