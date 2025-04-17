import asyncio
import time
import logging
from Expert.api import ExpertOptionAPI

logger = logging.getLogger(__name__)

class Expert:
    def __init__(self, token: str, demo: bool = True):
        self.token = token
        self.demo = demo
        self.asset_map = {}
        self.api: ExpertOptionAPI = ExpertOptionAPI(token=token, demo=demo)

    async def connect(self):
        await self.api.connect()
        self.asset_map = self.api.get_assets_map()

        if not self.asset_map:
            raise Exception("Asset map is empty. Failed to fetch active assets. Please check token or connection.")

        print("Fetched Asset Map:")
        for symbol, asset_id in self.asset_map.items():
            print(f"{symbol} -> {asset_id}")

        return True

    async def get_balance(self):
        return self.api.get_balance()

    def get_assets(self):
        return self.asset_map

    def get_asset_id(self, symbol: str):
        return self.asset_map.get(symbol)

    def get_payout(self, symbol: str):
        asset_id = self.get_asset_id(symbol)
        return self.api.get_payout_by_asset(asset_id)

    async def get_candles(self, symbol: str, timeframes=[60]):
        asset_id = self.get_asset_id(symbol)
        if asset_id is None:
            raise ValueError(f"Symbol '{symbol}' is not found in active assets.")
        return await self.api.get_candles(asset_id, timeframes)

    async def buy(self, symbol: str, amount: float, direction: str = "call"):
        asset_id = self.get_asset_id(symbol)
        if asset_id is None:
            raise ValueError(f"Symbol '{symbol}' is not found in active assets.")
        return await self.api.place_order(asset_id, amount, direction)

    async def check_win(self, order_id: int):
        return await self.api.check_win(order_id)
