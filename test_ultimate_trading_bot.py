import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from ultimate_trading_bot import TradingBot

@pytest.fixture
def bot():
    with patch('ultimate_trading_bot.TelegramClient'), \
         patch('ultimate_trading_bot.SolanaClient'), \
         patch('ultimate_trading_bot.requests.Session'), \
         patch('ultimate_trading_bot.ThreadPoolExecutor'), \
         patch('ultimate_trading_bot.TTLCache'), \
         patch.dict('os.environ', {'PUMPPORTAL_API_KEY': 'test_key'}):
        return TradingBot()

@pytest.mark.asyncio
async def test_create_token_and_buy_bundle_example_success(bot):
    with patch('ultimate_trading_bot.time.time', return_value=12345), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch.object(bot.session, 'post') as mock_post, \
         patch.object(bot, 'execute_bundled_trade', new_callable=AsyncMock, return_value=(True, ['sig1', 'sig2'])), \
         patch.object(bot, 'send_telegram_message', new_callable=AsyncMock) as mock_send_telegram_message:

        # Mock IPFS response
        mock_ipfs_response = MagicMock()
        mock_ipfs_response.json.return_value = {'metadataUri': 'ipfs://test_uri'}

        # Mock trade-local response
        mock_trade_local_response = MagicMock()
        mock_trade_local_response.json.return_value = ['tx1', 'tx2']

        # Make the mock_post awaitable
        async def awaitable_mock_post(*args, **kwargs):
            if mock_post.call_count == 1:
                return mock_ipfs_response
            return mock_trade_local_response

        mock_post.side_effect = awaitable_mock_post

        # Mock run_in_executor
        with patch.object(bot.executor, 'submit') as mock_submit:
            # Create a future to be returned by the mock
            future = asyncio.Future()
            future.set_result(mock_ipfs_response)
            mock_submit.return_value = future

            await bot.create_token_and_buy_bundle_example()

        assert 'placeholder_mint_address' in bot.holdings
        assert bot.holdings['placeholder_mint_address']['last_buy_signature'] == 'sig2'
