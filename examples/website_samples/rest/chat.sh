set -eu

SCRIPT_DIR=$(dirname "$0")
MEDIA_DIR=$(realpath ${SCRIPT_DIR}/../../third_party)

echo "[START chat]"
# [START chat]
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [
        {"role":"user",
         "parts":[{
           "text": "Hello"}]},
        {"role": "model",
         "parts":[{
           "text": "Great to meet you. What would you like to know?"}]},
        {"role":"user",
         "parts":[{
           "text": "I have two dogs in my house. How many paws are in my house?"}]},
      ]
    }' 2> /dev/null | grep "text"
# [END chat]

echo "[START chat_streaming]"
# [START chat_streaming]
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [
        {"role":"user",
         "parts":[{
           "text": "Hello"}]},
        {"role": "model",
         "parts":[{
           "text": "Great to meet you. What would you like to know?"}]},
        {"role":"user",
         "parts":[{
           "text": "I have two dogs in my house. How many paws are in my house?"}]},
      ]
    }' 2> /dev/null | grep "text"
# [END chat_streaming]

echo "[START chat_streaming_with_images]"
# [START chat_streaming_with_images]
IMG_PATH=${MEDIA_DIR}/organ.jpg

if [[ "$(base64 --version 2>&1)" = *"FreeBSD"* ]]; then
  B64FLAGS="--input"
else
  B64FLAGS="-w0"
fi

curl https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Hello, I am interested in learning about musical instruments. Can I show you one?"
                    }
                ]
            },
            {
                "role": "model",
                "parts": [
                    {
                        "text": "Certainly."
                    },
                ]
            },
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Tell me about this instrument"
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": "'$(base64 $B64FLAGS $IMG_PATH)'"
                        }
                    }
                ]
            }
        ]
    }' 2> /dev/null | grep "text"
# [END chat_streaming_with_images]