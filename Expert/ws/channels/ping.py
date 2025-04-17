"""Ping channel for maintaining WebSocket connection."""
import logging
from typing import Dict, Any
from uuid import uuid4
from Expert.ws.channels.base import BaseChannel

class PingChannel(BaseChannel):
    """Channel for sending ping requests to keep the connection alive."""
    
    def __init__(self, api):
        """Initialize the ping channel.
        
        Args:
            api: The ExpertOption API instance.
        """
        super().__init__(api)
        self.logger = logging.getLogger("PingChannel")
    
    async def send(self, api, message: Dict[str, Any]) -> Dict:
        """Send a ping request.
        
        Args:
            api: The ExpertOption API instance.
            message: The message payload for the ping request.
        
        Returns:
            The response from the server.
        """
        payload = {
            "action": "ping",
            "message": message,
            "token": api.token,
            "ns": str(uuid4())
        }
        self.logger.debug(f"Sending ping request: {payload}")
        await api.websocket_client.send(payload)
        response = await api.websocket_client.recv("ping", timeout=10.0)
        self.logger.debug(f"Received ping response: {response}")
        return response
    
    async def __call__(self):
        """Send a ping request with an empty message."""
        return await self.send(self.api, {})