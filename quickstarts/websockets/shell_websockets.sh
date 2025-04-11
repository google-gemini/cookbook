#!/bin/bash
#set -ex

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

# This script shows you how to use `websocat` to interact with the Gemini 2.0
# Multimodal Live API.

# You need to set $GOOGLE_API_KEY
# And you'll need:
#  $ sudo apt install jq
#  $ wget https://github.com/vi/websocat/releases/download/v1.14.0/websocat.x86_64-unknown-linux-musl
#    (or relevant binary from https://github.com/vi/websocat/releases)

echo "HOST: ${HOST:=generativelanguage.googleapis.com}"
echo "MODEL: ${MODEL:=gemini-2.0-flash-live-001}"
API_KEY=${GOOGLE_API_KEY:?Please set \$GOOGLE_API_KEY}

echo "Starting..."

# Define some pipes so we can separate model input and output.
mkfifo gemini_{in,out}put
echo "Pipes laid..."

# Process model output in the background.
# Uncomment this to do explicit line-by-line processing:
#while IFS= read -r line; do
#  jq <<<"$line"
#done < gemini_output &

# Or use this to `jq` everything:
jq --stream 'fromstream(0|truncate_stream(inputs))' <gemini_output &

output_pid=$!
echo "Output processing..."

# Launch the model connection and wire it up to the pipes.
websocat -n wss://${HOST}/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=${API_KEY} <gemini_input >gemini_output &
socket_pid=$!
echo "Model connected."

# Issue setup handshake.
echo '{"setup": {"model": "models/'${MODEL}'", "response_modalities":["TEXT"]}}' |tee >(jq) >gemini_input

# Generate something.
echo '{"client_content": { "turn_complete": true, "turns": [{"role": "user", "parts": [{"text": "what is 10 + 10?"}]}]}}' |tee >(jq) >gemini_input

sleep 5
rm gemini_{in,out}put
kill -9 $output_pid $socket_pid 2>/dev/null || true
