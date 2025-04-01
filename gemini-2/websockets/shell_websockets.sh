#!/bin/bash
#set -ex

# This script shows you how to use `websocat` to interact with the Gemini 2.0
# Multimodal Live API.

# You need to set $GOOGLE_API_KEY
# And you'll need:
#  $ sudo apt install jq
#  $ wget https://github.com/vi/websocat/releases/download/v1.14.0/websocat.x86_64-unknown-linux-musl
#    (or relevant binary from https://github.com/vi/websocat/releases)

echo "HOST: ${HOST:=generativelanguage.googleapis.com}"
echo "MODEL: ${MODEL:=gemini-2.0-flash-exp}"
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
websocat -n wss://${HOST}/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent?key=${API_KEY} <gemini_input >gemini_output &
socket_pid=$!
echo "Model connected."

# Issue setup handshake.
echo '{"setup": {"model": "models/'${MODEL}'", "generation_config": {"response_modalities":["TEXT"]}}}' |tee >(jq) >gemini_input

# Generate something.
echo '{"client_content": { "turn_complete": true, "turns": [{"role": "user", "parts": [{"text": "what is 10 + 10?"}]}]}}' |tee >(jq) >gemini_input

sleep 5
rm gemini_{in,out}put
kill -9 $output_pid $socket_pid 2>/dev/null || true
