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
pip install google-genai==2.8.0 pyaudio yt-dlp
```

This script also requires `ffmpeg` to be installed on your system. For example, on macOS:

```
brew install ffmpeg
```

Before running this script, ensure the `GEMINI_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

## Run

To run the script:

```
python Get_started_LiveTranslate.py --url "https://www.youtube.com/watch?v=QhdEJFFaig0" --target es
```
"""

import array
import asyncio
import argparse
import pyaudio
import yt_dlp
from google import genai
from google.genai import types

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1600  # samples per chunk (100ms at 16kHz)

def adjust_volume(pcm_data: bytes, volume: float) -> bytes:
    """Scales raw PCM 16-bit signed samples by the volume factor."""
    if volume >= 1.0:
        return pcm_data
    if volume <= 0.0:
        return b'\x00' * len(pcm_data)
    
    samples = array.array('h', pcm_data)
    for i in range(len(samples)):
        samples[i] = int(samples[i] * volume)
    return samples.tobytes()

async def stream_youtube_audio(url: str, audio_queue: asyncio.Queue, original_playback_queue: asyncio.Queue = None, volume: float = 0.08):
    """Downloads and demuxes YouTube audio, putting raw PCM bytes into the audio_queue."""
    print(f"\n[Info] Extracting audio URL from YouTube video: {url}")
    try:
        # Run yt_dlp in a thread to keep the event loop responsive
        loop = asyncio.get_running_loop()
        
        def extract():
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info['url']

        audio_url = await loop.run_in_executor(None, extract)
    except Exception as e:
        print(f"[Error] Failed to extract YouTube audio: {e}")
        return

    print("[Info] Starting audio stream via ffmpeg...")
    # Spawn ffmpeg to decode stream to raw PCM 16kHz mono 16-bit
    process = await asyncio.create_subprocess_exec(
        'ffmpeg',
        '-i', audio_url,
        '-f', 's16le',
        '-acodec', 'pcm_s16le',
        '-ar', str(SEND_SAMPLE_RATE),
        '-ac', str(CHANNELS),
        '-',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )

    # 1600 samples * 2 bytes/sample (16-bit) = 3200 bytes
    chunk_size_bytes = CHUNK_SIZE * 2
    bytes_per_second = SEND_SAMPLE_RATE * 2
    start_time = asyncio.get_event_loop().time()
    bytes_sent = 0

    try:
        while True:
            data = await process.stdout.read(chunk_size_bytes)
            if not data:
                break
            
            await audio_queue.put(data)
            
            # Put quieted audio into original playback queue
            if original_playback_queue is not None and volume > 0.0:
                quiet_data = adjust_volume(data, volume)
                await original_playback_queue.put(quiet_data)
                
            bytes_sent += len(data)
            
            # Rate limit to exactly 1.0x real-time playback speed
            expected_elapsed = bytes_sent / bytes_per_second
            actual_elapsed = asyncio.get_event_loop().time() - start_time
            sleep_time = expected_elapsed - actual_elapsed
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    except asyncio.CancelledError:
        pass
    finally:
        if process.returncode is None:
            try:
                process.terminate()
                await process.wait()
            except Exception:
                pass
        print("\n[Info] YouTube audio stream finished.")

async def send_realtime(session, audio_queue: asyncio.Queue):
    """Sends audio from the input queue to the GenAI session."""
    try:
        while True:
            chunk = await audio_queue.get()
            await session.send_realtime_input(
                audio=types.Blob(
                    data=chunk,
                    mime_type=f"audio/pcm;rate={SEND_SAMPLE_RATE}"
                )
            )
            audio_queue.task_done()
    except asyncio.CancelledError:
        pass

async def receive_responses(session, audio_queue_output: asyncio.Queue):
    """Receives responses from Gemini, plays audio and prints transcripts."""
    try:
        async for response in session.receive():
            server_content = response.server_content
            if server_content:
                # Handle model audio turn data
                if server_content.model_turn:
                    for part in server_content.model_turn.parts:
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            audio_queue_output.put_nowait(part.inline_data.data)
                
                # Print input (source) transcript
                if server_content.input_transcription and server_content.input_transcription.text:
                    lang = f" ({server_content.input_transcription.language_code})" if server_content.input_transcription.language_code else ""
                    print(f"\n[Source{lang}] {server_content.input_transcription.text}", flush=True)
                
                # Print output (translated) transcript
                if server_content.output_transcription and server_content.output_transcription.text:
                    lang = f" ({server_content.output_transcription.language_code})" if server_content.output_transcription.language_code else ""
                    print(f"[Translation{lang}] {server_content.output_transcription.text}", flush=True)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"\n[Error] Receiving loop encountered error: {e}")

async def play_audio(audio_queue_output: asyncio.Queue):
    """Plays translated audio from the output queue."""
    pya = pyaudio.PyAudio()
    try:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await audio_queue_output.get()
            await asyncio.to_thread(stream.write, bytestream)
            audio_queue_output.task_done()
    except asyncio.CancelledError:
        pass
    finally:
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        pya.terminate()

async def play_original_audio(original_playback_queue: asyncio.Queue):
    """Plays quieted original background audio from the queue."""
    pya = pyaudio.PyAudio()
    try:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,  # 16000Hz (original audio rate)
            output=True,
        )
        while True:
            bytestream = await original_playback_queue.get()
            await asyncio.to_thread(stream.write, bytestream)
            original_playback_queue.task_done()
    except asyncio.CancelledError:
        pass
    finally:
        try:
            stream.stop_stream()
            stream.close()
        except Exception:
            pass
        pya.terminate()

async def run(url: str, target_lang: str, original_volume: float = 0.08):
    # Initialize Google GenAI Client
    client = genai.Client()
    
    # Configure live connection with translation settings
    config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        translation_config=types.TranslationConfig(
            echo_target_language=True,
            target_language_code=target_lang,
        ),
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    audio_queue_input = asyncio.Queue(maxsize=10)
    audio_queue_output = asyncio.Queue()
    original_playback_queue = asyncio.Queue()

    model = "gemini-3.5-live-translate-preview"
    print(f"[Info] Connecting to Gemini Live ({model})...")
    
    try:
        async with client.aio.live.connect(model=model, config=config) as session:
            print("[Info] Connected successfully. Ready to stream!")
            async with asyncio.TaskGroup() as tg:
                stream_task = tg.create_task(
                    stream_youtube_audio(url, audio_queue_input, original_playback_queue, original_volume)
                )
                send_task = tg.create_task(send_realtime(session, audio_queue_input))
                receive_task = tg.create_task(receive_responses(session, audio_queue_output))
                play_task = tg.create_task(play_audio(audio_queue_output))
                play_original_task = tg.create_task(play_original_audio(original_playback_queue))
                
                # Wait for the YouTube stream to finish reading
                await stream_task
                
                # Wait for all buffered input chunks to be sent to Gemini
                await audio_queue_input.join()
                send_task.cancel()
                
                # Wait for original playback to finish
                await original_playback_queue.join()
                play_original_task.cancel()
                
                # Give Gemini a few seconds to finish translating and speaking the final chunks
                await asyncio.sleep(4.0)
                receive_task.cancel()
                play_task.cancel()
                
    except Exception as e:
        print(f"[Error] Live session error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream YouTube video audio to Gemini Live Translate CLI")
    parser.add_argument("--url", required=True, help="YouTube video URL")
    parser.add_argument("--target", default="es", help="Target translation language code (default: es)")
    parser.add_argument("--original-volume", type=float, default=0.08, help="Volume of original background audio (0.0 to 1.0, default: 0.08)")
    args = parser.parse_args()

    try:
        asyncio.run(run(args.url, args.target, args.original_volume))
    except KeyboardInterrupt:
        print("\n[Info] Interrupted by user. Exiting...")
