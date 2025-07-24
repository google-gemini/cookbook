import os
from solders.keypair import Keypair

# ==============================================================================
# Solana Configuration
# ==============================================================================
# This section configures the Solana connection and wallet details.

# Your Solana RPC endpoint.
# Using a private RPC is recommended for reliability and performance.
# You can obtain one from providers like Helius, QuickNode, or Alchemy.
RPC_HTTP_ENDPOINT = "https://api.mainnet-beta.solana.com"

# Your wallet's private key.
# It is strongly recommended to use environment variables for security.
# Example: os.getenv("PRIVATE_KEY")
# The private key should be in base58 encoded string format.
# To get your private key string:
# 1. If you have a phantom wallet export your private key (NOT the seed phrase).
# 2. Use a script to convert the byte array to a base58 string.
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "YOUR_PRIVATE_KEY_HERE")

# The public key of your wallet, derived from the private key.
# This is used for display and verification purposes.
try:
    KEYPAIR = Keypair.from_base58_string(PRIVATE_KEY)
    PUBLIC_KEY = KEYPAIR.pubkey()
except Exception as e:
    print(f"Error loading keypair from private key: {e}")
    print("Please ensure your PRIVATE_KEY is a valid base58 encoded string.")
    KEYPAIR = None
    PUBLIC_KEY = None

# The mint address of the quote currency (the currency you are trading against).
# For most pairs on Raydium/Solana, this is USDC.
USDC_MINT_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

# ==============================================================================
# Telegram Bot Configuration
# ==============================================================================
# This section configures the Telegram client for sending notifications.
# You need to create a Telegram application to get your API_ID and API_HASH.
# 1. Go to https://my.telegram.org and log in.
# 2. Click on "API development tools" and create a new application.
# It is recommended to store these as environment variables.
API_ID = int(os.getenv("TELEGRAM_API_ID", 1234567))  # Replace with your API ID
API_HASH = os.getenv("TELEGRAM_API_HASH", "YOUR_API_HASH_HERE")

# The username of the Telegram channel where you want to receive notifications.
# Example: "@my_trading_bot_channel"
CHANNEL_USERNAME = os.getenv("TELEGRAM_CHANNEL_USERNAME", "@YourChannelName")

# ==============================================================================
# Trading Parameters
# ==============================================================================
# This section defines the core parameters for your trading strategy.

# The amount of SOL to invest in each new token purchase.
# Example: 0.01 for a small test trade.
INVESTMENT_AMOUNT_USDC = 0.01  # For Pump.fun, this is in SOL

# Profit-taking tiers. The bot will sell portions of the token at these profit percentages.
# Example: [100, 200, 300] means sell at 100%, 200%, and 300% profit.
# The bot will sell an equal portion at each tier. For the example above, it would be 33.3% of the holdings at each tier.
PROFIT_TIERS_PERCENT = [100, 200, 300]

# The maximum slippage percentage you are willing to tolerate for trades.
# Slippage is the difference between the expected price and the actual price of a trade.
# A value of 5 means 5% slippage is allowed.
SLIPPAGE_PERCENT = 5

# The priority fee to use for transactions, in SOL.
# This helps your transactions get processed faster by the network.
# A higher fee can be crucial for time-sensitive trades like new token launches.
# Example: 0.0001 SOL
PRIORITY_FEE_SOL = 0.0001

# ==============================================================================
# API Endpoints
# ==============================================================================
# This section contains the URLs for the various APIs the bot interacts with.

# Raydium API to fetch newly created liquidity pools.
RAYDIUM_POOLS_API = "https://api.raydium.io/v2/sdk/liquidity/mainnet.json"

# Jupiter Price API for fetching token prices.
# The {0} will be replaced with the token's mint address.
JUPITER_PRICE_API = "https://price.jup.ag/v4/price?ids={0}"

# PumpPortal API endpoints for executing trades and creating tokens.
# Requires a PumpPortal API Key, which should be set as an environment variable.
PUMPPORTAL_TRADE_API = "https://pumpportal.io/api/trade"
PUMPPORTAL_TRADE_LOCAL_API = "https://pumpportal.io/api/trade-local"

# Jito Block Engine API for sending bundled transactions.
# This is used for atomic operations like creating and buying a token simultaneously.
JITO_BLOCK_ENGINE_API = "https://mainnet.block-engine.jito.wtf/api/v1/bundles"

# Bonk.fun specific API endpoints for creating tokens on their platform.
BONK_POOL_NAME = "bonk"
BONK_IPFS_IMG_UPLOAD_API = "https://bonk.fun/api/ipfs/image"
BONK_IPFS_META_UPLOAD_API = "https://bonk.fun/api/ipfs/metadata"

# Solscan Pro API for fetching detailed account information like transfer history.
# Requires a Solscan Pro API Key, set as an environment variable.
SOLSCAN_PRO_API_BASE_URL = "https://pro-api.solscan.io/v1.0"
