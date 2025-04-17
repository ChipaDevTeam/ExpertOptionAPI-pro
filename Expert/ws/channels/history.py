"""History channel for the ExpertOption API."""
from typing import List
from Expert.ws.channels.base import BaseChannel
from Expert.exceptions import InvalidAssetError
from Expert.utils import validate_asset_id

class HistoryChannel(BaseChannel):
    """Channel for fetching historical candle data."""
    
    name = "history"
    
    async def __call__(self, asset_id: int, periods: List[List[int]], timeframe: int = 5):
        """Fetch historical candle data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
            periods: List of time periods (e.g., [[start_time, end_time], ...]).
            timeframe: Candle timeframe (e.g., 5 for 5-second candles).
        
        Returns:
            The historical candle data response.
        
        Raises:
            InvalidAssetError: If the asset is not active.
        """
        if not validate_asset_id(asset_id, self.api.active_assets):
            raise InvalidAssetError(f"Asset ID {asset_id} is not active")
        
        message = {
            "assetid": asset_id,
            "periods": periods,
            "timeframes": [timeframe]
        }
        return await self.send_request("assetHistoryCandles", message)