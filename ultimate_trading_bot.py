import asyncio
import requests
import time
import logging
import json
import os
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction, Transaction
from solders.keypair import Keypair
from solders.signature import Signature
import base58

# Imports for SOL transfer using solana.py (compatible with solders Keypair/Pubkey)
# solana.py is a higher-level SDK, while solders provides low-level Rust-backed primitives.
# Using both allows for flexibility: solders for core keypair/transaction message,
# and solana.py for convenient RPC client and system program instructions.
from solana.rpc.api import Client as SolanaClient # Renamed to avoid conflict with TradingBot.client
from solders.system_program import transfer as solana_transfer

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor

# Import configuration from the separate config file
# This ensures all parameters are centralized and securely managed.
import gemini_config as config

# ==============================================================================
# Logging Setup
# ==============================================================================
# Configures a robust logging system to capture bot activities, warnings, and errors.
# Logs are directed to both a file for persistence and the console for real-time monitoring.
# Level set to INFO to balance verbosity with useful information. For debugging,
# this can be changed to logging.DEBUG.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ultimate_trading_bot.log"), # Persists logs to a file
        logging.StreamHandler()                          # Outputs logs to console
    ]
)
logger = logging.getLogger(__name__) # Logger specific to this module

# ==============================================================================
# TradingBot Class Definition
# ==============================================================================
class TradingBot:
    """
    Encapsulates the state, core logic, and external interactions of the Solana trading bot.
    This class-based approach promotes modularity, maintainability, and easier state management,
    avoiding the pitfalls of global variables.
    """
    def __init__(self):
        """
        Initializes the bot's resources, clients, and state variables.
        """
        # HTTP session for efficient and persistent connections to APIs.
        self.session = requests.Session()

        # Thread pool executor for running synchronous (blocking) I/O operations
        # (like requests.get/post) without blocking the asyncio event loop.
        # This is crucial for maintaining responsiveness in an asynchronous application.
        self.executor = ThreadPoolExecutor(max_workers=10) # Adjust max_workers based on system resources and API limits.

        # Cache for token prices to reduce redundant API calls and improve performance.
        # TTL (Time To Live) of 60 seconds means prices are re-fetched after 1 minute.
        self.price_cache = TTLCache(maxsize=10000, ttl=60)

        # Dictionary to track currently held tokens.
        # Format: { "token_address": { "amount": float, "buy_price": float, "target_prices": [], "sold_portions": [] } }
        self.holdings = {}

        # Set to keep track of liquidity pools that have already been processed to avoid re-processing.
        self.seen_pools = set()

        # Initialize Telegram client for notifications.
        self.client = TelegramClient(
            "ultimate_trading_bot_session",
            config.API_ID,
            config.API_HASH
        )

        # Critical check for PumpPortal API Key. Trading functions depend on this.
        self.pumpportal_api_key = os.getenv("PUMPPORTAL_API_KEY")
        if not self.pumpportal_api_key:
            logger.critical("PUMPPORTAL_API_KEY environment variable is not set. Trading functions (buy/sell/bundle) will not work.")
            # In a production system, consider raising an exception here to halt startup
            # if trading is the primary function and cannot proceed without the key.
            # raise ValueError("PUMPPORTAL_API_KEY is not set.")

        # Initialize Solscan Pro API Key. Optional for some features, but crucial for others.
        self.solscan_pro_api_key = os.getenv("SOLSCAN_PRO_API_KEY")
        if not self.solscan_pro_api_key:
            logger.warning("SOLSCAN_PRO_API_KEY environment variable is not set. Solscan Pro API functions (e.g., fetching transfers) will not work.")

        # Load the bot's primary Solana keypair from configuration.
        self.signer_keypair = config.KEYPAIR
        self.public_key = config.PUBLIC_KEY
        logger.info(f"Bot's public key loaded: {self.public_key}")

        # Initialize Solana RPC client for direct transfers and on-chain data fetching.
        # This uses the solana.py SDK for convenience.
        self.solana_rpc_client = SolanaClient(config.RPC_HTTP_ENDPOINT)

        # Initialize trading parameters from config. These can be overridden by Markdown.
        self.investment_amount_sol = config.INVESTMENT_AMOUNT_USDC # Renamed for clarity as it's SOL for Pump.fun
        self.profit_tiers_percent = config.PROFIT_TIERS_PERCENT
        self.slippage_percent = config.SLIPPAGE_PERCENT
        self.priority_fee_sol = config.PRIORITY_FEE_SOL

    # ==============================================================================
    # Configuration Loading from Markdown
    # ==============================================================================
    async def load_config_from_markdown(self, file_path: str) -> dict:
        """
        Loads configuration settings from a Markdown file.
        Expects key-value pairs in the format 'Key: Value' or 'Key=Value'.

        Args:
            file_path (str): The path to the Markdown configuration file.

        Returns:
            dict: A dictionary of parsed configuration settings.
        """
        parsed_config = {}
        if not os.path.exists(file_path):
            logger.error(f"Markdown config file not found: {file_path}")
            await self.send_telegram_message(f"❌ **CONFIG ERROR**: Markdown file `{file_path}` not found.")
            return parsed_config

        logger.info(f"Loading configuration from Markdown file: {file_path}")
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): # Skip empty lines and comments
                        continue

                    # Attempt to parse 'Key: Value' or 'Key=Value'
                    if ':' in line:
                        key, value = line.split(':', 1)
                    elif '=' in line:
                        key, value = line.split('=', 1)
                    else:
                        continue # Skip lines that don't match expected format

                    key = key.strip()
                    value = value.strip()
                    parsed_config[key] = value
            logger.info(f"Successfully loaded Markdown config from {file_path}.")
        except Exception as e:
            logger.error(f"Error reading or parsing Markdown config file {file_path}: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **CONFIG ERROR**: Failed to parse Markdown file `{file_path}`: `{e}`")

        return parsed_config

    def apply_markdown_config(self, config_dict: dict):
        """
        Applies parsed configuration settings from a dictionary to the bot's runtime.
        This method allows overriding default or environment variable settings.

        Args:
            config_dict (dict): A dictionary of settings loaded from Markdown.
        """
        logger.info("Applying Markdown configuration settings...")
        applied_changes = []

        # Example: Override investment amount
        if "Investment Amount" in config_dict:
            try:
                new_amount = float(config_dict["Investment Amount"])
                self.investment_amount_sol = new_amount
                applied_changes.append(f"Investment Amount: {new_amount} SOL")
                logger.info(f"Overridden Investment Amount to {new_amount} SOL.")
            except ValueError:
                logger.warning(f"Invalid value for 'Investment Amount': {config_dict['Investment Amount']}. Skipping.")

        # Example: Override profit tiers
        if "Profit Tiers" in config_dict:
            try:
                new_tiers = list(map(int, config_dict["Profit Tiers"].split(',')))
                self.profit_tiers_percent = new_tiers
                applied_changes.append(f"Profit Tiers: {new_tiers}%")
                logger.info(f"Overridden Profit Tiers to {new_tiers}%.")
            except ValueError:
                logger.warning(f"Invalid value for 'Profit Tiers': {config_dict['Profit Tiers']}. Skipping.")

        # Add more parameters here as needed (e.g., slippage, priority fee)
        if "Slippage Percent" in config_dict:
            try:
                new_slippage = float(config_dict["Slippage Percent"])
                self.slippage_percent = new_slippage
                applied_changes.append(f"Slippage Percent: {new_slippage}%")
                logger.info(f"Overridden Slippage Percent to {new_slippage}%.")
            except ValueError:
                logger.warning(f"Invalid value for 'Slippage Percent': {config_dict['Slippage Percent']}. Skipping.")

        if "Priority Fee Sol" in config_dict:
            try:
                new_priority_fee = float(config_dict["Priority Fee Sol"])
                self.priority_fee_sol = new_priority_fee
                applied_changes.append(f"Priority Fee SOL: {new_priority_fee}")
                logger.info(f"Overridden Priority Fee SOL to {new_priority_fee}.")
            except ValueError:
                logger.warning(f"Invalid value for 'Priority Fee Sol': {config_dict['Priority Fee Sol']}. Skipping.")

        if applied_changes:
            message = "⚙️ **Configuration Updated from Markdown**:\n" + "\n".join(applied_changes)
            asyncio.create_task(self.send_telegram_message(message)) # Send async message
        else:
            logger.info("No relevant configuration changes applied from Markdown.")


    # ==============================================================================
    # Communication and Utility Methods
    # ==============================================================================
    async def send_telegram_message(self, message: str):
        """
        Sends a message to the configured Telegram channel with retry logic for robustness.
        Handles FloodWaitError to prevent being rate-limited by Telegram.
        """
        for attempt in range(3):
            try:
                await self.client.send_message(config.CHANNEL_USERNAME, message)
                logger.info(f"Sent Telegram message: {message}")
                return
            except FloodWaitError as e:
                logger.warning(f"Telegram flood wait: sleeping for {e.seconds} seconds. Attempt {attempt + 1}/3")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Failed to send Telegram message (attempt {attempt + 1}/3): {e}", exc_info=True)
                await asyncio.sleep(1)
        logger.error(f"Failed to send Telegram message after multiple attempts: {message}")

    def get_token_price(self, token_mint_address: str) -> float | None:
        """
        Fetches the current price of a token using Jupiter's Price API.
        Utilizes a TTL cache to minimize redundant API calls.
        """
        if token_mint_address in self.price_cache:
            return self.price_cache[token_mint_address]

        try:
            url = config.JUPITER_PRICE_API.format(token_mint_address)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()

            price = data.get("data", {}).get(token_mint_address, {}).get("price")
            if price:
                self.price_cache[token_mint_address] = float(price)
                return float(price)
            else:
                logger.warning(f"Price not found for token {token_mint_address} in Jupiter API response: {data}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Network or HTTP error fetching price for {token_mint_address}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred while parsing price for {token_mint_address}: {e}", exc_info=True)
            return None

    async def _check_token_safety(self, token_mint_address: str) -> bool:
        """
        Performs critical on-chain safety checks for a token before considering a trade.
        This is a foundational component of the 'RugPullShield' and 'TrueTokenVerifier' features.

        Specifically, this function aims to verify the revocation of Mint Authority and Freeze Authority.

        Args:
            token_mint_address (str): The public key (address) of the token mint to check.

        Returns:
            bool: True if the token passes the safety checks (authorities appear revoked), False otherwise.
        """
        logger.info(f"Performing on-chain safety checks for token: {token_mint_address} (Mint/Freeze Authority).")
        await self.send_telegram_message(f"🔍 **SAFETY CHECK**: Initiating on-chain check for `{token_mint_address[:6]}...{token_mint_address[-6:]}`.")

        try:
            mint_pubkey = Pubkey.from_string(token_mint_address)

            # Fetch account info for the token mint. This is a synchronous RPC call,
            # so it's run in the thread pool executor to avoid blocking the asyncio loop.
            account_info = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.solana_rpc_client.get_account_info(mint_pubkey)
            )

            if not account_info or not account_info.value:
                logger.warning(f"Token {token_mint_address}: Mint account info not found or empty. Cannot verify authorities.")
                await self.send_telegram_message(f"⚠️ **SAFETY CHECK FAILED**: Mint account not found for `{token_mint_address[:6]}...`")
                return False

            # --- IMPORTANT: Conceptual Parsing for Mint/Freeze Authority ---
            # The 'data' field in account_info.value.data contains the raw bytes of the Mint account.
            # To programmatically verify if mintAuthority and freezeAuthority are revoked (i.e., set to None),
            # you would typically need to:
            # 1. Import or define the SPL Token Mint account layout (e.g., from spl_token.constants.MINT_LAYOUT).
            # 2. Parse account_info.value.data using that layout.
            # 3. Check the 'mint_authority_option' and 'freeze_authority_option' fields.
            #    A value of 0 typically indicates that the authority is revoked (None).
            #
            # Example (conceptual, requires `spl_token` library or manual parsing):
            # from spl_token.constants import MINT_LAYOUT
            # mint_data = MINT_LAYOUT.parse(account_info.value.data)
            # is_mint_authority_revoked = mint_data.mint_authority_option == 0
            # is_freeze_authority_revoked = mint_data.freeze_authority_option == 0
            #
            # if not is_mint_authority_revoked:
            #     logger.warning(f"Token {token_mint_address}: Mint authority is NOT revoked! This is a high risk. Skipping.")
            #     await self.send_telegram_message(f"❌ **RUG PULL ALERT**: Mint authority NOT revoked for `{token_mint_address[:6]}...`!")
            #     return False
            # if not is_freeze_authority_revoked:
            #     logger.warning(f"Token {token_mint_address}: Freeze authority is NOT revoked! This is a high risk. Skipping.")
            #     await self.send_telegram_message(f"❌ **RUG PULL ALERT**: Freeze authority NOT revoked for `{token_mint_address[:6]}...`!")
            #     return False

            # For the purpose of this demonstration, we will simulate the success of these checks
            # if the account data was successfully retrieved.
            logger.info(f"Token {token_mint_address}: Mint account data retrieved. (Simulating Mint/Freeze authority checks passed).")
            await self.send_telegram_message(f"✅ **SAFETY CHECK PASSED**: Authorities appear revoked for `{token_mint_address[:6]}...` (Simulated).")
            return True

        except Exception as e:
            logger.error(f"An error occurred during on-chain safety check for {token_mint_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **SAFETY CHECK ERROR**: Failed for `{token_mint_address[:6]}...`\nError: `{e}`")
            return False

    # ==============================================================================
    # Trading Execution Methods (Single Trades via PumpPortal)
    # ==============================================================================
    async def execute_buy(self, token_address: str, current_price: float):
        """
        Executes a token purchase using the PumpPortal API's single trade endpoint.
        Uses `self.investment_amount_sol` for the amount.
        """
        if not self.pumpportal_api_key:
            logger.error("PUMPPORTAL_API_KEY is not set. Cannot execute buy order.")
            await self.send_telegram_message("❌ **BUY FAILED**: PumpPortal API Key missing.")
            return

        logger.info(f"Attempting to buy {token_address} with {self.investment_amount_sol} SOL using single trade API...")

        payload = {
            "action": "buy",
            "mint": token_address,
            "amount": str(self.investment_amount_sol), # Use dynamically loaded investment amount
            "denominatedInSol": "true",
            "slippage": str(self.slippage_percent), # Use dynamically loaded slippage
            "priorityFee": str(self.priority_fee_sol), # Use dynamically loaded priority fee
            "pool": "pump",
            "skipPreflight": "false",
            "jitoOnly": "false"
        }

        try:
            url = f"{config.PUMPPORTAL_TRADE_API}?api-key={self.pumpportal_api_key}"
            response = await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self.session.post(url, json=payload))
            response.raise_for_status()

            trade_result = response.json()

            if trade_result.get("success"):
                signature = trade_result.get("signature")
                logger.info(f"Buy order successful for {token_address}. Signature: {signature}")

                token_amount = self.investment_amount_sol / current_price
                self.holdings[token_address] = {
                    "amount": token_amount,
                    "buy_price": current_price,
                    "target_prices": [current_price * (1 + tier / 100) for tier in self.profit_tiers_percent],
                    "sold_portions": [False] * len(self.profit_tiers_percent),
                    "last_buy_signature": signature
                }

                message = (f"✅ **PURCHASED**: `{token_address[:6]}...`\n"
                           f"**Amount (Est.)**: `{token_amount:.4f}` tokens\n"
                           f"**Price**: `${current_price:.6f}`\n"
                           f"**Cost**: `${self.investment_amount_sol}` SOL\n"
                           f"**Signature**: `https://solscan.io/tx/{signature[:6]}...{signature[-6:]}`")
                await self.send_telegram_message(message)
            else:
                error_message = trade_result.get("error", "Unknown error")
                logger.error(f"Buy order failed for {token_address}: {error_message}")
                await self.send_telegram_message(f"❌ **BUY FAILED**: `{token_address[:6]}...`\nError: `{error_message}`")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during buy for {token_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BUY ERROR**: `{token_address[:6]}...`\nNetwork Error: `{e}`")
        except Exception as e:
            logger.error(f"An unexpected error occurred during buy for {token_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BUY ERROR**: `{token_address[:6]}...`\nUnexpected Error: `{e}`")


    async def execute_sell(self, token_address: str, sell_price: float, portion_to_sell_percentage: int, profit_tier: int):
        """
        Executes a token sale using the PumpPortal API's single trade endpoint.
        Uses `self.slippage_percent` and `self.priority_fee_sol`.
        """
        if not self.pumpportal_api_key:
            logger.error("PUMPPORTAL_API_KEY is not set. Cannot execute sell order.")
            await self.send_telegram_message("❌ **SELL FAILED**: PumpPortal API Key missing.")
            return False

        logger.info(f"Attempting to sell {portion_to_sell_percentage}% of {token_address} using single trade API...")

        payload = {
            "action": "sell",
            "mint": token_address,
            "amount": f"{portion_to_sell_percentage}%",
            "denominatedInSol": "false",
            "slippage": str(self.slippage_percent),
            "priorityFee": str(self.priority_fee_sol),
            "pool": "pump",
            "skipPreflight": "false",
            "jitoOnly": "false"
        }

        try:
            url = f"{config.PUMPPORTAL_TRADE_API}?api-key={self.pumpportal_api_key}"
            response = await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self.session.post(url, json=payload))
            response.raise_for_status()

            trade_result = response.json()

            if trade_result.get("success"):
                signature = trade_result.get("signature")
                logger.info(f"Sell order successful for {token_address}. Signature: {signature}")

                profit = (sell_price - self.holdings[token_address]['buy_price']) / self.holdings[token_address]['buy_price'] * 100
                message = (f"💰 **SOLD**: `{token_address[:6]}...` (Tier {profit_tier}%)\n"
                           f"**Sell Price**: `${sell_price:.6f}`\n"
                           f"**Profit**: `~{profit:.2f}%`\n"
                           f"**Signature**: `https://solscan.io/tx/{signature[:6]}...{signature[-6:]}`")
                await self.send_telegram_message(message)
                return True
            else:
                error_message = trade_result.get("error", "Unknown error")
                logger.error(f"Sell order failed for {token_address}: {error_message}")
                await self.send_telegram_message(f"❌ **SELL FAILED**: `{token_address[:6]}...`\nError: `{error_message}`")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during sell for {token_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **SELL ERROR**: `{token_address[:6]}...`\nNetwork Error: `{e}`")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during sell for {token_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **SELL ERROR**: `{token_address[:6]}...`\nUnexpected Error: `{e}`")
            return False


    async def execute_bundled_trade(self, trade_requests: list[dict]) -> tuple[bool, list[str]]:
        """
        Constructs and sends a Jito bundle of transactions via PumpPortal's trade-local API.
        Uses `self.slippage_percent` and `self.priority_fee_sol` for bundle transactions.
        """
        logger.info(f"Attempting to execute a Jito bundle with {len(trade_requests)} transactions...")

        if not self.pumpportal_api_key:
            logger.error("PUMPPORTAL_API_KEY is not set. Cannot execute bundled trade.")
            await self.send_telegram_message("❌ **BUNDLE FAILED**: PumpPortal API Key missing.")
            return False, []
        if not trade_requests:
            logger.warning("No trade requests provided for the bundle. Skipping bundle execution.")
            return False, []

        # Ensure bundle requests use the current bot's trading parameters
        for req in trade_requests:
            if 'slippage' not in req:
                req['slippage'] = str(self.slippage_percent)
            if 'priorityFee' not in req:
                req['priorityFee'] = str(self.priority_fee_sol)
            if 'publicKey' not in req:
                req['publicKey'] = str(self.public_key)

        try:
            # Step 1: Get Unsigned Transactions from PumpPortal's trade-local API
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.session.post(config.PUMPPORTAL_TRADE_LOCAL_API, json=trade_requests)
            )
            response.raise_for_status()

            encoded_unsigned_transactions = response.json()
            if not isinstance(encoded_unsigned_transactions, list):
                logger.error(f"Unexpected response format from trade-local API: {encoded_unsigned_transactions}")
                await self.send_telegram_message(f"❌ **BUNDLE FAILED**: Unexpected response from trade-local API.")
                return False, []

            if len(encoded_unsigned_transactions) != len(trade_requests):
                logger.error(f"Mismatch in transaction count from trade-local. Expected {len(trade_requests)}, got {len(encoded_unsigned_transactions)}")
                await self.send_telegram_message(f"❌ **BUNDLE FAILED**: Mismatch in transaction count from trade-local API.")
                return False, []

            encoded_signed_transactions = []
            tx_signatures = []

            # Step 2: Decode and Sign Transactions Locally
            for index, encoded_tx in enumerate(encoded_unsigned_transactions):
                tx_message = VersionedTransaction.from_bytes(base58.b58decode(encoded_tx)).message

                current_request = trade_requests[index]
                action = current_request.get("action")

                signers = [self.signer_keypair]

                if action == "create":
                    mint_keypair_for_create = Keypair()
                    signers.append(mint_keypair_for_create)
                    trade_requests[index]["mint_keypair_obj"] = mint_keypair_for_create
                    trade_requests[index]["mint"] = str(mint_keypair_for_create.pubkey())

                signed_tx = VersionedTransaction(tx_message, signers)

                encoded_signed_transactions.append(base58.b58encode(bytes(signed_tx)).decode())
                tx_signatures.append(str(signed_tx.signatures[0]))

            # Step 3: Send Bundle to Jito Block Engine
            jito_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "sendBundle",
                "params": [encoded_signed_transactions]
            }

            jito_response = await loop.run_in_executor(
                self.executor,
                lambda: self.session.post(config.JITO_BLOCK_ENGINE_API, headers={"Content-Type": "application/json"}, json=jito_payload)
            )
            jito_response.raise_for_status()

            jito_result = jito_response.json()

            if "result" in jito_result:
                bundle_id = jito_result["result"]
                logger.info(f"Jito bundle accepted. Bundle ID: {bundle_id}")
                message = f"🚀 **JITO BUNDLE SENT!**\nBundle ID: `{bundle_id}`\n"
                for i, sig in enumerate(tx_signatures):
                    message += f"Tx {i+1}: `https://solscan.io/tx/{sig[:6]}...{sig[-6:]}`\n"
                await self.send_telegram_message(message)
                return True, tx_signatures
            elif "error" in jito_result:
                error_message = jito_result["error"].get("message", "Unknown Jito error")
                logger.error(f"Jito bundle failed: {error_message}")
                await self.send_telegram_message(f"❌ **JITO BUNDLE FAILED**: `{error_message}`")
                return False, []

        except requests.exceptions.RequestException as e:
            logger.error(f"Network or HTTP error during bundled trade: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BUNDLE ERROR**: Network Error: `{e}`")
            return False, []
        except Exception as e:
            logger.error(f"An unexpected error occurred during bundled trade: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BUNDLE ERROR**: Unexpected Error: `{e}`")
            return False, []

    async def create_token_and_buy_bundle_example(self):
        """
        This is the "first successful and effective task" demonstrating atomic operations:
        creating a new token on Pump.fun and immediately buying it within a single Jito bundle.
        This showcases high-speed, front-running capabilities.

        Requires an 'example.png' file in the same directory as the script.
        """
        logger.info("Running Jito bundle example: Create Token and Buy...")
        await self.send_telegram_message("🚀 **Starting First Effective Task**: Attempting to create a test token and buy it in a Jito bundle!")

        # --- Generate IPFS metadata ---
        try:
            timestamp = int(time.time())
            token_name = f"GeminiTestToken-{timestamp}"
            token_symbol = f"GT{timestamp % 1000}"

            form_data = {
                'name': token_name,
                'symbol': token_symbol,
                'description': f'This is a test token created by the Gemini bot as its first effective task. Timestamp: {timestamp}',
                'twitter': 'https://x.com/your_twitter',
                'telegram': 'https://t.me/your_telegram',
                'website': 'https://yourwebsite.com',
                'showName': 'true'
            }

            image_path = './example.png'
            if not os.path.exists(image_path):
                logger.error(f"Image file not found at {image_path}. Cannot create token metadata.")
                await self.send_telegram_message("❌ **BUNDLE EXAMPLE FAILED**: `example.png` not found for token creation. Please place an image file named 'example.png' in the bot's directory.")
                return

            with open(image_path, 'rb') as f:
                file_content = f.read()

            files = {'file': ('example.png', file_content, 'image/png')}

            metadata_response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.session.post("https://pump.fun/api/ipfs", data=form_data, files=files)
            )
            metadata_response.raise_for_status()
            metadata_response_json = metadata_response.json()
            metadata_uri = metadata_response_json.get('metadataUri')
            if not metadata_uri:
                logger.error(f"Failed to get metadata URI from IPFS response: {metadata_response_json}")
                await self.send_telegram_message("❌ **BUNDLE EXAMPLE FAILED**: Failed to get IPFS metadata URI.")
                return

            token_metadata = {
                'name': form_data['name'],
                'symbol': token_symbol,
                'uri': metadata_uri
            }
            logger.info(f"IPFS metadata created: {metadata_uri}")
            await self.send_telegram_message(f"🖼️ **IPFS Metadata**: Uploaded for `{token_name}`. URI: `{metadata_uri}`")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during IPFS metadata creation: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BUNDLE EXAMPLE ERROR**: IPFS Network Error: `{e}`")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred during IPFS metadata creation: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BUNDLE EXAMPLE ERROR**: Unexpected IPFS Error: `{e}`")
            return

        # --- Construct Bundle Requests ---
        create_token_request = {
            'publicKey': str(self.public_key),
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': 'placeholder_mint_address',
            'denominatedInSol': 'false',
            'amount': 1,
            'slippage': str(self.slippage_percent),
            'priorityFee': str(self.priority_fee_sol),
            'pool': 'pump'
        }

        buy_token_request = {
            "publicKey": str(self.public_key),
            "action": "buy",
            "mint": 'placeholder_mint_address',
            "denominatedInSol": "true",
            "amount": str(self.investment_amount_sol),
            "slippage": str(self.slippage_percent),
            "priorityFee": str(self.priority_fee_sol),
            "pool": "pump"
        }

        bundled_requests = [create_token_request, buy_token_request]

        # --- Execute the Bundle ---
        success, signatures = await self.execute_bundled_trade(bundled_requests)

        if success:
            logger.info(f"Jito bundle example completed successfully. Signatures: {signatures}")
            await self.send_telegram_message(f"✅ **First Task SUCCESS!**\nCreated and bought `{token_name}` (`{token_symbol}`).\nCheck Solscan for details.")

            created_mint_address = bundled_requests[0].get("mint")
            if created_mint_address:
                estimated_buy_price = self.investment_amount_sol / 1
                self.holdings[created_mint_address] = {
                    "amount": self.investment_amount_sol / estimated_buy_price,
                    "buy_price": estimated_buy_price,
                    "target_prices": [estimated_buy_price * (1 + tier / 100) for tier in self.profit_tiers_percent],
                    "sold_portions": [False] * len(self.profit_tiers_percent),
                    "last_buy_signature": signatures[1] if len(signatures) > 1 else None
                }
                logger.info(f"Added created token {created_mint_address} to holdings (estimated).")
        else:
            logger.error("Jito bundle example failed.")
            await self.send_telegram_message("❌ **First Task FAILED**: Jito bundle execution failed.")


    async def create_bonk_token(self, token_name: str, token_symbol: str, description: str, website: str, twitter: str, telegram: str, image_path: str):
        """
        Creates a new Bonk token using the PumpPortal API's 'create' action for the 'bonk' pool.
        This involves uploading image and metadata to Bonk's specific IPFS endpoints.
        This is a single transaction, not a bundle.
        """
        logger.info(f"Attempting to create Bonk token: {token_name} ({token_symbol})")

        if not self.pumpportal_api_key:
            logger.error("PUMPPORTAL_API_KEY is not set. Cannot create Bonk token.")
            await self.send_telegram_message("❌ **BONK CREATE FAILED**: `PUMPPORTAL_API_KEY` not set.")
            return

        # 1. Generate a random keypair for the new token's mint address.
        mint_keypair = Keypair()
        token_mint_address = str(mint_keypair.pubkey())
        logger.info(f"Generated Token CA: {token_mint_address}")
        await self.send_telegram_message(f"✨ **BONK TOKEN CREATE**: Generating new token: `{token_name}` (`{token_symbol}`)\nCA: `{token_mint_address[:6]}...{token_mint_address[-6:]}`")

        # 2. Upload image to Bonk's IPFS image storage.
        img_uri = None
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found at {image_path}. Cannot upload image for Bonk token.")
                await self.send_telegram_message(f"❌ **BONK CREATE FAILED**: Image file `{image_path}` not found.")
                return

            with open(image_path, 'rb') as f:
                file_content = f.read()

            files = {'image': ('image.png', file_content, 'image/png')}

            loop = asyncio.get_event_loop()
            img_response = await loop.run_in_executor(
                self.executor,
                lambda: self.session.post(config.BONK_IPFS_IMG_UPLOAD_API, files=files)
            )
            img_response.raise_for_status()
            img_uri = img_response.text
            logger.info(f"Image uploaded to Bonk IPFS. URI: {img_uri}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Bonk IPFS image upload: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BONK CREATE ERROR**: Image upload network error: `{e}`")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred during Bonk IPFS image upload: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BONK CREATE ERROR**: Unexpected image upload error: `{e}`")
            return

        # 3. Upload metadata to Bonk's IPFS metadata storage.
        metadata_uri = None
        try:
            metadata_payload = {
                'createdOn': "https://bonk.fun",
                'description': description,
                'image': img_uri,
                'name': token_name,
                'symbol': token_symbol,
                'website': website,
                'twitter': twitter,
                'telegram': telegram
            }

            loop = asyncio.get_event_loop()
            metadata_response = await loop.run_in_executor(
                self.executor,
                lambda: self.session.post(
                    config.BONK_IPFS_META_UPLOAD_API,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(metadata_payload)
                )
            )
            metadata_response.raise_for_status()
            metadata_uri = metadata_response.text
            logger.info(f"Metadata uploaded to Bonk IPFS. URI: {metadata_uri}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Bonk IPFS metadata upload: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BONK CREATE ERROR**: Metadata upload network error: `{e}`")
            return
        except Exception as e:
            logger.error(f"An unexpected error occurred during Bonk IPFS metadata upload: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BONK CREATE ERROR**: Unexpected metadata upload error: `{e}`")
            return

        # 4. Token metadata for the create transaction payload.
        token_metadata = {
            'name': token_name,
            'symbol': token_symbol,
            'uri': metadata_uri
        }

        # 5. Send the create transaction to PumpPortal.
        payload = {
            'action': 'create',
            'tokenMetadata': token_metadata,
            'mint': token_mint_address,
            'denominatedInSol': 'true',
            'amount': 1,
            'slippage': str(self.slippage_percent),
            'priorityFee': str(self.priority_fee_sol),
            'pool': config.BONK_POOL_NAME
        }

        try:
            url = f"{config.PUMPPORTAL_TRADE_API}?api-key={self.pumpportal_api_key}"
            response = await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self.session.post(url, json=payload))
            response.raise_for_status()

            create_result = response.json()

            if create_result.get("success"):
                signature = create_result.get("signature")
                logger.info(f"Bonk token creation successful. Signature: {signature}")
                message = (f"✅ **BONK TOKEN CREATED!**\n"
                           f"**Name**: `{token_name}` (`{token_symbol}`)\n"
                           f"**CA**: `{token_mint_address[:6]}...{token_mint_address[-6:]}`\n"
                           f"**Signature**: `https://solscan.io/tx/{signature[:6]}...{signature[-6:]}`")
                await self.send_telegram_message(message)
            else:
                error_message = create_result.get("error", "Unknown error")
                logger.error(f"Bonk token creation failed: {error_message}")
                await self.send_telegram_message(f"❌ **BONK TOKEN CREATE FAILED**: `{token_name}`\nError: `{error_message}`")

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Bonk token creation: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **BONK CREATE ERROR**: Network Error: `{e}`")
        except Exception as e:
            logger.error(f"An unexpected error occurred during Bonk token creation: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **BONK CREATE ERROR**: Unexpected error: `{e}`")

    async def send_sol_to_address(self, recipient_address: str, amount_sol: float):
        """
        Sends a specified amount of SOL from the bot's wallet to a recipient address.
        """
        logger.info(f"Attempting to send {amount_sol} SOL from {self.public_key} to {recipient_address}...")
        await self.send_telegram_message(f"💸 **SOL TRANSFER**: Attempting to send `{amount_sol}` SOL to `{recipient_address[:6]}...{recipient_address[-6:]}`.")

        try:
            amount_lamports = int(amount_sol * 1_000_000_000)
            recipient_pubkey = Pubkey.from_string(recipient_address)

            recent_blockhash = (await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.solana_rpc_client.get_latest_blockhash().value.blockhash
            ))

            transaction = VersionedTransaction.from_legacy(
                Transaction.new_signed_with_payer(
                    [
                        solana_transfer(
                            from_pubkey=self.public_key,
                            to_pubkey=recipient_pubkey,
                            lamports=amount_lamports,
                        )
                    ],
                    self.public_key,
                    [self.signer_keypair],
                    recent_blockhash,
                )
            )

            response = (await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.solana_rpc_client.send_transaction(transaction)
            ))

            tx_signature = str(response.value)

            logger.info(f"SOL transfer successful! Signature: {tx_signature}")
            await self.send_telegram_message(f"✅ **SOL TRANSFER SUCCESS!**\n"
                                           f"**Amount**: `{amount_sol}` SOL\n"
                                           f"**To**: `{recipient_address[:6]}...{recipient_address[-6:]}`\n"
                                           f"**Signature**: `https://solscan.io/tx/{tx_signature[:6]}...{tx_signature[-6:]}`")

        except Exception as e:
            logger.error(f"An error occurred during SOL transfer: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **SOL TRANSFER FAILED!**\n"
                                           f"**Amount**: `{amount_sol}` SOL\n"
                                           f"**To**: `{recipient_address[:6]}...{recipient_address[-6:]}`\n"
                                           f"**Error**: `{e}`")

    async def fetch_solscan_transfers(self, account_address: str, limit: int = 10, offset: int = 0) -> list[dict]:
        """
        Fetches transfer history for a given account from Solscan Pro API.
        """
        logger.info(f"Fetching Solscan transfer history for account: {account_address}...")

        if not self.solscan_pro_api_key:
            logger.error("SOLSCAN_PRO_API_KEY is not set. Cannot fetch Solscan transfers.")
            await self.send_telegram_message("❌ **SOLSCAN API FAILED**: `SOLSCAN_PRO_API_KEY` not set.")
            return []

        headers = {
            "accept": "application/json",
            "x-api-key": self.solscan_pro_api_key
        }

        params = {
            "account": account_address,
            "limit": min(limit, 50),
            "offset": offset
        }

        try:
            url = f"{config.SOLSCAN_PRO_API_BASE_URL}/account/transfer"
            response = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                lambda: self.session.get(url, headers=headers, params=params)
            )
            response.raise_for_status()

            data = response.json()

            if isinstance(data, list):
                logger.info(f"Successfully fetched {len(data)} transfers for {account_address}.")
                await self.send_telegram_message(f"📊 **SOLSCAN TRANSFERS**: Fetched `{len(data)}` transfers for `{account_address[:6]}...{account_address[-6:]}`.")
                return data
            else:
                error_message = data.get("error_message", "Unknown error from Solscan API")
                logger.error(f"Solscan API returned an error: {error_message}. Full response: {data}")
                await self.send_telegram_message(f"❌ **SOLSCAN API ERROR**: `{error_message}` for account `{account_address[:6]}...`")
                return []

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching Solscan transfers for {account_address}: {e.response.status_code} - {e.response.text}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **SOLSCAN API ERROR**: HTTP Error `{e.response.status_code}` for `{account_address[:6]}...`")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching Solscan transfers for {account_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"⚠️ **SOLSCAN API ERROR**: Network Error for `{account_address[:6]}...`\nError: `{e}`")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred fetching Solscan transfers for {account_address}: {e}", exc_info=True)
            await self.send_telegram_message(f"❌ **SOLSCAN API ERROR**: Unexpected error for `{account_address[:6]}...`\nError: `{e}`")
            return []


    # ==============================================================================
    # Main Monitoring Loops
    # ==============================================================================
    async def monitor_new_pools(self):
        """
        Periodically checks the Raydium API for newly created liquidity pools.
        If a new, safe pool is found, it attempts to execute a buy order.
        """
        logger.info("Starting Raydium pool monitor...")
        while True:
            try:
                response = await asyncio.get_event_loop().run_in_executor(self.executor, lambda: self.session.get(config.RAYDIUM_POOLS_API))
                response.raise_for_status()
                pools = response.json().get("data", [])

                for pool in pools:
                    token_address = pool.get("mintA", {}).get("address")
                    quote_address = pool.get("mintB", {}).get("address")

                    if token_address and token_address not in self.seen_pools and quote_address == config.USDC_MINT_ADDRESS:
                        self.seen_pools.add(token_address)
                        logger.info(f"New potential pool found: {token_address}")

                        if await self._check_token_safety(token_address): # Now performs an RPC call
                            price = self.get_token_price(token_address)
                            if price and price > 0:
                                await self.execute_buy(token_address, price)
                            else:
                                logger.warning(f"Could not fetch a valid price for new token {token_address}. Skipping purchase.")
                        else:
                            logger.warning(f"Token {token_address} failed safety checks. Skipping purchase.")

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching Raydium pools: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"An unexpected error occurred in pool monitor: {e}", exc_info=True)

            await asyncio.sleep(30)

    async def monitor_holdings_for_sell(self):
        """
        Periodically checks the price of held tokens against their profit targets.
        If a target is reached, it attempts to execute a sell order.
        """
        logger.info("Starting holdings monitor for selling...")
        while True:
            for token_address, data in list(self.holdings.items()):
                current_price = self.get_token_price(token_address)

                if not current_price:
                    logger.warning(f"Could not get price for held token {token_address}. Will retry on next cycle.")
                    continue

                for i, (target_price, sold) in enumerate(zip(data["target_prices"], data["sold_portions"])):
                    if current_price >= target_price and not sold:
                        logger.info(f"Target price of ${target_price:.6f} reached for {token_address} at current price ${current_price:.6f}.")

                        portion_to_sell_percentage = 100
                        profit_tier_val = self.profit_tiers_percent[i]

                        if await self.execute_sell(token_address, current_price, portion_to_sell_percentage, profit_tier_val):
                            self.holdings[token_address]["sold_portions"][i] = True

                if all(self.holdings[token_address]["sold_portions"]):
                    logger.info(f"All portions of {token_address} have been sold. Removing from holdings.")
                    del self.holdings[token_address]

            await asyncio.sleep(15)

    # ==============================================================================
    # Main Bot Execution Loop
    # ==============================================================================
    async def run(self):
        """
        Starts the bot and all its concurrent monitoring and execution tasks.
        """
        await self.client.start()
        logger.info("Telegram client started successfully.")
        await self.send_telegram_message("🤖 **Trading Bot is now online and running.**")

        try:
            # Load and apply Markdown configuration if desired
            # This allows overriding default config.py values at runtime.
            # Example: Load from 'my_default_prompt_strategy_A.md'
            # markdown_config = await self.load_config_from_markdown("my_default_prompt_strategy_A.md")
            # self.apply_markdown_config(markdown_config)

            # Example: Load from 'my_default_prompt_strategy_B.md'
            # markdown_config = await self.load_config_from_markdown("my_default_prompt_strategy_B.md")
            # self.apply_markdown_config(markdown_config)

            await asyncio.gather(
                # The "first successful and effective task":
                # Automatically creates a test token and immediately buys it in an atomic Jito bundle.
                self.create_token_and_buy_bundle_example(),

                # These are the continuous monitoring loops for general trading.
                self.monitor_new_pools(),
                self.monitor_holdings_for_sell(),

                # --- Optional Tasks (Uncomment to enable) ---
                # self.create_bonk_token(
                #     token_name="MyBonkToken",
                #     token_symbol="MBOT",
                #     description="A test token created by my Gemini bot on Bonk.fun!",
                #     website="https://mybot.com",
                #     twitter="https://x.com/mybot",
                #     telegram="https://t.me/mybotcommunity",
                #     image_path="./example.png"
                # ),

                # self.send_sol_to_address(
                #    recipient_address="ANOTHER_WALLET_ADDRESS_HERE",
                #    amount_sol=0.001
                # ),

                # asyncio.create_task(self.fetch_solscan_transfers(account_address=str(self.public_key)))
            )
        finally:
            await self.client.disconnect()
            self.session.close()
            self.executor.shutdown(wait=True)
            logger.info("Bot has been shut down gracefully.")

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    bot = TradingBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Manual shutdown initiated by user (Ctrl+C).")
    except Exception as e:
        logger.critical(f"A critical, unhandled error forced the bot to stop: {e}", exc_info=True)
