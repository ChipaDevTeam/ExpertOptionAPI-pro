"""Candles channel for subscribing to real-time candle data."""
import logging
from typing import Dict, List
from uuid import uuid4
from Expert.ws.channels.base import BaseChannel

class CandlesChannel(BaseChannel):
    """Channel for subscribing to real-time candle data."""
    
    def __init__(self, api):
        """Initialize the candles channel.
        
        Args:
            api: The ExpertOption API instance.
        """
        super().__init__(api)
        self.logger = logging.getLogger("CandlesChannel")
    
    async def __call__(self, asset_id: int, timeframes: List[int]) -> Dict:
        """Subscribe to candle data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
            timeframes: List of timeframes to subscribe to (e.g., [0, 5]).
        
        Returns:
            The candle data response.
        """
        payload = {
            "action": "subscribeCandles",
            "message": {
                "assetsIds": [asset_id],
                "timeframes": timeframes
            },
            "token": self.api.token,
            "ns": str(uuid4())
        }
        self.logger.debug(f"Sending candles subscription request: {payload}")
        await self.api.websocket_client.send(payload)
        response = await self.api.websocket_client.recv("candles", timeout=20.0)
        if response.get("action") == "error":
            self.logger.error(f"Received error response: {response}")
            raise ValueError(f"Server error: {response.get('message')}")
        self.logger.debug(f"Received candles response: {response}")
        return response