# audio_loop.py

"""
AudioLoop module for real-time audio, video, and text streaming.

This module contains the `AudioLoop` class, which facilitates bi-directional communication
with Google's Gemini AI model using audio, video, and textual inputs. The class uses asyncio
to manage asynchronous tasks and supports real-time audio playback and video capture.

Dependencies:
    - Python 3.11+
    - asyncio
    - pyaudio
    - opencv (cv2)
    - mss
    - PIL (Pillow)
    - google.genai

Logging:
    - Logs are configured using `setup_logging()` and written to a file in the `logs` directory.

This implementation of AudioLoop() is meant to be imported into other porgrams that manage the GUI
"""

import logging
import os
from datetime import datetime

def setup_logging():
    """
    Setup logging configuration with both file and console output.
    """
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(logs_dir, f"gemini_cv_{timestamp}.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            # Uncomment the next line to also log to the console:
            # logging.StreamHandler(sys.stdout)
        ],
        force=True  # Python 3.8+ to override any existing configuration
    )

    logger = logging.getLogger(__name__)
    print(f"Logging to file: {log_filename}")
    logger.info(f"Logging started - Log file: {log_filename}")
    logger.info("Root logger configured with a FileHandler using UTF-8 encoding.")
    return logger

logger = setup_logging()
logger.info("audio_loop module loaded.")


import asyncio
import base64
import io
import traceback
import cv2
import pyaudio
import PIL.Image
import mss

from dotenv import load_dotenv
from google import genai

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

class AudioLoop:
    """
    Manages real-time audio, video, and text interactions with an AI model.

    The `AudioLoop` class provides asynchronous methods for:
    - Capturing audio and video input.
    - Sending and receiving real-time data streams to/from the AI model.
    - Playing back audio responses and displaying text outputs.

    Attributes:
        user_input_queue (asyncio.Queue): A queue for receiving user messages.
        display_text_callback (callable): Callback function to handle text outputs.
        pya (pyaudio.PyAudio): PyAudio instance for audio handling.
        audio_in_queue (asyncio.Queue): Queue for incoming audio responses.
        out_queue (asyncio.Queue): Queue for outgoing data streams.
        audio_stream (pyaudio.Stream): PyAudio stream for microphone input.
        session (AsyncSession): Live session object for communication with the AI model.
    """
        
    def __init__(self, user_input_queue: asyncio.Queue, display_text_callback=None):
        """
        Initialize the AudioLoop instance.

        Args:
            user_input_queue (asyncio.Queue): A queue from which user messages can be retrieved asynchronously.
            display_text_callback (callable, optional): A callback function to display text responses.
                This function should accept a single string argument. If not provided,
                text output will be ignored. Defaults to a no-op function.
        """
        logger.debug("Initializing AudioLoop...")
        self.audio_in_queue = None
        self.out_queue = None
        self.audio_stream = None
        self.session = None

        self.user_input_queue = user_input_queue
        self.display_text_callback = display_text_callback if display_text_callback else (lambda x: None)

        self.pya = pyaudio.PyAudio()
        logger.debug("AudioLoop initialized.")

    async def send_text(self):
        """
        Asynchronously sends text messages from the user input queue to the AI model.

        Continuously retrieves messages from `user_input_queue`, sends them to the
        AI model, and exits gracefully when 'q' is received.
        """
        logger.debug("send_text task started.")
        while True:
            text = await self.user_input_queue.get()
            logger.debug(f"Received user text: {text}")
            if text.lower() == "q":
                logger.info("User requested exit by sending 'q'.")
                break
            await self.session.send(text or ".", end_of_turn=True)
            logger.debug("Text sent to session.")

    def _get_frame(self, cap):
        """
        Captures a single frame from the given video capture device and converts it to a JPEG.

        Args:
            cap (cv2.VideoCapture): OpenCV video capture object.

        Returns:
            dict: A dictionary containing MIME type and Base64-encoded JPEG data.
        """
        ret, frame = cap.read()
        if not ret:
            logger.warning("Failed to read frame from camera.")
            return None
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)
        original_size = img.size
        img.thumbnail([1024, 1024])
        logger.debug(f"Captured frame resized from {original_size} to {img.size}")

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        logger.debug(f"Frame converted to JPEG of size {len(image_bytes)} bytes.")
        return {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        """
        Captures video frames from the default camera and queues them for sending.

        Continuously captures frames using OpenCV, processes them into JPEG format, and
        adds them to the output queue until the task is cancelled or the camera is closed.
        """
        logger.info("Attempting to open camera...")
        cap = await asyncio.to_thread(cv2.VideoCapture, 0)
        if not cap.isOpened():
            logger.error("Failed to open camera.")
            return
        logger.info("Camera opened successfully.")

        frame_count = 0
        try:
            while True:
                frame = await asyncio.to_thread(self._get_frame, cap)
                if frame is None:
                    logger.warning("No more frames retrieved from camera.")
                    break
                frame_count += 1
                if frame_count % 10 == 0:
                    logger.debug(f"Captured frame {frame_count}")

                await asyncio.sleep(1.0)
                await self.out_queue.put(frame)
                logger.debug(f"Frame {frame_count} queued for sending.")
        except asyncio.CancelledError:
            logger.info("get_frames task cancelled.")
        finally:
            logger.info("Releasing camera...")
            cap.release()

    def _get_screen_frame(self):
        """
        Captures a screenshot of the primary display and converts it to a JPEG.

        Returns:
            dict: A dictionary containing MIME type and Base64-encoded JPEG data.
        """
        # Although in most cases mss cleans up after itself, it’s still cleaner to use a with: block.
        # This ensures any underlying resources used by MSS are released promptly after each frame capture.
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            i = sct.grab(monitor)

            mime_type = "image/jpeg"
            image_bytes = mss.tools.to_png(i.rgb, i.size)
            img = PIL.Image.open(io.BytesIO(image_bytes))

            original_size = img.size
            img.thumbnail([1024, 1024])
            logger.debug(f"Captured screen resized from {original_size} to {img.size}")

            image_io = io.BytesIO()
            img.save(image_io, format="jpeg")
            image_io.seek(0)

            image_bytes = image_io.read()
            logger.debug(f"Screen frame converted to JPEG of size {len(image_bytes)} bytes.")
            return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):
        """
        Captures screen frames and queues them for sending.

        Continuously captures screenshots of the primary monitor and queues them
        until the task is cancelled.
        """
        logger.info("Starting screen capture...")
        try:
            frame_count = 0
            while True:
                frame = await asyncio.to_thread(self._get_screen_frame)
                if frame is None:
                    logger.warning("No screen frame retrieved.")
                    break
                frame_count += 1
                if frame_count % 10 == 0:
                    logger.debug(f"Captured screen frame {frame_count}")
                await asyncio.sleep(1.0)
                await self.out_queue.put(frame)
                logger.debug(f"Screen frame {frame_count} queued for sending.")
        except asyncio.CancelledError:
            logger.info("get_screen task cancelled.")

    async def send_realtime(self):
        """
        Sends real-time data (audio, video, or screen) from the output queue to the AI model.

        Continuously retrieves messages from `out_queue` and sends them to the active session.
        """
        logger.info("send_realtime task started.")
        while True:
            msg = await self.out_queue.get()
            logger.debug("Sending realtime data to session.")
            await self.session.send(msg)
            logger.debug("Data sent.")

    async def listen_audio(self):
        """
        Captures audio from the default microphone and queues it for sending.

        Opens a PyAudio stream to capture microphone input, processes audio chunks,
        and adds them to the output queue.
        """
        logger.info("Starting audio input listening...")
        mic_info = self.pya.get_default_input_device_info()
        logger.debug(f"Default microphone: {mic_info['name']} (index {mic_info['index']})")
        self.audio_stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        logger.info("Microphone audio stream opened successfully.")
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})
            logger.debug("Audio chunk queued for sending.")

    async def receive_audio(self):
        """
        Receives audio and text responses from the AI model.

        Continuously listens for incoming responses from the AI model, processes
        audio and text, and updates the respective queues or callbacks.
        """
        logger.info("Starting receive_audio task...")
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    logger.debug("Received audio data from session.")
                    continue
                if text := response.text:
                    logger.debug(f"Received text response: {text.strip()}")
                    self.display_text_callback(text)

            # On turn_complete, empty out the audio queue
            while not self.audio_in_queue.empty():
                discarded = self.audio_in_queue.get_nowait()
                logger.debug("Discarding old audio data on turn complete.")

    async def play_audio(self):
        """
        Plays back received audio responses from the AI model.

        Continuously retrieves audio data from `audio_in_queue` and plays it using PyAudio.
        """
        logger.info("Starting audio playback...")
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        logger.info("Audio playback stream opened successfully.")
        try:
            while True:
                bytestream = await self.audio_in_queue.get()
                await asyncio.to_thread(stream.write, bytestream)
                logger.debug("Played received audio chunk.")
        except asyncio.CancelledError:
            logger.info("play_audio task cancelled.")
        finally:
            logger.info("Closing playback audio stream...")
            stream.close()

    async def run(self, model, config, mode, client):
        """
        Runs the main loop for managing AI interactions.

        Establishes a live session with the AI model and coordinates various tasks
        for audio, video, and text interactions.

        Args:
            model (str): AI model identifier.
            config (dict): Configuration for the AI model session.
            mode (str): Input mode ('text', 'camera', or 'screen').
            client (genai.Client): GenAI client instance.

        Raises:
            asyncio.CancelledError: If the loop is cancelled (e.g., user exits).
        """
        logger.info("Starting AudioLoop.run()")
        try:
            async with (
                client.aio.live.connect(model=model, config=config) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                logger.info("Session connected successfully.")

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text(), name="send_text")
                tg.create_task(self.send_realtime(), name="send_realtime")
                tg.create_task(self.listen_audio(), name="listen_audio")

                if mode == "text" or mode == None:
                    # Do nothing if mode is "text" or None
                    pass
                else:
                    if mode == "camera":
                        # Create an asynchronous task to get frames from the camera
                        tg.create_task(self.get_frames(), name="get_frames")
                    elif mode == "screen":
                        # Create an asynchronous task to get the screen content
                        tg.create_task(self.get_screen(), name="get_screen")

                tg.create_task(self.receive_audio(), name="receive_audio")
                tg.create_task(self.play_audio(), name="play_audio")

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            logger.info("AudioLoop.run() cancelled - likely user requested exit.")
        except ExceptionGroup as EG:
            logger.error("ExceptionGroup encountered in run:")
            traceback.print_exception(EG)
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            if self.audio_stream:
                self.audio_stream.close()
                logger.info("Audio stream closed.")
            # best practice to close pya
            self.pya.terminate()
            logger.info("PyAudio terminated.")

def main():
    """
    Main function to run the AudioLoop application as a CLI.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Run the AudioLoop application as a CLI.")
    parser.add_argument(
        "--mode",
        type=str,
        default="text", # no streaming by default
        help="Source of video frames to stream",
        choices=["text", "camera", "screen"]
    )
    args = parser.parse_args()

    MODEL = "models/gemini-2.0-flash-exp"
    client = genai.Client(http_options={"api_version": "v1alpha"})

    CONFIG_1 = {"generation_config": {"response_modalities": ["TEXT"]}}

    voices = ["Puck", "Charon", "Kore", "Fenrir", "Aoede"]
    CONFIG_2 = {"generation_config": {
                    "response_modalities": ["AUDIO"],
                    "speech_config": voices[2]  # Set voice
                    }
                }

    # select CONFIG_1 or CONFIG_2
    CONFIG = CONFIG_2

    user_input_queue = asyncio.Queue()
    display_callback = print

    async def read_user_input():
        """Async function to continuously read user input from console and queue it."""
        loop = asyncio.get_running_loop()
        while True:
            text = await asyncio.to_thread(input, "message > ")
            if text.lower() == "quit":
                text = "q"
            await user_input_queue.put(text)

    async def run_loop():
        loop_instance = AudioLoop(user_input_queue=user_input_queue, display_text_callback=display_callback)
        user_input_task = asyncio.create_task(read_user_input())
        try:
            await loop_instance.run(MODEL, CONFIG, args.mode, client)
        finally:
            user_input_task.cancel()
            logger.info("Main run_loop ended.")

    logger.info("Starting main CLI mode...")
    asyncio.run(run_loop())

if __name__ == "__main__":
    load_dotenv()
    main()
