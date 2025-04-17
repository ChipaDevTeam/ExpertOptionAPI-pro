"""Profile object for the ExpertOption API."""
from Expert.ws.objects.base import BaseObject

class Profile(BaseObject):
    """Object for storing user profile data."""
    
    def __init__(self):
        super().__init__()
        self.__name = "profile"
        self.__demo_balance: float = 0.0
        self.__real_balance: float = 0.0
        self.__user_id: int = None
        self.__nickname: str = None
    
    @property
    def demo_balance(self) -> float:
        """Get the demo balance.
        
        Returns:
            The demo balance.
        """
        return self.__demo_balance
    
    @demo_balance.setter
    def demo_balance(self, value: float):
        """Set the demo balance."""
        self.__demo_balance = value
    
    @property
    def real_balance(self) -> float:
        """Get the real balance.
        
        Returns:
            The real balance.
        """
        return self.__real_balance
    
    @real_balance.setter
    def real_balance(self, value: float):
        """Set the real balance."""
        self.__real_balance = value
    
    @property
    def user_id(self) -> int:
        """Get the user ID.
        
        Returns:
            The user ID.
        """
        return self.__user_id
    
    @user_id.setter
    def user_id(self, value: int):
        """Set the user ID."""
        self.__user_id = value
    
    @property
    def nickname(self) -> str:
        """Get the nickname.
        
        Returns:
            The nickname.
        """
        return self.__nickname
    
    @nickname.setter
    def nickname(self, value: str):
        """Set the nickname."""
        self.__nickname = value