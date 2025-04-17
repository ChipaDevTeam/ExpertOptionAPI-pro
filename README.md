# ExpertOptionAPI-pro
The latest version of ExpertOptionAPI created with alot of help of the Chipa Comunity

## ExpertOptionAPI Usage Guide

This README provides a full example of how to use the `ExpertOptionAPI` Python library along with the `AlligatorIndicator` and `RSIIndicator`.

## Features

- Connect to ExpertOption using WebSocket
- Fetch account balance and active trading assets
- Dynamically select high-profit assets
- Subscribe to live candle data
- Place and monitor trade orders
- Fetch historical candles
- Analyze market trends with indicators
- Get traders' choice sentiment

## Requirements

- Python 3.7+
- asyncio
- Logging
- `ExpertOptionAPI` and indicators module

## Installation

Make sure to install the necessary modules and have the `Expert.api` and `Expert.indicators` properly configured in your environment.

## Example

```python
import asyncio
import logging
from Expert.api import ExpertOptionAPI
from Expert.indicators import AlligatorIndicator, RSIIndicator

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def main():
    token = ""  # Replace with your token
    api = ExpertOptionAPI(token=token, demo=True, server_region="wss://fr24g1us.expertoption.finance/ws/v40")
    
    try:
        await api.connect()
        
        # Balance and asset info
        balance = api.get_balance()
        print(f"Account balance: {balance}")
        print(f"Active assets: {len(api.active_assets)}")
        
        # Select the most profitable asset
        selected_asset_id = 240
        available_assets = [
            (asset_id, asset["profit"]) 
            for asset_id, asset in api.active_assets.items() 
            if asset.get("is_active") == 1 and asset.get("type") == 1 and "profit" in asset
        ]
        if available_assets:
            selected_asset_id = max(available_assets, key=lambda x: x[1])[0]
            print(f"Selected: {api.active_assets[selected_asset_id]['name']} (ID: {selected_asset_id})")

        # Subscribe to candles
        await api.get_candles(selected_asset_id, timeframes=[0, 5])
        candle_data = api.candle_cache.get(selected_asset_id)
        print(f"Candles: {candle_data}")
        
        # Place an order
        order_id = await api.place_order(selected_asset_id, amount=1.0, direction="call")
        print(f"Order ID: {order_id}")
        order = await api.check_order_status(order_id)
        print(f"Order Status: {order.status}, Profit: {order.profit}")

        # Historical data and indicators
        periods = [[1744822016, 1744822726]]
        historical = await api.get_historical_candles(selected_asset_id, periods)

        alligator = AlligatorIndicator(historical)
        print(f"Alligator: {await alligator.evaluate_market_trend(api, selected_asset_id)}")

        rsi = RSIIndicator(historical)
        print(f"RSI: {rsi.evaluate_market_condition()}")

        # Traders choice
        choice = await api.get_traders_choice(selected_asset_id)
        print(f"Traders' Choice: {choice}")

    except Exception as e:
        print(f"Error: {e}")
        api.logger.error("Main execution failed", exc_info=True)
    finally:
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

## Notes

- Replace the token with a valid one from your ExpertOption account.
- The `AlligatorIndicator` and `RSIIndicator` rely on proper historical candle data.

---

Happy coding and profitable trading!
