# Copyright 2026 Google LLC
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
Example demonstrating cryptographic compliance checking and runtime scope validation
for the Google Antigravity SDK using Kakunin.
"""

from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv
from google.antigravity import Agent, LocalAgentConfig
from kakunin import Kakunin
from kakunin.exceptions import ScopeViolationError
from kakunin.integrations.google_antigravity import get_kakunin_hooks

# Load environment keys
load_dotenv()


def query_market_prices(symbol: str) -> str:
    """Query current prices for a ticker symbol."""
    print(f"[Tool Executed] query_market_prices: {symbol}")
    return f"Price for {symbol}: $150.00"


def execute_market_trade(symbol: str, amount: int) -> str:
    """Execute a market buy order."""
    print(f"[Tool Executed] execute_market_trade: Buying {amount} shares of {symbol}")
    return f"Successfully bought {amount} shares of {symbol}"


async def main() -> None:
    kak_api_key = os.getenv("KAK_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not kak_api_key or not gemini_api_key:
        print("Error: Please set KAK_API_KEY and GEMINI_API_KEY environment variables.")
        sys.exit(1)

    print("Registering agent in Kakunin...")
    async with Kakunin(api_key=kak_api_key) as kakunin_client:
        agent_record = await kakunin_client.agents.create(
            name="Antigravity-Compliance-Trader",
            model="gemini-3.5-flash",
            version="1.0.0",
            model_hash="sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            metadata={"scopes": ["market.read", "trade.execute"]},
        )
        await kakunin_client.agents.certify(agent_record.id)
        
        # Configure Kakunin hooks
        hooks = get_kakunin_hooks(
            kakunin=kakunin_client,
            agent_id=agent_record.id,
            tool_scopes_mapping={
                "query_market_prices": ["market.read"],
                "execute_market_trade": ["trade.execute"],
            }
        )

        config = LocalAgentConfig(
            model="gemini-3.5-flash",
            system_instructions="You are a helpful stock trader with access to market tools.",
            tools=[query_market_prices, execute_market_trade],
            hooks=hooks,
        )

        print("\n--- Running Antigravity Agent (Safe Query) ---")
        async with Agent(config=config) as agent:
            try:
                res = await agent.chat("What is the price of GOOG?")
                print(f"Response: {res}")
            except ScopeViolationError as e:
                print(f"Blocked by Kakunin: {e}")

            print("\n--- Running Antigravity Agent (Execution Query) ---")
            try:
                res = await agent.chat("Buy 5 shares of GOOG")
                print(f"Response: {res}")
            except ScopeViolationError as e:
                print(f"Blocked by Kakunin: {e}")


if __name__ == "__main__":
    asyncio.run(main())
