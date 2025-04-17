"""Main API class for the ExpertOption API."""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional
from uuid import uuid4
from Expert.ws.client import WebSocketClient
from Expert.ws.channels.authenticate import AuthenticateChannel
from Expert.ws.channels.ping import PingChannel
from Expert.ws.channels.candles import CandlesChannel
from Expert.ws.channels.buy import BuyChannel
from Expert.ws.channels.history import HistoryChannel
from Expert.ws.channels.traders_choice import TradersChoiceChannel
from Expert.ws.objects.profile import Profile
from Expert.ws.objects.candles import Candles
from Expert.ws.objects.order import Order
from Expert.constants import get_asset_id, get_asset_symbol, get_available_regions, get_default_multiple_action
from Expert.utils import validate_asset_id, validate_symbol, get_next_expiration_time
from Expert.exceptions import (
    ConnectionError, InvalidAssetError, InvalidExpirationTimeError,
    OrderPlacementError, DataFetchError
)

class ExpertOptionAPI:
    """Main API class for interacting with the ExpertOption server."""
    
    def __init__(self, token: str, demo: bool = True, server_region: str = "wss://fr24g1us.expertoption.finance/ws/v40"):
        """Initialize the API client.
        
        Args:
            token: Authentication token for the ExpertOption server.
            demo: True for demo mode, False for real trading.
            server_region: WebSocket server URI.
        """
        self.token = token
        self.demo = demo
        self.server_region = server_region if server_region in get_available_regions() else "wss://fr24g1us.expertoption.finance/ws/v40"
        self.websocket_client = WebSocketClient(self)
        self.logger = logging.getLogger("ExpertOptionAPI")
        self.profile = Profile()
        self.candles = Candles()
        self.active_assets: Dict[int, Dict] = {}
        self.candle_cache: Dict[int, Dict] = {}
        self.order_cache: Dict[int, Order] = {}
        self.connected = False
        self.assets_data = None
        self.profile_data = None

    async def connect(self, max_retries: int = 3, retry_delay: float = 5.0):
        """Connect to the ExpertOption server and initialize the session with retries.
        
        Args:
            max_retries: Maximum number of connection retries.
            retry_delay: Delay between retries in seconds.
        
        Raises:
            ConnectionError: If all retries fail.
        """
        if self.connected:
            self.logger.info("Already connected to the server")
            return
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                await self.websocket_client.connect(self.server_region)
                # Send multipleAction requests and fetch assets
                await self.send_multiple_action()
                await asyncio.sleep(1.0)  # Add delay to ensure responses are processed
                await self.set_trading_mode()
                await self.fetch_profile()
                # Process assets data
                self.logger.debug(f"Assets data type: {type(self.assets_data)}, content: {self.assets_data}")
                if self.assets_data and isinstance(self.assets_data, dict):
                    try:
                        assets_list = self.assets_data.get("message", {}).get("assets", [])
                        if not isinstance(assets_list, list):
                            self.logger.error(f"Assets list is not a list: {assets_list}")
                            raise ValueError("Assets data is invalid")
                        # Merge new assets with existing ones
                        for asset in assets_list:
                            if asset.get("is_active") == 1:
                                self.active_assets[asset["id"]] = asset
                        self.logger.info(f"Merged {len(assets_list)} assets, total active assets: {len(self.active_assets)}")
                        self.logger.debug(f"Active asset IDs: {list(self.active_assets.keys())}")
                    except Exception as e:
                        self.logger.error(f"Failed to process assets data: {str(e)}")
                        raise DataFetchError(f"Failed to process assets data: {str(e)}")
                else:
                    self.logger.warning("No valid assets data received from multipleAction, trying fetch_assets")
                    await self.fetch_assets()
                self.connected = True
                self.logger.info("Successfully connected to ExpertOption server")
                asyncio.create_task(self._auto_ping())
                return
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt + 1} failed: {str(e)}", exc_info=True)
                self.connected = False
                await self.websocket_client.disconnect()
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    raise ConnectionError(f"Connection failed after {max_retries} attempts: {str(e)}")

    async def send_multiple_action(self):
        """Send multipleAction requests similar to the old library and F12 data."""
        try:
            # First multipleAction request (matches F12, without defaultSubscribeCandles)
            ns = str(uuid4())
            payload1 = {
                "action": "multipleAction",
                "message": {
                    "actions": [
                        {"action": "userGroup", "ns": str(uuid4()), "token": self.token},
                        {"action": "profile", "ns": str(uuid4()), "token": self.token},
                        {"action": "assets", "ns": str(uuid4()), "token": self.token},
                        {"action": "getCurrency", "ns": str(uuid4()), "token": self.token},
                        {"action": "getCountries", "ns": str(uuid4()), "token": self.token},
                        {"action": "environment", "message": {
                            "supportedFeatures": ["achievements", "trade_result_share", "tournaments", "referral", "twofa", "inventory", "deposit_withdrawal_error_handling", "report_a_problem_form", "ftt_trade", "stocks_trade"],
                            "supportedAbTests": ["tournament_glow", "floating_exp_time", "tutorial", "tutorial_account_type", "tutorial_account_type_reg", "hide_education_section", "in_app_update_android_2", "auto_consent_reg", "btn_finances_to_register", "battles_4th_5th_place_rewards", "show_achievements_bottom_sheet", "kyc_webview", "promo_story_priority", "force_lang_in_app", "one_click_deposit"],
                            "supportedInventoryItems": ["riskless_deal", "profit", "eopoints", "tournaments_prize_x3", "mystery_box", "special_deposit_bonus", "cashback_offer"]
                        }, "ns": str(uuid4()), "token": self.token},
                        {"action": "setTimeZone", "message": {"timeZone": 180}, "ns": str(uuid4()), "token": self.token},
                        {"action": "getCandlesTimeframes", "ns": str(uuid4()), "token": self.token}
                    ]
                },
                "token": self.token,
                "ns": ns
            }
            self.logger.debug(f"Sending first multipleAction payload: {json.dumps(payload1, indent=2)}")
            await self.websocket_client.send(payload1)
            self.logger.info("Sent first multipleAction request")
            await asyncio.sleep(1.0)  # Wait for response

            # Second multipleAction request (matches old library, without defaultSubscribeCandles)
            payload2 = {
                "action": "multipleAction",
                "message": {
                    "actions": [
                        {"action": "userGroup", "ns": str(uuid4()), "token": self.token},
                        {"action": "profile", "ns": str(uuid4()), "token": self.token},
                        {"action": "assets", "message": {"mode": ["vanilla"], "subscribeMode": ["vanilla"]}, "ns": str(uuid4()), "token": self.token},
                        {"action": "getCurrency", "ns": str(uuid4()), "token": self.token},
                        {"action": "getCountries", "ns": str(uuid4()), "token": self.token},
                        {"action": "environment", "ns": str(uuid4()), "token": self.token},
                        {"action": "setTimeZone", "message": {"timeZone": -180}, "ns": str(uuid4()), "token": self.token},
                        {"action": "getCandlesTimeframes", "ns": str(uuid4()), "token": self.token}
                    ]
                },
                "token": self.token,
                "ns": str(uuid4())
            }
            self.logger.debug(f"Sending second multipleAction payload: {json.dumps(payload2, indent=2)}")
            await self.websocket_client.send(payload2)
            self.logger.info("Sent second multipleAction request")
            await asyncio.sleep(1.0)  # Wait for response

            # Third multipleAction request (matches old library)
            payload3 = {
                "action": "multipleAction",
                "message": {
                    "actions": [
                        {"action": "openOptions", "ns": str(uuid4()), "token": self.token},
                        {"action": "tradeHistory", "message": {"index_from": 0, "count": 20, "is_demo": 1}, "ns": str(uuid4()), "token": self.token},
                        {"action": "tradeHistory", "message": {"index_from": 0, "count": 20, "is_demo": 0}, "ns": str(uuid4()), "token": self.token},
                        {"action": "getTournaments", "ns": str(uuid4()), "token": self.token},
                        {"action": "getTournamentInfo", "ns": str(uuid4()), "token": self.token}
                    ]
                },
                "token": self.token,
                "ns": str(uuid4())
            }
            self.logger.debug(f"Sending third multipleAction payload: {json.dumps(payload3, indent=2)}")
            await self.websocket_client.send(payload3)
            self.logger.info("Sent third multipleAction request")
        except Exception as e:
            self.logger.error(f"Failed to send multipleAction requests: {str(e)}", exc_info=True)
            raise

    async def disconnect(self):
        """Disconnect from the ExpertOption server."""
        try:
            self.connected = False  # Set connected to False before disconnecting
            await self.websocket_client.disconnect()
            self.logger.info("Disconnected from ExpertOption server")
        except Exception as e:
            self.logger.error(f"Failed to disconnect: {str(e)}", exc_info=True)

    async def _auto_ping(self):
        """Periodically send ping requests to keep the connection alive."""
        ping_channel = PingChannel(self)
        while self.connected:
            try:
                await ping_channel.send(self, {})
                self.logger.debug("Sent ping request")
                await asyncio.sleep(15)  # Increased interval to reduce load
            except Exception as e:
                self.logger.error(f"Error sending ping: {str(e)}", exc_info=True)
                await asyncio.sleep(15)

    async def set_trading_mode(self):
        """Set the trading mode (demo or real)."""
        try:
            mode = 1 if self.demo else 0
            payload = {"action": "setContext", "message": {"is_demo": mode}, "token": self.token, "ns": str(uuid4())}
            self.logger.debug(f"Sending setContext payload: {json.dumps(payload, indent=2)}")
            await self.websocket_client.send(payload)
            self.logger.info(f"Trading mode set to {'demo' if self.demo else 'real'}")
        except Exception as e:
            self.logger.error(f"Failed to set trading mode: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to set trading mode: {str(e)}")

    async def fetch_profile(self):
        """Fetch user profile data from the server."""
        try:
            if self.profile_data:
                profile_data = self.profile_data.get("message", {}).get("profile", {})
                self.profile.demo_balance = profile_data.get("demo_balance", 0.0)
                self.profile.real_balance = profile_data.get("balance", 0.0)
                self.profile.user_id = profile_data.get("id")
                self.profile.nickname = profile_data.get("name")
                self.logger.info("User profile data fetched from cache")
            else:
                payload = {"action": "profile", "message": None, "ns": str(uuid4()), "token": self.token}
                self.logger.debug(f"Sending profile payload: {json.dumps(payload, indent=2)}")
                await self.websocket_client.send(payload)
                response = await self.websocket_client.recv("profile", timeout=20.0)
                self.profile_data = response
                profile_data = response.get("message", {}).get("profile", {})
                self.profile.demo_balance = profile_data.get("demo_balance", 0.0)
                self.profile.real_balance = profile_data.get("balance", 0.0)
                self.profile.user_id = profile_data.get("id")
                self.profile.nickname = profile_data.get("name")
                self.logger.info("User profile data fetched successfully")
        except Exception as e:
            self.logger.error(f"Failed to fetch profile data: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to fetch profile data: {str(e)}")

    async def fetch_assets(self):
        """Fetch available assets data from the server (fallback)."""
        try:
            payload = {
                "action": "assets",
                "message": {"mode": ["vanilla", "binary"], "subscribeMode": ["vanilla"]},
                "ns": str(uuid4()),
                "token": self.token
            }
            self.logger.debug(f"Sending assets payload: {json.dumps(payload, indent=2)}")
            await self.websocket_client.send(payload)
            await asyncio.sleep(0.5)
            response = await self.websocket_client.recv("assets", timeout=20.0)
            self.assets_data = response
            # Merge new assets with existing ones
            assets_list = response.get("message", {}).get("assets", [])
            for asset in assets_list:
                if asset.get("is_active") == 1:
                    self.active_assets[asset["id"]] = asset
            self.logger.info(f"Merged {len(assets_list)} assets, total active assets: {len(self.active_assets)}")
            self.logger.debug(f"Active asset IDs: {list(self.active_assets.keys())}")
        except Exception as e:
            self.logger.error(f"Failed to fetch assets data: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to fetch assets data: {str(e)}")

    def get_balance(self) -> float:
        """Get the current account balance.
        
        Returns:
            The balance for the current mode (demo or real).
        """
        balance = self.profile.demo_balance if self.demo else self.profile.real_balance
        self.logger.debug(f"Account balance: {balance}")
        return balance

    async def get_candles(self, asset_id: int, timeframes: List[int] = [0, 5]) -> Dict:
        """Subscribe to real-time candle data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
            timeframes: List of timeframes (e.g., [0, 5] for tick and 5-second candles).
        
        Returns:
            The candle data.
        
        Raises:
            InvalidAssetError: If the asset is not active.
            DataFetchError: If fetching candle data fails.
        """
        try:
            if not validate_asset_id(asset_id, self.active_assets):
                self.logger.error(f"Asset ID {asset_id} not found in active assets: {list(self.active_assets.keys())}")
                raise InvalidAssetError(f"Asset ID {asset_id} is not active")
            
            candles_channel = CandlesChannel(self)
            response = await candles_channel(asset_id, timeframes)
            self.logger.debug(f"Candle response for asset ID {asset_id}: {response}")
            
            candle_data = response.get("message", {})
            if not isinstance(candle_data, dict) or "candles" not in candle_data:
                self.logger.error(f"Invalid candle data format for asset ID {asset_id}: {candle_data}")
                raise DataFetchError(f"Invalid candle data format for asset ID {asset_id}")
            
            self.candle_cache[asset_id] = candle_data
            self.candles.candles_data = candle_data
            self.logger.info(f"Fetched candle data for asset ID {asset_id}")
            return self.candle_cache[asset_id]
        except Exception as e:
            self.logger.error(f"Failed to fetch candle data for asset ID {asset_id}: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to fetch candle data: {str(e)}")

    async def place_order(self, asset_id: int, amount: float, direction: str = "call") -> int:
        """Place a trading order.
        
        Args:
            asset_id: The ID of the asset.
            amount: The investment amount.
            direction: The trade direction ("call" or "put").
        
        Returns:
            The order ID.
        
        Raises:
            InvalidAssetError: If the asset is not active.
            InvalidExpirationTimeError: If the expiration time is invalid.
            OrderPlacementError: If order placement fails.
        """
        try:
            if not validate_asset_id(asset_id, self.active_assets):
                raise InvalidAssetError(f"Asset ID {asset_id} is not active")
            
            await self.get_candles(asset_id)
            candle_data = self.candle_cache.get(asset_id, {})
            self.logger.debug(f"Candle data for placing order: {candle_data}")
            
            exp_times = self.active_assets.get(asset_id, {}).get("rates", [{}])[0].get("expirations", [])
            server_time = candle_data.get("candles", [{}])[0].get("t", int(time.time()))
            
            if not exp_times:
                self.logger.warning("No valid expiration times found, using fallback")
                exp_time = int(time.time()) + 60  # Fallback to 1 minute from now
            else:
                exp_time = get_next_expiration_time(exp_times, server_time)
            
            buy_channel = BuyChannel(self)
            response = await buy_channel(asset_id, amount, direction, exp_time, self.demo)
            options = response.get("message", {}).get("options", [])
            if options:
                order_id = options[0].get("id")
                order = Order()
                order.order_id = order_id
                order.asset_id = asset_id
                order.amount = amount
                order.direction = direction
                order.strike_time = server_time
                order.exp_time = exp_time
                self.order_cache[order_id] = order
                self.logger.info(f"Order placed successfully for asset ID {asset_id}. Order ID: {order_id}")
                return order_id
            raise OrderPlacementError("Order placement failed: No options returned")
        except Exception as e:
            self.logger.error(f"Failed to place order for asset ID {asset_id}: {str(e)}", exc_info=True)
            raise OrderPlacementError(f"Failed to place order: {str(e)}")

    async def check_order_status(self, order_id: int, timeout: float = 60.0) -> Optional[Order]:
        """Check the status of a trading order.
        
        Args:
            order_id: The ID of the order to check.
            timeout: Maximum time to wait for the result.
        
        Returns:
            The order object with updated status and profit.
        """
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = await self.websocket_client.recv("expertOption", timeout=1.0)
                    options = response.get("message", {}).get("options", [])
                    for opt in options:
                        if opt.get("id") == order_id:
                            order = self.order_cache.get(order_id, Order())
                            order.status = opt.get("status")
                            order.profit = opt.get("profit", 0)
                            self.logger.info(f"Order status for ID {order_id}: {opt}")
                            return order
                    await asyncio.sleep(1)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.logger.error(f"Error checking order status for ID {order_id}: {str(e)}", exc_info=True)
                    return None
            self.logger.warning(f"Order ID {order_id} did not resolve within {timeout} seconds")
            return None
        except Exception as e:
            self.logger.error(f"Failed to check order status for ID {order_id}: {str(e)}", exc_info=True)
            return None

    async def place_order_by_symbol(self, symbol: str, amount: float, direction: str = "call") -> int:
        """Place a trading order using the asset symbol.
        
        Args:
            symbol: The symbol of the asset (e.g., 'BTCUSD').
            amount: The amount to invest.
            direction: Trade direction ("call" or "put").
        
        Returns:
            The order ID.
        
        Raises:
            InvalidAssetError: If the symbol is invalid.
        """
        try:
            if not validate_symbol(symbol):
                raise InvalidAssetError(f"Symbol {symbol} not found")
            asset_id = get_asset_id(symbol)
            return await self.place_order(asset_id, amount, direction)
        except Exception as e:
            self.logger.error(f"Failed to place order by symbol {symbol}: {str(e)}", exc_info=True)
            raise InvalidAssetError(f"Failed to place order by symbol: {str(e)}")

    async def get_historical_candles(self, asset_id: int, periods: List[List[int]]) -> Dict:
        """Fetch historical candle data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
            periods: List of time periods [[start, end], ...] in Unix timestamps.
        
        Returns:
            The historical candle data.
        
        Raises:
            InvalidAssetError: If the asset is not active.
            DataFetchError: If fetching historical candle data fails.
        """
        try:
            if not validate_asset_id(asset_id, self.active_assets):
                self.logger.error(f"Asset ID {asset_id} not found in active assets: {list(self.active_assets.keys())}")
                raise InvalidAssetError(f"Asset ID {asset_id} is not active")
            
            payload = {
                "action": "assetHistoryCandles",
                "message": {
                    "assetid": asset_id,
                    "periods": periods,
                    "timeframes": [5]
                },
                "token": self.token,
                "ns": str(uuid4())
            }
            self.logger.debug(f"Sending historical candles request: {json.dumps(payload, indent=2)}")
            await self.websocket_client.send(payload)
            response = await self.websocket_client.recv("assetHistoryCandles", timeout=20.0)
            self.logger.debug(f"Received historical candles response: {response}")
            
            candle_data = response.get("message", {})
            if not isinstance(candle_data, dict) or "candles" not in candle_data:
                self.logger.error(f"Invalid historical candle data format for asset ID {asset_id}: {candle_data}")
                raise DataFetchError(f"Invalid historical candle data format for asset ID {asset_id}")
            
            return candle_data
        except Exception as e:
            self.logger.error(f"Failed to fetch historical candle data for asset ID {asset_id}: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to fetch historical candle data: {str(e)}")

    async def get_traders_choice(self, asset_id: int) -> Dict:
        """Fetch traders' choice data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
        
        Returns:
            The traders' choice data.
        
        Raises:
            InvalidAssetError: If the asset is not active.
            DataFetchError: If fetching traders' choice data fails.
        """
        try:
            if not validate_asset_id(asset_id, self.active_assets):
                self.logger.error(f"Asset ID {asset_id} not found in active assets: {list(self.active_assets.keys())}")
                raise InvalidAssetError(f"Asset ID {asset_id} is not active")
            
            traders_choice_channel = TradersChoiceChannel(self)
            response = await traders_choice_channel(asset_id)
            self.logger.debug(f"Traders' choice response for asset ID {asset_id}: {response}")
            
            choice_data = response.get("message", {})
            if not isinstance(choice_data, dict):
                self.logger.error(f"Invalid traders' choice data format for asset ID {asset_id}: {choice_data}")
                raise DataFetchError(f"Invalid traders' choice data format for asset ID {asset_id}")
            
            return choice_data
        except Exception as e:
            self.logger.error(f"Failed to fetch traders' choice data for asset ID {asset_id}: {str(e)}", exc_info=True)
            raise DataFetchError(f"Failed to fetch traders' choice data: {str(e)}")