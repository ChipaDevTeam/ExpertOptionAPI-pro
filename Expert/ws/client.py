"""WebSocket client for the ExpertOption API."""
import asyncio
import logging
import websockets
import json
from typing import Dict, Optional
from Expert.exceptions import ConnectionError

class WebSocketClient:
    """WebSocket client for communicating with the ExpertOption server."""
    
    def __init__(self, api):
        """Initialize the WebSocket client.
        
        Args:
            api: The ExpertOption API instance.
        """
        self.api = api
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.logger = logging.getLogger("ExpertOptionWebSocketClient")
        self.message_queue: Dict[str, asyncio.Queue] = {}
        self.connected = False

    async def connect(self, uri: str):
        """Connect to the WebSocket server.
        
        Args:
            uri: The WebSocket server URI.
        
        Raises:
            ConnectionError: If the connection fails.
        """
        try:
            self.logger.info(f"Connecting to WebSocket server: {uri}")
            headers = {
                "Origin": "https://app.expertoption.com",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits"
            }
            self.websocket = await websockets.connect(uri, ping_interval=5, ping_timeout=20, extra_headers=headers)
            self.connected = True
            self.logger.info("WebSocket connection established successfully")
            asyncio.create_task(self._receive_messages())
        except Exception as e:
            self.logger.error(f"Failed to connect to WebSocket server: {str(e)}", exc_info=True)
            self.connected = False
            raise ConnectionError(f"Failed to connect to WebSocket server: {str(e)}")

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        try:
            if self.websocket and self.connected:
                await self.websocket.close()
                self.connected = False
                self.logger.info("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"Failed to disconnect from WebSocket server: {str(e)}", exc_info=True)

    async def send(self, payload: Dict):
        """Send a message to the WebSocket server.
        
        Args:
            payload: The message payload to send.
        
        Raises:
            ConnectionError: If not connected or sending fails.
        """
        try:
            if not self.connected or not self.websocket:
                raise ConnectionError("Not connected to WebSocket server")
            await self.websocket.send(json.dumps(payload))
            self.logger.debug(f"Sent message: {json.dumps(payload, indent=2)}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}", exc_info=True)
            raise ConnectionError(f"Failed to send message: {str(e)}")

    async def recv(self, action: str, timeout: float = 20.0) -> Dict:
        """Receive a message for a specific action.
        
        Args:
            action: The action to filter messages by.
            timeout: Maximum time to wait for the message.
        
        Returns:
            The received message.
        
        Raises:
            asyncio.TimeoutError: If no message is received within the timeout.
        """
        try:
            if action not in self.message_queue:
                self.message_queue[action] = asyncio.Queue()
            return await asyncio.wait_for(self.message_queue[action].get(), timeout=timeout)
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout waiting for message with action: {action}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to receive message for action {action}: {str(e)}", exc_info=True)
            raise

    async def _receive_messages(self):
        """Continuously receive messages from the WebSocket server."""
        try:
            while self.connected and self.websocket:
                message = await self.websocket.recv()
                try:
                    data = json.loads(message)
                    action = data.get("action")
                    ns = data.get("ns")
                    self.logger.debug(f"Received message: {json.dumps(data, indent=2)}")
                    
                    # Store profile and assets data
                    if action == "profile":
                        self.api.profile_data = data
                        self.logger.info(f"Stored profile data from multipleAction: {data}")
                    elif action == "assets":
                        self.api.assets_data = data
                        self.logger.info(f"Stored assets data from multipleAction: {data}")
                    
                    # Queue the message for specific action
                    if action in self.message_queue:
                        await self.message_queue[action].put(data)
                except json.JSONDecodeError:
                    self.logger.warning(f"Received non-JSON message: {message}")
                except Exception as e:
                    self.logger.error(f"Error processing received message: {str(e)}", exc_info=True)
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.warning(f"WebSocket connection closed: {str(e)}")
            self.connected = False
            await self.disconnect()
        except Exception as e:
            self.logger.error(f"Error in receiving messages: {str(e)}", exc_info=True)
            self.connected = False
            await self.disconnect()