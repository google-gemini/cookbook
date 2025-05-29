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
OSC Test Client for Get_started_LyriaRealTime.py

This script sends a sequence of OSC messages to test the OSC server
functionality implemented in `Get_started_LyriaRealTime.py`.

Instructions:
1. Run `Get_started_LyriaRealTime.py` in one terminal.
   Ensure your GOOGLE_API_KEY is set and `python-osc` is installed.
2. Once the Lyria script is running and you see "OSC Server listening on...",
   run this `osc_test_client.py` script in another terminal.
3. Observe the console output of both scripts to verify commands are being
   sent by the client and received/processed by the server.
"""

from pythonosc import udp_client
import time

# OSC Server Configuration (must match Get_started_LyriaRealTime.py)
OSC_SERVER_IP = "127.0.0.1"
OSC_SERVER_PORT = 5005  # Default port in Get_started_LyriaRealTime.py

# Create OSC Client
client = udp_client.SimpleUDPClient(OSC_SERVER_IP, OSC_SERVER_PORT)

def send_osc_command(address, arguments=None, delay_after_send=2.0):
    """Helper function to send OSC messages and print feedback."""
    if arguments is not None:
        # SimpleUDPClient expects arguments as a list or tuple, even if it's a single value.
        # However, for single arguments, it's often more natural to pass them directly.
        # The send_message method handles single values vs lists appropriately.
        print(f"Sending OSC: {address} with argument(s): {arguments}")
        client.send_message(address, arguments)
    else:
        print(f"Sending OSC: {address}")
        client.send_message(address, None)
    
    if delay_after_send > 0:
        time.sleep(delay_after_send)

if __name__ == "__main__":
    print("Starting OSC Test Client...")
    print(f"Targeting OSC Server at {OSC_SERVER_IP}:{OSC_SERVER_PORT}")
    print("Ensure Get_started_LyriaRealTime.py is running and listening for OSC messages.")
    time.sleep(2) # Give user a moment to read

    try:
        # Initial prompt and play
        send_osc_command("/lyria/setPrompts", "Ambient Pad:1.0", delay_after_send=1)
        send_osc_command("/lyria/play", delay_after_send=5)

        # Change BPM
        send_osc_command("/lyria/bpm", 90, delay_after_send=5)

        # Change prompts
        send_osc_command("/lyria/setPrompts", "Synth Lead:0.7,Bass Guitar:0.9", delay_after_send=5)

        # Pause and resume
        send_osc_command("/lyria/pause", delay_after_send=3)
        send_osc_command("/lyria/play", delay_after_send=5) # Resume

        # Change scale
        send_osc_command("/lyria/scale", "C_MAJOR_A_MINOR", delay_after_send=5)
        
        # Test AUTO BPM
        send_osc_command("/lyria/bpm", "AUTO", delay_after_send=5)

        # Test AUTO Scale
        send_osc_command("/lyria/scale", "AUTO", delay_after_send=5)

        # Send another prompt to hear effect of AUTO settings
        send_osc_command("/lyria/setPrompts", "Ethereal Choir:1.0", delay_after_send=5)

        # Stop the music
        print("Test sequence complete. Sending /lyria/stop...")
        send_osc_command("/lyria/stop", delay_after_send=0) # No delay after stop

        print("OSC Test Client finished.")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the Lyria OSC server script (Get_started_LyriaRealTime.py) is running.")
        print("and that the IP address and port match.")

    print("Exiting OSC Test Client.")
