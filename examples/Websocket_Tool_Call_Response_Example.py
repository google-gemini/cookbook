# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example: Handling Tool Call Responses with Gemini Live API Websockets

This example demonstrates the CORRECT way to send function/tool call responses
back to the Gemini Live API using websockets.

## The Issue (GitHub #906)
The documentation mentions BidiGenerateContentToolResponse, but the actual
format that works is different. This example shows the working solution.

## Setup

Install dependencies:
```
pip install websockets
```

Set your API key:
```
export GOOGLE_API_KEY="your-api-key"
```

## Run
```
python Websocket_Tool_Call_Response_Example.py
```
"""

import asyncio
import json
import os
from websockets.asyncio.client import connect

# Configuration
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable must be set")

host = "generativelanguage.googleapis.com"
model = "gemini-2.0-flash-live-001"
uri = f"wss://{host}/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key={GOOGLE_API_KEY}"


# Example tool functions
def get_weather(location: str) -> dict:
    """Mock function to get weather information."""
    return {
        "location": location,
        "temperature": "72°F",
        "condition": "Sunny",
        "humidity": "45%"
    }


def turn_on_lights() -> dict:
    """Mock function to turn on lights."""
    return {"status": "success", "message": "Lights turned on"}


def turn_off_lights() -> dict:
    """Mock function to turn off lights."""
    return {"status": "success", "message": "Lights turned off"}


# Tool registry mapping function names to implementations
TOOL_REGISTRY = {
    "get_weather": get_weather,
    "turn_on_lights": turn_on_lights,
    "turn_off_lights": turn_off_lights,
}


async def setup_session(ws):
    """Initialize the websocket session with model configuration and tools."""
    setup_msg = {
        "setup": {
            "model": f"models/{model}",
            "generation_config": {
                "response_modalities": ["TEXT"]
            },
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
                                        "description": "The city and state, e.g. San Francisco, CA"
                                    }
                                },
                                "required": ["location"]
                            }
                        },
                        {
                            "name": "turn_on_lights",
                            "description": "Turn on the lights"
                        },
                        {
                            "name": "turn_off_lights",
                            "description": "Turn off the lights"
                        }
                    ]
                }
            ]
        }
    }
    
    print("📤 Sending setup message...")
    await ws.send(json.dumps(setup_msg))
    
    # Wait for setup confirmation
    raw_response = await ws.recv(decode=False)
    setup_response = json.loads(raw_response.decode("ascii"))
    print("✅ Setup complete:", setup_response)
    return setup_response


async def send_user_message(ws, text: str):
    """Send a user message to the model."""
    msg = {
        "client_content": {
            "turns": [
                {
                    "role": "user",
                    "parts": [{"text": text}]
                }
            ],
            "turn_complete": True
        }
    }
    print(f"\n📤 User: {text}")
    await ws.send(json.dumps(msg))


async def handle_tool_call(ws, tool_call: dict):
    """
    Handle tool calls from the model.
    
    CRITICAL: The correct format for tool responses is:
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
    
    DO NOT use "BidiGenerateContentToolResponse" - it doesn't work!
    
    Alternative format (as suggested in the GitHub issue):
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
    """
    print("\n🔧 Tool calls received:")
    
    function_calls = tool_call.get('functionCalls', [])
    
    # Process each function call
    for fc in function_calls:
        function_name = fc['name']
        function_id = fc['id']
        function_args = fc.get('args', {})
        
        print(f"  • {function_name}({function_args})")
        
        # Execute the function
        if function_name in TOOL_REGISTRY:
            try:
                # Get the function and call it with the arguments
                func = TOOL_REGISTRY[function_name]
                result = func(**function_args)
                print(f"    ✓ Result: {result}")
                
                # METHOD 1: Using tool_response (preferred based on cookbook examples)
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
                
                # METHOD 2: Using clientContent with functionResponse (alternative)
                # Uncomment to use this method instead:
                # response_msg = {
                #     "clientContent": {
                #         "turns": [
                #             {
                #                 "role": "user",
                #                 "parts": [
                #                     {
                #                         "functionResponse": {
                #                             "name": function_name,
                #                             "response": {
                #                                 "output": result
                #                             }
                #                         }
                #                     }
                #                 ]
                #             }
                #         ],
                #         "turnComplete": True
                #     }
                # }
                
                print(f"📤 Sending tool response: {json.dumps(response_msg, indent=2)}")
                await ws.send(json.dumps(response_msg))
                
            except TypeError as e:
                print(f"    ✗ Error executing {function_name}: {e}")
                # Send error response
                error_response = {
                    "tool_response": {
                        "function_responses": [
                            {
                                "id": function_id,
                                "name": function_name,
                                "response": {
                                    "result": {
                                        "error": str(e)
                                    }
                                }
                            }
                        ]
                    }
                }
                await ws.send(json.dumps(error_response))
        else:
            print(f"    ✗ Unknown function: {function_name}")


async def process_responses(ws):
    """Process responses from the model."""
    async for raw_response in ws:
        response = json.loads(raw_response.decode("ascii"))
        
        # Handle server content (text responses)
        server_content = response.get("serverContent")
        if server_content:
            model_turn = server_content.get("modelTurn")
            if model_turn:
                parts = model_turn.get("parts", [])
                for part in parts:
                    if "text" in part:
                        print(f"🤖 Model: {part['text']}")
            
            # Check if turn is complete
            if server_content.get("turnComplete"):
                print("\n✓ Turn complete\n")
                break
        
        # Handle tool calls
        tool_call = response.get("toolCall")
        if tool_call:
            await handle_tool_call(ws, tool_call)


async def main():
    """Main function demonstrating tool call handling."""
    print("=" * 70)
    print("Gemini Live API - Websocket Tool Call Response Example")
    print("=" * 70)
    
    async with connect(
        uri, 
        additional_headers={"Content-Type": "application/json"}
    ) as ws:
        # Setup session
        await setup_session(ws)
        
        # Example 1: Simple function call
        print("\n" + "=" * 70)
        print("Example 1: Simple weather query")
        print("=" * 70)
        await send_user_message(ws, "What's the weather in San Francisco?")
        await process_responses(ws)
        
        # Example 2: Multiple function calls
        print("\n" + "=" * 70)
        print("Example 2: Multiple function calls")
        print("=" * 70)
        await send_user_message(
            ws, 
            "Turn on the lights and tell me the weather in New York"
        )
        await process_responses(ws)
        
        # Example 3: Function call with follow-up
        print("\n" + "=" * 70)
        print("Example 3: Function call with follow-up")
        print("=" * 70)
        await send_user_message(ws, "Get the weather for London")
        await process_responses(ws)
        
        await send_user_message(ws, "Is that good weather?")
        await process_responses(ws)
        
    print("\n" + "=" * 70)
    print("✓ Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
