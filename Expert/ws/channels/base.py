"""Base channel class for WebSocket channels."""
import logging
from typing import Any, Dict

class BaseChannel:
    """Base class for WebSocket channels."""
    
    def __init__(self, api):
        """Initialize the base channel.
        
        Args:
            api: The ExpertOption API instance.
        """
        self.api = api
        self.logger = logging.getLogger(self.__class__.__name__)

    async def __call__(self, *args, **kwargs) -> Dict:
        """Execute the channel logic.
        
        This method should be overridden by subclasses.
        
        Returns:
            The server response as a dictionary.
        
        Raises:
            NotImplementedError: If not overridden by a subclass.
        """
        raise NotImplementedError("Subclasses must implement __call__ method")