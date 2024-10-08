# Use Gemini in OpenAI Format (via LiteLLM Gateway)

Use LiteLLM AI Gateway to loadbalance + track usage + set budgets across calls Gemini/VertexAI/etc. 


Works for [Google AI Studio](https://docs.litellm.ai/docs/providers/gemini) + [Vertex AI](https://docs.litellm.ai/docs/providers/vertex) calls.


Note: LiteLLM Gateway is **OpenAI-Compatible**. This means you can call it with any project (ContinueDev, Librechat, etc.) or sdk (Langfuse, LlamaIndex, Instructor, etc.), that supports OpenAI. 

## Sample Usage

### Pre-requisites
* `pip install -q google-generativeai`
* Get API Key - https://aistudio.google.com/
* `pip install 'litellm[proxy]'`

```bash
export GEMINI_API_KEY="" # add gemini api key to environment
```



1. Setup config.yaml 
```yaml
model_list:
    - model_name: gemini-pro
      litellm_params:
        model: gemini/gemini-pro
        api_key: os.environ/GEMINI_API_KEY
```

2. Start proxy 

```bash
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000
```

3. Test it! 

[Use with Langchain, LlamaIndex, Instructor, etc.](https://docs.litellm.ai/docs/proxy/user_keys)

```python
import openai
client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(
    model="gemini-pro", # model name in config.yaml
    messages = [
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ]
)

print(response)
```

## Loadbalance + Fallbacks b/w Google AI Studio and VertexAI 

LiteLLM supports loadbalancing + fallbacks across 100+ LLMs. Just use `model_name` to loadbalance between a group of models. 

### Usage

Let's setup loadbalancing between gemini-pro models and fallback to vertex_ai/anthropic in case of failure 

Pre-requisites 
- run `!gcloud auth application-default login` to add vertex credentials to your environment ([See alternative auth mechanisms](https://docs.litellm.ai/docs/providers/vertex))

### 1. Setup config.yaml 

```yaml 
model_list:
    - model_name: gemini-pro
      litellm_params:
        model: gemini/gemini-pro
        api_key: os.environ/GEMINI_API_KEY
    - model_name: gemini-pro
      litellm_params:
        model: vertex_ai/gemini-pro 
        vertex_credentials: /path/to/service_account.json
        vertex_project: my-project
        vertex_region: my-region
    - model_name: anthropic-vertex
      litellm_params:
        model: vertex_ai/claude-3-sonnet@20240229
        vertex_ai_project: "my-test-project"
        vertex_ai_location: "us-east-1"

litellm_settings:
  fallbacks: [{"gemini-pro": ["anthropic-vertex"]}]
```

### 2. Start proxy 

```bash
litellm --config /path/to/config.yaml 

# RUNNING on http://0.0.0.0:4000
```

### 3. Test it! 

1. Test simple call

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "gemini-pro",
    "messages": [
        {
        "role": "user",
        "content": "what llm are you"
        }
    ]
}'
```

2. Test loadbalancing

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-H 'Authorization: Bearer sk-1234' \
-d '{
  "model": "gemini-pro",
  "messages": [
        {"role": "user", "content": "Hi there!"}
    ],
    "mock_testing_rate_limit_error": true
}'
```

3. Test fallbacks 

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
    -H 'Content-Type: application/json' \
    -d '{
    "model": "gemini-pro",
    "messages": [
        {
        "role": "user",
        "content": "what llm are you"
        }
    ],
    "mock_testing_fallbacks": true 
}'
```


## Track Usage

LiteLLM supports logging to LLMOps tools like Langfuse, Langsmith, any OTEL endpoint, etc. as well as storage services like s3, gcs. [Full List](https://docs.litellm.ai/docs/proxy/logging)

Here's how to log Gemini cost data to [Langsmith](https://www.langchain.com/langsmith) for usage tracking 


### 1. Setup config.yaml 

```yaml
model_list:
    - model_name: gemini-pro
      litellm_params:
        model: gemini/gemini-pro
        api_key: os.environ/GEMINI_API_KEY

litellm_settings:
  success_callback: ["langsmith"] # 

environment_variables: # can also just be added to env via `export key=value` 
  LANGSMITH_API_KEY: "lsv2_pt_xxxxxxxx"
  LANGSMITH_PROJECT: "litellm-proxy" # [OPTIONAL]
  LANGSMITH_BASE_URL: "https://api.smith.langchain.com" # [OPTIONAL] only needed if you have a custom Langsmith instance
```

### 2. Start proxy 

```bash
litellm --config /path/to/config.yaml --detailed_debug

# RUNNING on http://0.0.0.0:4000
```

### 3. Test it! 

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-d ' {
      "model": "gemini-pro",
      "messages": [
        {
          "role": "user",
          "content": "Hello, Gemini!"
        }
      ],
    }
'
```

Expect to see your call logged on your Langsmith project with the response_cost, token usage, etc. 

## Advanced - Track Usage per project

LiteLLM lets you track spend for a call by model, key, team, user, making it ideal for cost attribution and budgeting. [**Learn More**](https://docs.litellm.ai/docs/proxy/virtual_keys)

Pre-requisites: 
- [Setup LiteLLM Proxy with DB](https://docs.litellm.ai/docs/proxy/virtual_keys#setup)


### Quick Start 

Let's track spend by LiteLLM key. 

1. Setup config.yaml 

```yaml
model_list:
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GEMINI_API_KEY

general_settings: 
  master_key: sk-1234 
  database_url: "postgresql://<user>:<password>@<host>:<port>/<dbname>" # 👈 KEY CHANGE
```

2. Create LiteLLM Virtual key

```bash
curl -X POST 'http://0.0.0.0:4000/key/generate' \
-H 'Authorization: Bearer <your-master-key>' \
-H 'Content-Type: application/json' \
-d '{}'
```

3. Make call with LiteLLM Virtual key 

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-d ' {
      "model": "gemini-pro",
      "messages": [
        {
          "role": "user",
          "content": "Hello, Gemini!"
        }
      ],
    }
'
```

### Set Budgets per project 

Let's set budgets on a LiteLLM key. (Can also do this by [user/team](https://docs.litellm.ai/docs/proxy/users#set-budgets))

1. Setup config.yaml 

```yaml
model_list:
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GEMINI_API_KEY

general_settings: 
  master_key: sk-1234 
  database_url: "postgresql://<user>:<password>@<host>:<port>/<dbname>" # 👈 KEY CHANGE
```

2. Create LiteLLM Virtual key

```bash
curl -X POST 'http://0.0.0.0:4000/key/generate' \
-H 'Authorization: Bearer <your-master-key>' \
-H 'Content-Type: application/json' \
-d '{"max_budget": 0, "budget_duration": "1m"}'
```

- "max_budget": This is the maximum budget allowed for a key within a period. By default, this is None. 
- "budget_duration": Budget is reset at the end of specified duration. If not set, budget is never reset. You can set duration as seconds ("30s"), minutes ("30m"), hours ("30h"), days ("30d"), months ("1mo").

[**See full API spec**](https://litellm-api.up.railway.app/#/key%20management/generate_key_fn_key_generate_post)

3. Make call with LiteLLM Virtual key 

```bash
curl -X POST 'http://0.0.0.0:4000/chat/completions' \
-H 'Content-Type: application/json' \
-d ' {
      "model": "gemini-pro",
      "messages": [
        {
          "role": "user",
          "content": "Hello, Gemini!"
        }
      ],
    }
'
```

Expect this call to fail, with a `BudgetExceededError:`. 


## Advanced - Specifying Safety Settings 
In certain use-cases you may need to make calls to the models and pass [safety settigns](https://ai.google.dev/docs/safety_setting_gemini) different from the defaults. To do so, simple pass the `safety_settings` argument to `completion` or `acompletion`. For example:

```yaml
model_list:
    - model_name: gemini-pro
      litellm_params:
        model: gemini/gemini-pro
        api_key: os.environ/GEMINI_API_KEY
        safety_settings: [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE",
            },
        ]
```

## Tool Calling 

```python
from openai import OpenAI
client = OpenAI(api_key="anything", base_url="http://0.0.0.0:4000")

tools = [
  {
    "type": "function",
    "function": {
      "name": "get_current_weather",
      "description": "Get the current weather in a given location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
          },
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
      },
    }
  }
]
messages = [{"role": "user", "content": "What's the weather like in Boston today?"}]
completion = client.chat.completions.create(
  model="gemini-pro",
  messages=messages,
  tools=tools,
  tool_choice="auto"
)

print(completion)

```


# Gemini-Pro-Vision
LiteLLM Supports the following image types passed in `url`
- Images with direct links - https://storage.googleapis.com/github-repo/img/gemini/intro/landmark3.jpg
- Image in local storage - ./localimage.jpeg

## Sample Usage


1. Setup config.yaml 
```yaml
model_list:
    - model_name: gemini-pro
      litellm_params:
        model: gemini/gemini-pro
        api_key: os.environ/GEMINI_API_KEY
```

2. Start proxy 

```bash
litellm --config /path/to/config.yaml

# RUNNING on http://0.0.0.0:4000
```

3. Test it! 

```python

from openai import OpenAI

client = OpenAI(api_key="anything", base_url="http://0.0.0.0:4000")

response = client.chat.completions.create(
    model="gemini-pro",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": 'https://storage.googleapis.com/github-repo/img/gemini/intro/landmark3.jpg',
                },
            ],
        }
    ],
    max_tokens=300,
)

print(response.choices[0])
```

## Chat Models

**ALL MODELS SUPPORTED**. 

Just add `gemini/` to the beginning of the model name.

Example models: 

| Model Name            | Function Call                                          | Required OS Variables          |
|-----------------------|--------------------------------------------------------|--------------------------------|
| gemini-pro            | `model:'gemini/gemini-pro'`            | `os.environ['GEMINI_API_KEY']` |
| gemini-1.5-pro-latest | `model: 'gemini/gemini-1.5-pro-latest'` | `os.environ['GEMINI_API_KEY']` |
| gemini-pro-vision     | `model: 'gemini/gemini-pro-vision'`     | `os.environ['GEMINI_API_KEY']` |
