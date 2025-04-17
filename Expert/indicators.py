"""Technical indicators for the ExpertOption API."""
import numpy as np
import logging
from typing import Dict, List, Optional
from Expert.api import ExpertOptionAPI
from Expert.exceptions import InvalidAssetError, OrderPlacementError

class AlligatorIndicator:
    """Alligator Indicator for analyzing market trends and generating trading signals."""
    
    def __init__(self, candle_data: Dict):
        """Initialize the Alligator Indicator with candle data.
        
        Args:
            candle_data: Candle data dictionary from the API.
        """
        self.logger = logging.getLogger("AlligatorIndicator")
        self.prices = self._extract_closing_prices(candle_data)
        if self.prices:
            self.jaw = self._calculate_sma(13, 8)
            self.teeth = self._calculate_sma(8, 5)
            self.lips = self._calculate_sma(5, 3)
        else:
            self.logger.warning("No closing prices extracted from candle data")
            self.jaw = self.teeth = self.lips = []

    def _extract_closing_prices(self, candle_data: Dict) -> List[float]:
        """Extract closing prices from candle data.
        
        Args:
            candle_data: Candle data dictionary.
        
        Returns:
            List of closing prices.
        """
        prices = []
        try:
            for candle in candle_data.get("candles", []):
                for period in candle.get("periods", []):
                    for data in period[1]:
                        closing_price = data[3]
                        prices.append(closing_price)
        except Exception as e:
            self.logger.error(f"Error extracting closing prices: {e}")
        return prices

    def _calculate_sma(self, period: int, shift: int) -> np.ndarray:
        """Calculate Smoothed Moving Average.
        
        Args:
            period: Period for the moving average.
            shift: Shift for the moving average.
        
        Returns:
            Smoothed moving average values as a NumPy array.
        """
        if not self.prices:
            return np.array([])
        sma = np.convolve(self.prices, np.ones(period), "valid") / period
        return np.concatenate((np.full(shift, np.nan), sma))

    async def evaluate_market_trend(self, api: ExpertOptionAPI, asset_id: int = 240, amount: float = 1.0) -> str:
        """Evaluate market conditions and place a trade if conditions are met.
        
        Args:
            api: ExpertOptionAPI instance for placing orders.
            asset_id: The ID of the asset to trade.
            amount: The amount to invest in the trade.
        
        Returns:
            Market signal ("Buy signal executed", "Sell signal executed", "Hold", or "Not enough data").
        
        Raises:
            InvalidAssetError: If the asset is not active.
            OrderPlacementError: If placing the order fails.
        """
        if len(self.jaw) < 2 or len(self.teeth) < 2 or len(self.lips) < 2:
            self.logger.warning("Not enough data for Alligator Indicator analysis")
            return "Not enough data"

        last_order = self.jaw[-1] > self.teeth[-1] > self.lips[-1]
        prev_order = self.jaw[-2] > self.teeth[-2] > self.lips[-2]

        if not prev_order and last_order:
            try:
                order_id = await api.place_order(asset_id, amount, "call")
                self.logger.info(f"Buy signal executed for asset ID {asset_id}, order ID: {order_id}")
                return "Buy signal executed"
            except Exception as e:
                self.logger.error(f"Failed to execute buy order: {e}")
                raise OrderPlacementError(f"Failed to execute buy order: {e}")

        if prev_order and not last_order:
            try:
                order_id = await api.place_order(asset_id, amount, "put")
                self.logger.info(f"Sell signal executed for asset ID {asset_id}, order ID: {order_id}")
                return "Sell signal executed"
            except Exception as e:
                self.logger.error(f"Failed to execute sell order: {e}")
                raise OrderPlacementError(f"Failed to execute sell order: {e}")

        self.logger.debug("No trading signal generated. Holding position.")
        return "Hold"

class RSIIndicator:
    """Relative Strength Index (RSI) for analyzing market conditions."""
    
    def __init__(self, candle_data: Dict, period: int = 14):
        """Initialize the RSI Indicator with candle data.
        
        Args:
            candle_data: Candle data dictionary from the API.
            period: Number of periods for RSI calculation.
        """
        self.logger = logging.getLogger("RSIIndicator")
        self.period = period
        self.prices = self._extract_closing_prices(candle_data)

    def _extract_closing_prices(self, candle_data: Dict) -> List[float]:
        """Extract closing prices from candle data.
        
        Args:
            candle_data: Candle data dictionary.
        
        Returns:
            List of closing prices.
        """
        prices = []
        try:
            for candle in candle_data.get("candles", []):
                for period in candle.get("periods", []):
                    for data in period[1]:
                        closing_price = data[3]
                        prices.append(closing_price)
        except Exception as e:
            self.logger.error(f"Error extracting closing prices: {e}")
        return prices

    def calculate_rsi(self) -> Optional[float]:
        """Calculate the Relative Strength Index (RSI).
        
        Returns:
            RSI value or None if insufficient data.
        """
        if len(self.prices) < self.period:
            self.logger.warning(f"Insufficient data for RSI calculation. Need at least {self.period} prices, got {len(self.prices)}")
            return None

        try:
            changes = np.diff(self.prices)
            gains = np.where(changes > 0, changes, 0)
            losses = np.where(changes < 0, -changes, 0)

            avg_gain = np.mean(gains[:self.period])
            avg_loss = np.mean(losses[:self.period])

            for i in range(self.period, len(gains)):
                avg_gain = (avg_gain * (self.period - 1) + gains[i]) / self.period
                avg_loss = (avg_loss * (self.period - 1) + losses[i]) / self.period

            if avg_loss == 0:
                self.logger.debug("No losses recorded. RSI set to 100")
                return 100

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            self.logger.debug(f"Calculated RSI: {rsi}")
            return rsi
        except Exception as e:
            self.logger.error(f"Error calculating RSI: {e}")
            return None

    def evaluate_market_condition(self, overbought_threshold: float = 70, oversold_threshold: float = 30) -> str:
        """Evaluate if the market is overbought or oversold based on RSI.
        
        Args:
            overbought_threshold: RSI threshold for overbought condition.
            oversold_threshold: RSI threshold for oversold condition.
        
        Returns:
            Market condition ("Overbought", "Oversold", "Neutral", or "Not enough data").
        """
        rsi = self.calculate_rsi()
        if rsi is None:
            return "Not enough data"
        if rsi > overbought_threshold:
            self.logger.debug(f"RSI {rsi} indicates overbought condition")
            return "Overbought"
        if rsi < oversold_threshold:
            self.logger.debug(f"RSI {rsi} indicates oversold condition")
            return "Oversold"
        self.logger.debug(f"RSI {rsi} indicates neutral condition")
        return "Neutral"

    async def execute_rsi_strategy(self, api: ExpertOptionAPI, asset_id: int = 240, amount: float = 1.0,
                                  overbought_threshold: float = 70, oversold_threshold: float = 30) -> str:
        """Execute a trading strategy based on RSI signals.
        
        Args:
            api: ExpertOptionAPI instance for placing orders.
            asset_id: The ID of the asset to trade.
            amount: The amount to invest in the trade.
            overbought_threshold: RSI threshold for overbought condition.
            oversold_threshold: RSI threshold for oversold condition.
        
        Returns:
            Trading signal ("Buy signal executed", "Sell signal executed", "Hold", or "Not enough data").
        
        Raises:
            InvalidAssetError: If the asset is not active.
            OrderPlacementError: If placing the order fails.
        """
        condition = self.evaluate_market_condition(overbought_threshold, oversold_threshold)
        if condition == "Not enough data":
            return condition

        if condition == "Oversold":
            try:
                order_id = await api.place_order(asset_id, amount, "call")
                self.logger.info(f"Buy signal executed for asset ID {asset_id} (RSI oversold), order ID: {order_id}")
                return "Buy signal executed"
            except Exception as e:
                self.logger.error(f"Failed to execute buy order: {e}")
                raise OrderPlacementError(f"Failed to execute buy order: {e}")

        if condition == "Overbought":
            try:
                order_id = await api.place_order(asset_id, amount, "put")
                self.logger.info(f"Sell signal executed for asset ID {asset_id} (RSI overbought), order ID: {order_id}")
                return "Sell signal executed"
            except Exception as e:
                self.logger.error(f"Failed to execute sell order: {e}")
                raise OrderPlacementError(f"Failed to execute sell order: {e}")

        return "Hold"