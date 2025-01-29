set -eu

echo "[START tuned_models_create]"
# [START tuned_models_create]
curl -X POST "https://generativelanguage.googleapis.com/v1beta/tunedModels?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -d '
      {
        "display_name": "number generator model",
        "base_model": "models/gemini-1.5-flash-001-tuning",
        "tuning_task": {
          "hyperparameters": {
            "batch_size": 2,
            "learning_rate": 0.001,
            "epoch_count":5,
          },
          "training_data": {
            "examples": {
              "examples": [
                {
                    "text_input": "1",
                    "output": "2",
                },{
                    "text_input": "3",
                    "output": "4",
                },{
                    "text_input": "-3",
                    "output": "-2",
                },{
                    "text_input": "twenty two",
                    "output": "twenty three",
                },{
                    "text_input": "two hundred",
                    "output": "two hundred one",
                },{
                    "text_input": "ninety nine",
                    "output": "one hundred",
                },{
                    "text_input": "8",
                    "output": "9",
                },{
                    "text_input": "-98",
                    "output": "-97",
                },{
                    "text_input": "1,000",
                    "output": "1,001",
                },{
                    "text_input": "10,100,000",
                    "output": "10,100,001",
                },{
                    "text_input": "thirteen",
                    "output": "fourteen",
                },{
                    "text_input": "eighty",
                    "output": "eighty one",
                },{
                    "text_input": "one",
                    "output": "two",
                },{
                    "text_input": "three",
                    "output": "four",
                },{
                    "text_input": "seven",
                    "output": "eight",
                }
              ]
            }
          }
        }
      }' | tee tunemodel.json

# Check the operation for status updates during training.
# Note: you can only check the operation on v1/
operation=$(cat tunemodel.json | jq ".name" | tr -d '"')
tuning_done=false

while [[ "$tuning_done" != "true" ]];
do
  sleep 5
  curl -X GET "https://generativelanguage.googleapis.com/v1/${operation}?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
     2> /dev/null > tuning_operation.json

  complete=$(jq .metadata.completedPercent < tuning_operation.json)
  tput cuu1
  tput el
  echo "Tuning...${complete}%"
  tuning_done=$(jq .done < tuning_operation.json)
done

# Or get the TunedModel and check it's state. The model is ready to use if the state is active.
modelname=$(cat tunemodel.json | jq ".metadata.tunedModel" | tr -d '"')
curl -X GET  https://generativelanguage.googleapis.com/v1beta/${modelname}?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' > tuned_model.json

cat tuned_model.json | jq ".state"
# [END tuned_models_create]


echo "[START tuned_models_generate_content]"
# [START tuned_models_generate_content]
curl -X POST https://generativelanguage.googleapis.com/v1beta/$modelname:generateContent?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' \
    -d '{
        "contents": [{
        "parts": [{
          "text": "LXIII"
          }]
        }]
        }' 2> /dev/null
# [END tuned_models_generate_content]

echo "[START tuned_models_get]"
# [START tuned_models_get]
curl -X GET https://generativelanguage.googleapis.com/v1beta/${modelname}?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' | grep state
# [END tuned_models_get]

echo "[START tuned_models_list]"
# [START tuned_models_list]
# Sending a page_size is optional
curl -X GET https://generativelanguage.googleapis.com/v1beta/tunedModels?page_size=5 \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${access_token}" \
    -H "x-goog-user-project: ${project_id}" > tuned_models.json

jq .tunedModels[].name < tuned_models.json

# Send the nextPageToken to get the next page.
page_token=$(jq .nextPageToken < tuned_models.json | tr -d '"')

if [[ "$page_token" != "null"" ]]; then
curl -X GET https://generativelanguage.googleapis.com/v1beta/tunedModels?page_size=5\&page_token=${page_token}?key=$GOOGLE_API_KEY \
    -H "Content-Type: application/json"  > tuned_models2.json
jq .tunedModels[].name < tuned_models.json
fi
# [END tuned_models_list]

echo "[START tuned_models_delete]"
# [START tuned_models_delete]
curl -X DELETE https://generativelanguage.googleapis.com/v1beta/${modelname}?key=$GOOGLE_API_KEY \
    -H 'Content-Type: application/json' 
# [END tuned_models_delete]