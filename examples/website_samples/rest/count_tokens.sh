set -eu 

SCRIPT_DIR=$(dirname "$0")
MEDIA_DIR=$(realpath ${SCRIPT_DIR}/../../third_party)

TEXT_PATH=${MEDIA_DIR}/poem.txt
A11_PATH=${MEDIA_DIR}/a11.txt
IMG_PATH=${MEDIA_DIR}/organ.jpg
AUDIO_PATH=${MEDIA_DIR}/sample.mp3
VIDEO_PATH=${MEDIA_DIR}/Big_Buck_Bunny.mp4

BASE_URL="https://generativelanguage.googleapis.com"

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

echo "[START tokens_context_window]"
# [START tokens_context_window]
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro?key=$GOOGLE_API_KEY > model.json
jq .inputTokenLimit model.json
jq .outputTokenLimit model.json
# [END tokens_context_window]

echo "[START tokens_text_only]"
# [START tokens_text_only]
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[{
          "text": "The quick brown fox jumps over the lazy dog."
          }],
        }],
      }'
# [END tokens_text_only]

echo "[START tokens_chat]"
# [START tokens_chat]
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [
        {"role": "user",
        "parts": [{"text": "Hi, my name is Bob."}],
        },
        {"role": "model",
         "parts":[{"text": "Hi Bob"}],
        },
      ],
      }'
# [END tokens_chat]

echo "[START tokens_multimodal_image_inline]"
# [START tokens_multimodal_image_inline]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
            {"text": "Tell me about this instrument"},
            {
              "inline_data": {
                "mime_type":"image/jpeg",
                "data": "'$(base64 $B64FLAGS $IMG_PATH)'"
              }
            }
        ]
        }]
       }' 2> /dev/null
# [END tokens_multimodal_image_inline]

echo "[START tokens_multimodal_image_file_api]"
# [START tokens_multimodal_image_file_api]
MIME_TYPE=$(file -b --mime-type "${IMG_PATH}")
NUM_BYTES=$(wc -c < "${IMG_PATH}")
DISPLAY_NAME=TEXT

tmp_header_file=upload-header.tmp

# Initial resumable request defining metadata.
# The upload url is in the response headers dump them to a file.
curl "${BASE_URL}/upload/v1beta/files?key=${GOOGLE_API_KEY}" \
  -D upload-header.tmp \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
  -H "Content-Type: application/json" \
  -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
rm "${tmp_header_file}"

# Upload the actual bytes.
curl "${upload_url}" \
  -H "Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Offset: 0" \
  -H "X-Goog-Upload-Command: upload, finalize" \
  --data-binary "@${IMG_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Can you tell me about the instruments in this photo?"},
          {"file_data":
            {"mime_type": "image/jpeg", 
            "file_uri": '$file_uri'}
          }]
        }]
       }' 
# [END tokens_multimodal_image_file_api]

echo "# [START tokens_multimodal_video_audio_file_api]"
# [START tokens_multimodal_video_audio_file_api]

MIME_TYPE=$(file -b --mime-type "${VIDEO_PATH}")
NUM_BYTES=$(wc -c < "${VIDEO_PATH}")
DISPLAY_NAME=VIDEO_PATH

# Initial resumable request defining metadata.
# The upload url is in the response headers dump them to a file.
curl "${BASE_URL}/upload/v1beta/files?key=${GOOGLE_API_KEY}" \
  -D upload-header.tmp \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
  -H "Content-Type: application/json" \
  -d "{'file': {'display_name': '${DISPLAY_NAME}'}}" 2> /dev/null

upload_url=$(grep -i "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
rm "${tmp_header_file}"

# Upload the actual bytes.
curl "${upload_url}" \
  -H "Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Offset: 0" \
  -H "X-Goog-Upload-Command: upload, finalize" \
  --data-binary "@${VIDEO_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)

state=$(jq ".file.state" file_info.json)

name=$(jq ".file.name" file_info.json)

while [[ "($state)" = *"PROCESSING"* ]];
do
  echo "Processing video..."
  sleep 5
  # Get the file of interest to check state
  curl https://generativelanguage.googleapis.com/v1beta/files/$name > file_info.json
  state=$(jq ".file.state" file_info.json)
done

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:countTokens?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Describe this video clip"},
          {"file_data":{"mime_type": "video/mp4", "file_uri": '$file_uri'}}]
        }]
       }'
# [END tokens_multimodal_video_audio_file_api]

echo "[START tokens_cached_content]"
# [START tokens_cached_content]
echo '{
  "model": "models/gemini-1.5-flash-001",
  "contents":[
    {
      "parts":[
        {
          "inline_data": {
            "mime_type":"text/plain",
            "data": "'$(base64 $B64FLAGS $A11_PATH)'"
          }
        }
      ],
    "role": "user"
    }
  ],
  "systemInstruction": {
    "parts": [
      {
        "text": "You are an expert at analyzing transcripts."
      }
    ]
  },
  "ttl": "300s"
}' > request.json

curl -X POST "https://generativelanguage.googleapis.com/v1beta/cachedContents?key=$GOOGLE_API_KEY" \
 -H 'Content-Type: application/json' \
 -d @request.json \
 > cache.json

jq .usageMetadata.totalTokenCount cache.json
# [END tokens_cached_content]

echo "[START tokens_system_instruction]"
# [START tokens_system_instruction]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{ "system_instruction": {
    "parts":
      { "text": "You are a cat. Your name is Neko."}},
    "contents": {
      "parts": {
        "text": "Hello there"}}}' > system_instructions.json

jq .usageMetadata.totalTokenCount system_instructions.json
# [END tokens_system_instruction]

echo "[START tokens_tools]"
# [START tokens_tools]
cat > tools.json << EOF
{
  "function_declarations": [
    {
      "name": "enable_lights",
      "description": "Turn on the lighting system.",
      "parameters": { "type": "object" }
    },
    {
      "name": "set_light_color",
      "description": "Set the light color. Lights must be enabled for this to work.",
      "parameters": {
        "type": "object",
        "properties": {
          "rgb_hex": {
            "type": "string",
            "description": "The light color as a 6-digit hex string, e.g. ff0000 for red."
          }
        },
        "required": [
          "rgb_hex"
        ]
      }
    },
    {
      "name": "stop_lights",
      "description": "Turn off the lighting system.",
      "parameters": { "type": "object" }
    }
  ]
} 
EOF

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=$GOOGLE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '
  {
    "system_instruction": {
      "parts": {
        "text": "You are a helpful lighting system bot. You can turn lights on and off, and you can set the color. Do not perform any other tasks."
      }
    },
    "tools": ['$(source "$tools")'],

    "tool_config": {
      "function_calling_config": {"mode": "none"}
    },

    "contents": {
      "role": "user",
      "parts": {
        "text": "What can you do?"
      }
    }
  }
' > tools_output.json

jq .usageMetadata.totalTokenCount tools_output.json
# [END tokens_tools]