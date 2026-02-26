# Websocket Tool Call Response - Solution for GitHub Issue #906

## Problem summary

When using the Gemini Live API with websockets for function calling, the documentation mentions `BidiGenerateContentToolResponse` but doesn't clearly explain the correct format for sending function/tool responses back to the model. Many developers encounter connection closures or non-functional responses when trying to implement tool calling.

## The Issue

Users were struggling with:
1. Unclear documentation about the `BidiGenerateContentToolResponse` format
2. The field name `functionResponses[]` mentioned in docs not working
3. Websocket connections closing when sending tool responses
4. No clear examples of the working format for websockets

## The solution

There are **TWO working formats** for sending tool responses via websockets:

### Method 1: Using `tool_response` (Recommended)

This is the format used in the official cookbook examples and is the recommended approach:

```json
{
  "tool_response": {
    "function_responses": [
      {
        "id": "<function_call_id>",
        "name": "<function_name>",
        "response": {
          "result": <your_result_data>
        }
      }
    ]
  }
}
```

**Python Example:**
```python
response_msg = {
    "tool_response": {
        "function_responses": [
            {
                "id": function_id,
                "name": function_name,
                "response": {"result": result}
            }
        ]
    }
}
await ws.send(json.dumps(response_msg))
```

### Method 2: Using `clientContent` with `functionResponse`

This alternative format was suggested by community members and also works:

```json
{
  "clientContent": {
    "turns": [
      {
        "role": "user",
        "parts": [
          {
            "functionResponse": {
              "name": "<function_name>",
              "response": {
                "output": <your_result_data>
              }
            }
          }
        ]
      }
    ],
    "turnComplete": true
  }
}
```

**Python Example:**
```python
response_msg = {
    "clientContent": {
        "turns": [
            {
                "role": "user",
                "parts": [
                    {
                        "functionResponse": {
                            "name": function_name,
                            "response": {
                                "output": result
                            }
                        }
                    }
                ]
            }
        ],
        "turnComplete": True
    }
}
await ws.send(json.dumps(response_msg))
```

## Key differences from documentation

**What DOESN'T work:**
- ❌ `BidiGenerateContentToolResponse` as a top-level message type
- ❌ `functionResponses` (without the nested structure)
- ❌ Sending responses without proper structure

**What DOES work:**
- ✅ `tool_response` with nested `function_responses` array
- ✅ `clientContent` with `functionResponse` in parts
- ✅ Both methods require proper function ID and name matching

## Complete working example

See the full working example in:
- [`Websocket_Tool_Call_Response_Example.py`](./Websocket_Tool_Call_Response_Example.py)

This example demonstrates:
- Proper websocket setup with tool declarations
- Handling tool calls from the model
- Sending tool responses back in the correct format
- Multiple function calls in sequence
- Error handling

## Code comparison

### SDK vs Websockets

**With SDK (google-genai):**
```python
from google import genai
from google.genai import types

# Function response is simple
function_response = types.FunctionResponse(
    id=fc.id,
    name=fc.name,
    response={"result": "ok"}
)

# Send it
await session.send_tool_response(function_responses=[function_response])
```

**With Websockets:**
```python
import json

# Must format as JSON with specific structure
response_msg = {
    "tool_response": {
        "function_responses": [
            {
                "id": fc['id'],
                "name": fc['name'],
                "response": {"result": "ok"}
            }
        ]
    }
}

# Send as JSON string
await ws.send(json.dumps(response_msg))
```

## Tool declaration format

When setting up the websocket session, declare your tools like this:

```python
setup_msg = {
    "setup": {
        "model": f"models/{model}",
        "tools": [
            {
                "function_declarations": [
                    {
                        "name": "get_weather",
                        "description": "Get the current weather for a location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "City and state"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                ]
            }
        ]
    }
}
```

## Handling tool calls

When the model wants to call a function, you'll receive a message like:

```json
{
  "toolCall": {
    "functionCalls": [
      {
        "id": "abc123",
        "name": "get_weather",
        "args": {
          "location": "San Francisco, CA"
        }
      }
    ]
  }
}
```

Process it and send back the response using one of the two methods above.

## Common pitfalls

1. **Forgetting the function ID**: Always include the `id` field from the original function call
2. **Wrong nesting**: The response data must be nested correctly under `response.result` or `response.output`
3. **Not setting turnComplete**: For the clientContent method, include `"turnComplete": true`
4. **Sending as Python dict instead of JSON string**: Use `json.dumps()` to convert to string
5. **Mismatched function names**: The response name must match the call name exactly

## Testing your implementation

Use this simple test to verify your tool responses work:

```python
async def test_tool_response():
    async with connect(uri) as ws:
        await setup_session(ws)
        
        # Send a message that should trigger a tool call
        await send_user_message(ws, "What's the weather in London?")
        
        # Process responses - if you get a tool call and can respond
        # without the websocket closing, it works!
        await process_responses(ws)
```

## References

- GitHub Issue: [#906](https://github.com/google-gemini/cookbook/issues/906)
- Official Cookbook: [Get_started_LiveAPI_tools.ipynb](../../quickstarts/Get_started_LiveAPI_tools.ipynb)
- Websocket Examples: [websockets/Get_started_LiveAPI_tools.ipynb](../../quickstarts/websockets/Get_started_LiveAPI_tools.ipynb)
- API Documentation: [Live API Function Calling](https://ai.google.dev/api/live#FunctionResponse)

## Credits

- Solution identified by [@nmfisher](https://github.com/nmfisher) in issue #906
- Cookbook examples by Google Gemini team
- Community contributions and testing

## Need help?

If you're still having issues:
1. Check that your API key is valid
2. Verify you're using a compatible model (e.g., `gemini-2.0-flash-live-001`)
3. Ensure your websocket URI is correct
4. Review the complete example in `Websocket_Tool_Call_Response_Example.py`
5. Open an issue in the [cookbook repository](https://github.com/google-gemini/cookbook/issues)
