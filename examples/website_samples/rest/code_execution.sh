set -eu 

echo "[START code_execution_basic]"
# [START code_execution_basic]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d ' {"tools": [{"code_execution": {}}],
    "contents": {
      "parts": 
        {
            "text": "What is the sum of the first 50 prime numbers? Generate and run code for the calculation, and make sure you get all 50."
        }
    },
}'
# [END code_execution_basic]

echo "[START code_execution_chat]"
# [START code_execution_chat]
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{"tools": [{"code_execution": {}}],
    "contents": [
        {
            "role": "user",
            "parts": [{
                "text": "Can you print \"Hello world!\"?"
            }]
        },{
            "role": "model",
            "parts": [
               {
                 "text": ""
               },
               {
                 "executable_code": {
                   "language": "PYTHON",
                   "code": "\nprint(\"hello world!\")\n"
                 }
               },
               {
                 "code_execution_result": {
                   "outcome": "OUTCOME_OK",
                   "output": "hello world!\n"
                 }
               },
               {
                 "text": "I have printed \"hello world!\" using the provided python code block. \n"
               }
             ],
        },{
            "role": "user",
            "parts": [{
                "text": "What is the sum of the first 50 prime numbers? Generate and run code for the calculation, and make sure you get all 50."
            }]
        }
    ]
}'
# [END code_execution_chat]
