set -eu

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

echo "[START cache_create]"
# [START cache_create]
wget https://storage.googleapis.com/generativeai-downloads/data/a11.txt
echo '{
  "model": "models/gemini-1.5-flash-001",
  "contents":[
    {
      "parts":[
        {
          "inline_data": {
            "mime_type":"text/plain",
            "data": "'$(base64 $B64FLAGS a11.txt)'"
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

CACHE_NAME=$(cat cache.json | grep '"name":' | cut -d '"' -f 4 | head -n 1)

echo "[START cache_generate_content]"
# [START cache_generate_content]
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-001:generateContent?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{
      "contents": [
        {
          "parts":[{
            "text": "Please summarize this transcript"
          }],
          "role": "user"
        },
      ],
      "cachedContent": "'$CACHE_NAME'"
    }'
# [END cache_generate_content]
# [END cache_create]
rm a11.txt request.json

echo "[START cache_list]"
# [START cache_list]
curl "https://generativelanguage.googleapis.com/v1beta/cachedContents?key=$GOOGLE_API_KEY"
# [END cache_list]

echo "[START cache_get]"
# [START cache_get]
curl "https://generativelanguage.googleapis.com/v1beta/$CACHE_NAME?key=$GOOGLE_API_KEY"
# [END cache_get]

echo "[START cache_update]"
# [START cache_update]
curl -X PATCH "https://generativelanguage.googleapis.com/v1beta/$CACHE_NAME?key=$GOOGLE_API_KEY" \
 -H 'Content-Type: application/json' \
 -d '{"ttl": "600s"}'
# [END cache_update]

echo "[START cache_delete]"
# [START cache_delete]
curl -X DELETE "https://generativelanguage.googleapis.com/v1beta/$CACHE_NAME?key=$GOOGLE_API_KEY"
# [END cache_delete]