"""Candles object for the ExpertOption API."""
from typing import List
from Expert.ws.objects.base import BaseObject

class Candle:
    """Object for storing a single candle's data."""
    
    def __init__(self, candle_data: List[float]):
        """Initialize the candle object.
        
        Args:
            candle_data: List containing [open, high, low, close] values.
        """
        self.__open = candle_data[0]
        self.__high = candle_data[1]
        self.__low = candle_data[2]
        self.__close = candle_data[3]
    
    @property
    def open(self) -> float:
        """Get the open price."""
        return self.__open
    
    @property
    def high(self) -> float:
        """Get the high price."""
        return self.__high
    
    @property
    def low(self) -> float:
        """Get the low price."""
        return self.__low
    
    @property
    def close(self) -> float:
        """Get the close price."""
        return self.__close
    
    @property
    def type(self) -> str:
        """Get the candle type (green or red).
        
        Returns:
            'green' if close > open, 'red' if close < open, 'neutral' otherwise.
        """
        if self.__close > self.__open:
            return "green"
        if self.__close < self.__open:
            return "red"
        return "neutral"

class Candles(BaseObject):
    """Object for storing candle data for an asset."""
    
    def __init__(self):
        super().__init__()
        self.__name = "candles"
        self.__candles_data: dict = {}
    
    @property
    def candles_data(self) -> dict:
        """Get the candles data.
        
        Returns:
            Dictionary containing candle data.
        """
        return self.__candles_data
    
    @candles_data.setter
    def candles_data(self, data: dict):
        """Set the candles data."""
        self.__candles_data = data
    
    def get_candle(self, index: int) -> Candle:
        """Get a specific candle by index.
        
        Args:
            index: The index of the candle.
        
        Returns:
            The candle object.
        """
        periods = self.__candles_data.get("candles", [[]])[0].get("periods", [[]])[1]
        return Candle(periods[index]) if periods else None