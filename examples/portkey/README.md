# Portkey AI with Gemini
[Portkey](https://portkey.ai/?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs) is the Control Panel for AI apps, offering an AI Gateway and Observability Suite that enables teams to build **reliable**, **cost-efficient**, and **fast** applications. This guide will walk you through integrating Portkey with Google Gemini, allowing you to leverage Gemini's powerful LLMs through Portkey's unified API and advanced features.

## Key Features

With Portkey, you can:

- [x] Connect to 250+ models through a unified API
- [x] Monitor 42+ metrics & logs for all requests
- [x] Enable semantic caching to reduce latency & costs
- [x] Implement reliability features like conditional routing, retries & fallbacks
- [x] Add custom tags to requests for better tracking and analysis
- [x] Guardrails and more

## Quickstart

### 1. Installation

Install the Portkey SDK in your environment:

```sh
pip install portkey-ai
```


### 2. Initialize Portkey with a Virtual Key

To use Gemini with Portkey, you'll need two keys:

1. **Portkey API Key**: Sign up at [app.portkey.ai](https://app.portkey.ai/signup?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs) and copy your [API key](https://app.portkey.ai/api-keys?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs).
2. **Gemini API Key**: Generate your [Gemini API Key](https://aistudio.google.com/apikey).

Create a `Virtual Key` in Portkey to securely store your Gemini API key:

1. Navigate to the Virtual Keys tab in Portkey, and create a new key for Gemini
2. Use the Virtual Key in your code:

```python
from portkey_ai import Portkey

portkey = Portkey(
    api_key="YOUR_PORTKEY_API_KEY",
    virtual_key="YOUR_GEMINI_VIRTUAL_KEY"
)
```



> You can also make API calls without using virtual key, learn more [here](https://github.com/portkey-ai/gateway)
### 4. Make API Calls

Now you can make calls to models powered by Gemini through Portkey:

```python
completion = portkey.chat.completions.create(
    messages=[{"role": "user", "content": "Say this is a test"}],
    model="gemini-1.5-flash"
)

print(completion)
```



### Observability

Portkey automatically logs all requests, making debugging and monitoring simple. View detailed logs and traces in the Portkey dashboard.


![observability dashboard](https://raw.githubusercontent.com/siddharthsambharia-portkey/Portkey-Product-Images/refs/heads/main/Portkey-Dashboard.png)


![image](https://raw.githubusercontent.com/siddharthsambharia-portkey/Portkey-Product-Images/refs/heads/main/Portkey-Traces.png)


### Using 250+ Models

One of Portkey's strengths is the ability to easily switch between different LLM providers. To do so, simply change the virtual key.

```python
portkey = Portkey(
    api_key="YOUR_PORTKEY_API_KEY",
    virtual_key="VIRTUAL_KEY",
)
```


### Add Custom-data to your requests
You can send custom metadata along with your requests in Portkey, which can later be used for auditing or filtering logs. You can pass **any number** of keys, all values should be of type `string` with max-length as **128** characters.

```python
portkey = Portkey(
    api_key="PORTKEY_API_KEY",
    virtual_key="GEMINI_VIRTUAL_KEY"
)

response = portkey.with_options(
    metadata = {
        "environment": "production",
        "prompt": "test_prompt",
        "session_id": "1729"
}).chat.completions.create(
    messages = [{ "role": 'user', "content": 'What is 1729' }],
    model = 'gmeini-1.5-flash'
)

print(response.choices[0].message)
```


## Advanced Routing

Portkey config is a JSON object that defines how Portkey should handle your API requests. Configs allow you to customize various aspects of your API calls, including routing, caching, and reliability features. You can apply configs globally when initializing the Portkey client.

Here's a basic structure of a Portkey config:

```python
portkey = Portkey(
    api_key="YOUR_PORTKEY_API_KEY",
    virtual_key="YOUR_GEMINI_VIRTUAL_KEY",
    config=test_config, # Example Configs of features like load-balance, guardrails, routing are given below.
    model="gemini-1.5-flash"
)
```



Portkey offers sophisticated routing capabilities to enhance the reliability and flexibility of your LLM integrations. Here are some key routing features:

1. **Retries**: Automatically retry failed requests.
2. **Fallbacks**: Specify alternative models or providers if the primary option fails.
3. **Conditional Routing**: Route requests based on specific conditions.
4. **Load Balancing**: Distribute requests across multiple models or providers.

Let's explore some of these features with examples:


### 1. Guardrails
Portkey’s Guardrails allow you to verify your LLM inputs AND outputs, adhering to your specifed checks. You can orchestrate your request - with actions ranging from denying the request, logging the guardrail result, creating an evals dataset, falling back to another LLM or prompt, retrying the request, and more.

```python
guardrails_config = {
    "before_request_hooks": [{
        "id": "input-guardrail-id-xx"
    }],
    "after_request_hooks": [{
        "id": "output-guardrail-id-xx"
    }]
}
```



### 2. Caching

Enable semantic caching to reduce latency and costs:

```python
test_config = {
    "cache": {
        "mode": "semantic", # Choose between simple and semantic
    }
}
```



### 3. Retries and Fallbacks

```python
retry_fallback_config = {
    "retry": {
        "attempts": 3,
    },
    "fallback": {
        "targets": [
            {"virtual_key": "openai-virtual-key"},
            {"virtual_key": "anthropic-virtual-key"}
        ]
    }
}
```

This configuration attempts to retry the Geimini's request up to 3 times if a timeout or rate limit error occurs. If all retries fail, it will fallback to OpenAI's GPT-3.5 Turbo, and if that fails, to Anthropic's Claude 3.5.

### 4. Conditional Routing

```python
test_config = {
  "strategy": {
    "mode": "conditional",
    "conditions": [
      {
        "query": { "metadata.user_plan": { "$eq": "paid" } },
        "then": "free-model"
      },
      {
        "query": { "metadata.user_plan": { "$eq": "free" } },
        "then": "paid-model"
      }
    ],
    "default": "free-model"
  },
  "targets": [
    {
      "name": "free-model",
      "virtual_key": "gemini-virtual-key",
      "override_params": {"model": "gemini-1.5-flash-8b"},
    },
     {
      "name": "paid-model",
      "virtual_key": "gemini-virtual-key",
      "override_params": {"model": "gemini-1.5-flash"},
    },
  ]
}

```

This configuration routes requests to gemini-1.5-flash model for `paid` and to gemini-1.5-flash-8b Turbo for `free`, based on the `user_plan` metadata.

### 5. Load Balancing

```python
test_config = {
    "strategy": {
         "mode": "loadbalance"
    },
    "targets": [{
        "virtual_key": "Gemini-virtual-key",
        "override_params": {"model": "gemini-1.5-flash"},
        "weight": 0.7
    }, {
        "virtual_key": "Gemini-virtual-key",
        "override_params": {"model": "gemini-1.0-pro"},
        "weight": 0.3
    }]
}
```

This configuration distributes 70% of traffic to Gemini's Flash model and 30% to Gemini's Pro.

## Managing Google Gemini Prompts
You can manage all prompts to Google Gemini in the Prompt Library. All the current models of Google Gemini are supported and you can easily start testing different prompts.

Once you’re ready with your prompt, you can use the   `portkey.prompts.completions.create` interface to use the prompt in your application.

[Learn more on Portkey docs](https://portkey.ai/docs/product/prompt-library#prompt-library?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs)

![prompt dashboard](https://github.com/siddharthsambharia-portkey/Portkey-Product-Images/blob/main/Portkey-Prompt-Library.png?raw=true)


## Additional Resources

- [Portkey Observability Documentation](https://portkey.ai/docs/product/observability?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs)
- [AI Gateway Documentation](https://portkey.ai/docs/product/ai-gateway?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs)

- [Open Source AI Gateway](https://github.com/portkey-ai/gateway?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs)

For detailed information on each feature and how to use it, please refer to the [Portkey documentation](https://docs.portkey.ai/?utm_source=gemini&utm_medium=external_integration&utm_campaign=gemini-docs).

If you have any questions or need further assistance, reach out to us on [Discord](https://discord.gg/portkey-llms-in-prod-1143393887742861333) or via email at [hello@portkey.ai](mailto:hello@portkey.ai).

