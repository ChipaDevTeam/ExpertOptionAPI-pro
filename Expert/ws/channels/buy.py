"""Buy channel for placing trading orders."""
import logging
import time
from typing import Dict, Any
from uuid import uuid4
from Expert.ws.channels.base import BaseChannel
from Expert.utils import validate_asset_id, validate_expiration_time

class BuyChannel(BaseChannel):
    """Channel for placing trading orders."""
    
    def __init__(self, api):
        """Initialize the buy channel.
        
        Args:
            api: The ExpertOption API instance.
        """
        super().__init__(api)
        self.logger = logging.getLogger("BuyChannel")
    
    async def __call__(self, asset_id: int, amount: float, direction: str, exp_time: int, is_demo: bool) -> Dict:
        """Place a trading order.
        
        Args:
            asset_id: The ID of the asset.
            amount: The investment amount.
            direction: The trade direction ("call" or "put").
            exp_time: The expiration time of the order.
            is_demo: True for demo mode, False for real trading.
        
        Returns:
            The response from the server.
        """
        payload = {
            "action": "expertOption",
            "message": {
                "options": [
                    {
                        "amount": amount,
                        "asset_id": asset_id,
                        "direction": direction,
                        "expired": exp_time,
                        "is_demo": 1 if is_demo else 0,
                        "strike_time": int(time.time())  # Use current time as fallback
                    }
                ]
            },
            "token": self.api.token,
            "ns": str(uuid4())
        }
        self.logger.debug(f"Sending buy request: {payload}")
        await self.api.websocket_client.send(payload)
        response = await self.api.websocket_client.recv("expertOption", timeout=20.0)
        self.logger.debug(f"Received buy response: {response}")
        return response