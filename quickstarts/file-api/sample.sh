#!/bin/bash
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

# Upload a file using the GenAI File API via curl.
api_key=""
input_file=""
display_name=""

while getopts a:i:d: flag
do
    case "${flag}" in
        a) api_key=${OPTARG};;
        i) input_file=${OPTARG};;
        d) display_name=${OPTARG};;
    esac
done

BASE_URL="https://generativelanguage.googleapis.com"

CHUNK_SIZE=8388608  # 8 MiB
MIME_TYPE=$(file -b --mime-type "${input_file}")
NUM_BYTES=$(wc -c < "${input_file}")

echo "Starting upload of '${input_file}' to ${BASE_URL}..."
echo "  MIME type: '${MIME_TYPE}'"
echo "  Size: ${NUM_BYTES} bytes"

# Initial resumable request defining metadata.
tmp_header_file=$(mktemp /tmp/upload-header.XXX)
curl "${BASE_URL}/upload/v1beta/files?key=${api_key}" \
  -D "${tmp_header_file}" \
  -H "X-Goog-Upload-Protocol: resumable" \
  -H "X-Goog-Upload-Command: start" \
  -H "X-Goog-Upload-Header-Content-Length: ${NUM_BYTES}" \
  -H "X-Goog-Upload-Header-Content-Type: ${MIME_TYPE}" \
  -H "Content-Type: application/json" \
  -d "{'file': {'display_name': '${display_name}'}}"
upload_url=$(grep "x-goog-upload-url: " "${tmp_header_file}" | cut -d" " -f2 | tr -d "\r")
rm "${tmp_header_file}"

if [[ -z "${upload_url}" ]]; then
  echo "Failed initial resumable upload request."
  exit 1
fi

# Upload the actual bytes.
NUM_CHUNKS=$(((NUM_BYTES + CHUNK_SIZE - 1) / CHUNK_SIZE))
tmp_chunk_file=$(mktemp /tmp/upload-chunk.XXX)
for i in $(seq 1 ${NUM_CHUNKS})
do
  offset=$((i - 1))
  byte_offset=$((offset * CHUNK_SIZE))
  # Read the actual bytes to the tmp file.
  dd skip="${offset}" bs="${CHUNK_SIZE}" count=1 if="${input_file}" of="${tmp_chunk_file}" 2>/dev/null
  num_chunk_bytes=$(wc -c < "${tmp_chunk_file}")
  upload_command="upload"
  if [[ ${i} -eq ${NUM_CHUNKS} ]] ; then
    # For the final chunk, specify "finalize".
    upload_command="${upload_command}, finalize"
  fi
  echo "  Uploading ${byte_offset} - $((byte_offset + num_chunk_bytes)) of ${NUM_BYTES}..."
  curl "${upload_url}" \
    -H "Content-Length: ${num_chunk_bytes}" \
    -H "X-Goog-Upload-Offset: ${byte_offset}" \
    -H "X-Goog-Upload-Command: ${upload_command}" \
    --data-binary "@${tmp_chunk_file}"
done

rm "${tmp_chunk_file}"

echo "Upload complete!"
