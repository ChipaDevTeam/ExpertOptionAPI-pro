"""Channel for authenticating with the ExpertOption server."""
from Expert.ws.channels.base import BaseChannel
from uuid import uuid4

class AuthenticateChannel(BaseChannel):
    """Channel for authenticating with the ExpertOption server."""
    
    async def __call__(self) -> dict:
        """Authenticate with the server using the provided token.
        
        Returns:
            The server response containing authentication details.
        """
        payload = {
            "action": "authenticate",
            "message": {
                "token": self.api.token
            },
            "ns": str(uuid4())
        }
        self.logger.debug(f"Sending authentication request: {payload}")
        await self.api.websocket_client.send(payload)
        
        response = await self.api.websocket_client.recv("authenticate", timeout=20.0)
        self.logger.debug(f"Received authentication response: {response}")
        return response