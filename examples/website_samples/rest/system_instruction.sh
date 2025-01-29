set -eu

echo "[START system_instruction]"
# [START system_instruction]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{ "system_instruction": {
    "parts":
      { "text": "You are a cat. Your name is Neko."}},
    "contents": {
      "parts": {
        "text": "Hello there"}}}'
# [END system_instruction]