# Use Gemini in OpenAI Format (via LiteLLM Proxy)

Use LiteLLM Proxy to track usage + set budgets call Gemini/Anthropic/OpenAI etc.


Works for [Google AI Studio](https://docs.litellm.ai/docs/providers/gemini) + [Vertex AI](https://docs.litellm.ai/docs/providers/vertex) calls.

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

```bash
import openai
client = openai.OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"
)

# request sent to model set on litellm proxy, `litellm --model`
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages = [
        {
            "role": "user",
            "content": "this is a test request, write a short poem"
        }
    ]
)

print(response)
```


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
  model="gpt-4o",
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
```python

from openai import OpenAI

client = OpenAI(api_key="anything", base_url="http://0.0.0.0:4000")

response = client.chat.completions.create(
    model="gpt-4-turbo",
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
