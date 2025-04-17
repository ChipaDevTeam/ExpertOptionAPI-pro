"""Traders Choice channel for the ExpertOption API."""
from Expert.ws.channels.base import BaseChannel
from Expert.exceptions import InvalidAssetError
from Expert.utils import validate_asset_id

class TradersChoiceChannel(BaseChannel):
    """Channel for fetching traders' choice data (put/call ratio)."""
    
    name = "traders_choice"
    
    async def __call__(self, asset_id: int):
        """Fetch traders' choice data for a specific asset.
        
        Args:
            asset_id: The ID of the asset.
        
        Returns:
            The traders' choice data response.
        
        Raises:
            InvalidAssetError: If the asset is not active.
        """
        if not validate_asset_id(asset_id, self.api.active_assets):
            raise InvalidAssetError(f"Asset ID {asset_id} is not active")
        
        message = {
            "assets": [asset_id]
        }
        return await self.send_request("tradersChoice", message)