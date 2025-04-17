"""Base class for ExpertOption WebSocket objects."""
from typing import Optional

class BaseObject:
    """Base class for ExpertOption WebSocket objects."""
    
    def __init__(self):
        self.__name: Optional[str] = None
    
    @property
    def name(self) -> str:
        """Get the name of the WebSocket object.
        
        Returns:
            The name of the object.
        """
        return self.__name