set -eu

echo "[START safety_settings]"
# [START safety_settings]
    echo '{
    "safetySettings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"}
    ],
    "contents": [{
        "parts":[{
            "text": "'I support Martians Soccer Club and I think Jupiterians Football Club sucks! Write a ironic phrase about them.'"}]}]}' > request.json
    
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d @request.json 2> /dev/null
# [END safety_settings]

echo "[START safety_settings_multi]"
# [START safety_settings_multi]
    echo '{
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ],
        "contents": [{
            "parts":[{
                "text": "'I support Martians Soccer Club and I think Jupiterians Football Club sucks! Write a ironic phrase about them.'"}]}]}' > request.json

    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
        -H 'Content-Type: application/json' \
        -X POST \
        -d @request.json 2> /dev/null
# [END safety_settings_multi]
