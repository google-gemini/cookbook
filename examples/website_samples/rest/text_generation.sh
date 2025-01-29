set -eu

SCRIPT_DIR=$(dirname "$0")
MEDIA_DIR=$(realpath ${SCRIPT_DIR}/../../third_party)

IMG_PATH=${MEDIA_DIR}/organ.jpg
IMG_PATH2=${MEDIA_DIR}/Cajun_instruments.jpg
AUDIO_PATH=${MEDIA_DIR}/sample.mp3
VIDEO_PATH=${MEDIA_DIR}/Big_Buck_Bunny.mp4
PDF_PATH=${MEDIA_DIR}/test.pdf

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

BASE_URL="https://generativelanguage.googleapis.com"

echo "[START text_gen_text_only_prompt]"
# [START text_gen_text_only_prompt]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[{"text": "Write a story about a magic backpack."}]
        }]
       }' 2> /dev/null
# [END text_gen_text_only_prompt]

echo "[START text_gen_text_only_prompt_streaming]"
# [START text_gen_text_only_prompt_streaming]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=${GOOGLE_API_KEY}" \
        -H 'Content-Type: application/json' \
        --no-buffer \
        -d '{ "contents":[{"parts":[{"text": "Write a story about a magic backpack."}]}]}'
# [END text_gen_text_only_prompt_streaming]

echo "[START text_gen_multimodal_one_image_prompt]"
# [START text_gen_multimodal_one_image_prompt]
# Use a temporary file to hold the base64 encoded image data
TEMP_B64=$(mktemp)
trap 'rm -f "$TEMP_B64"' EXIT
base64 $B64FLAGS $IMG_PATH > "$TEMP_B64"

# Use a temporary file to hold the JSON payload
TEMP_JSON=$(mktemp)
trap 'rm -f "$TEMP_JSON"' EXIT

cat > "$TEMP_JSON" << EOF
{
  "contents": [{
    "parts":[
      {"text": "Tell me about this instrument"},
      {
        "inline_data": {
          "mime_type":"image/jpeg",
          "data": "$(cat "$TEMP_B64")"
        }
      }
    ]
  }]
}
EOF

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d "@$TEMP_JSON" 2> /dev/null
# [END text_gen_multimodal_one_image_prompt]

echo "[START text_gen_multimodal_one_image_prompt_streaming]"
# [START text_gen_multimodal_one_image_prompt_streaming]
cat > "$TEMP_JSON" << EOF
{
  "contents": [{
    "parts":[
      {"text": "Tell me about this instrument"},
      {
        "inline_data": {
          "mime_type":"image/jpeg",
          "data": "$(cat "$TEMP_B64")"
        }
      }
    ]
  }]
}
EOF

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d "@$TEMP_JSON" 2> /dev/null
# [END text_gen_multimodal_one_image_prompt_streaming]

echo "[START text_gen_multimodal_two_image_prompt]"
# [START text_gen_multimodal_two_image_prompt]
# Base64 encode both images into temporary files
TEMP_B64_1=$(mktemp)
TEMP_B64_2=$(mktemp)
trap 'rm -f "$TEMP_B64_1" "$TEMP_B64_2"' EXIT
base64 $B64FLAGS "$IMG_PATH" > "$TEMP_B64_1"
base64 $B64FLAGS "$IMG_PATH2" > "$TEMP_B64_2"

# Create the JSON payload using the base64 data from both images
cat > "$TEMP_JSON" << EOF
{
    "contents": [{
        "parts":[
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": "$(cat "$TEMP_B64_1")"
                }
            },
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": "$(cat "$TEMP_B64_2")"
                }
            },
            {
                "text": "Generate a list of all the objects contained in both images."
            }
        ]
    }]
}
EOF

# Make the API request using the JSON file
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d "@$TEMP_JSON" 2> /dev/null > response.json

# Display the response
cat response.json
# [END text_gen_multimodal_two_image_prompt]

echo "[START text_gen_multimodal_one_image_bounding_box_prompt]"
# [START text_gen_multimodal_one_image_bounding_box_prompt]
# Re-use TEMP_B64_2 (from the previous two-image prompt) and TEMP_JSON

# Create the JSON payload for bounding box detection
cat > "$TEMP_JSON" << EOF
{
    "contents": [{
        "parts":[
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": "$(cat "$TEMP_B64_2")"
                }
            },
            {
                "text": "Generate bounding boxes for each of the objects in this image in [y_min, x_min, y_max, x_max] format."
            }
        ]
    }]
}
EOF

# Make the API request using the JSON file
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d "@$TEMP_JSON" 2> /dev/null > response.json

cat response.json
# [END text_gen_multimodal_one_image_bounding_box_prompt]

echo "[START text_gen_multimodal_audio]"
# [START text_gen_multimodal_audio]
# Use File API to upload audio data to API request.
MIME_TYPE=$(file -b --mime-type "${AUDIO_PATH}")
NUM_BYTES=$(wc -c < "${AUDIO_PATH}")
DISPLAY_NAME=AUDIO

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
  --data-binary "@${AUDIO_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Please describe this file."},
          {"file_data":{"mime_type": "audio/mpeg", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo

jq ".candidates[].content.parts[].text" response.json
# [END text_gen_multimodal_audio]

echo "[START text_gen_multimodal_audio_streaming]"
# [START text_gen_multimodal_audio_streaming]
# Use File API to upload audio data to API request.
MIME_TYPE=$(file -b --mime-type "${AUDIO_PATH}")
NUM_BYTES=$(wc -c < "${AUDIO_PATH}")
DISPLAY_NAME=AUDIO

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
  --data-binary "@${AUDIO_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Please describe this file."},
          {"file_data":{"mime_type": "audio/mpeg", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo
# [END text_gen_multimodal_audio_streaming]

echo "[START text_gen_multimodal_video_prompt]"
# [START text_gen_multimodal_video_prompt]
# Use File API to upload audio data to API request.
MIME_TYPE=$(file -b --mime-type "${VIDEO_PATH}")
NUM_BYTES=$(wc -c < "${VIDEO_PATH}")
DISPLAY_NAME=VIDEO

# Initial resumable request defining metadata.
# The upload url is in the response headers dump them to a file.
curl "${BASE_URL}/upload/v1beta/files?key=${GOOGLE_API_KEY}" \
  -D "${tmp_header_file}" \
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
echo file_uri=$file_uri

state=$(jq ".file.state" file_info.json)
echo state=$state

name=$(jq ".file.name" file_info.json)
echo name=$name

while [[ "($state)" = *"PROCESSING"* ]];
do
  echo "Processing video..."
  sleep 5
  # Get the file of interest to check state
  curl https://generativelanguage.googleapis.com/v1beta/files/$name > file_info.json
  state=$(jq ".file.state" file_info.json)
done

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Transcribe the audio from this video, giving timestamps for salient events in the video. Also provide visual descriptions."},
          {"file_data":{"mime_type": "video/mp4", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo

jq ".candidates[].content.parts[].text" response.json
# [END text_gen_multimodal_video_prompt]

echo "[START text_gen_multimodal_video_prompt_streaming]"
# [START text_gen_multimodal_video_prompt_streaming]
# Use File API to upload audio data to API request.
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
echo file_uri=$file_uri

state=$(jq ".file.state" file_info.json)
echo state=$state

while [[ "($state)" = *"PROCESSING"* ]];
do
  echo "Processing video..."
  sleep 5
  # Get the file of interest to check state
  curl https://generativelanguage.googleapis.com/v1beta/files/$name > file_info.json
  state=$(jq ".file.state" file_info.json)
done

curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Please describe this file."},
          {"file_data":{"mime_type": "video/mp4", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo
# [END text_gen_multimodal_video_prompt_streaming]

echo "[START text_gen_multimodal_pdf]"
# [START text_gen_multimodal_pdf]
MIME_TYPE=$(file -b --mime-type "${PDF_PATH}")
NUM_BYTES=$(wc -c < "${PDF_PATH}")
DISPLAY_NAME=TEXT


echo $MIME_TYPE
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
  --data-binary "@${PDF_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri

# Now generate content using that file
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Can you add a few more lines to this poem?"},
          {"file_data":{"mime_type": "application/pdf", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo

jq ".candidates[].content.parts[].text" response.json
# [END text_gen_multimodal_pdf]

echo "[START text_gen_multimodal_pdf_streaming]"
# [START text_gen_multimodal_pdf_streaming]
MIME_TYPE=$(file -b --mime-type "${PDF_PATH}")
NUM_BYTES=$(wc -c < "${PDF_PATH}")
DISPLAY_NAME=TEXT


echo $MIME_TYPE
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
  --data-binary "@${PDF_PATH}" 2> /dev/null > file_info.json

file_uri=$(jq ".file.uri" file_info.json)
echo file_uri=$file_uri

# Now generate content using that file
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [{
        "parts":[
          {"text": "Can you add a few more lines to this poem?"},
          {"file_data":{"mime_type": "application/pdf", "file_uri": '$file_uri'}}]
        }]
       }' 2> /dev/null > response.json

cat response.json
echo
# [END text_gen_multimodal_pdf_streaming]