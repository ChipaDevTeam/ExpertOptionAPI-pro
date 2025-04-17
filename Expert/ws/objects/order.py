"""Order object for the ExpertOption API."""
from Expert.ws.objects.base import BaseObject

class Order(BaseObject):
    """Object for storing trading order data."""
    
    def __init__(self):
        super().__init__()
        self.__name = "order"
        self.__order_id: int = None
        self.__asset_id: int = None
        self.__amount: float = None
        self.__direction: str = None
        self.__strike_time: int = None
        self.__exp_time: int = None
        self.__profit: float = None
        self.__status: int = None
    
    @property
    def order_id(self) -> int:
        """Get the order ID."""
        return self.__order_id
    
    @order_id.setter
    def order_id(self, value: int):
        """Set the order ID."""
        self.__order_id = value
    
    @property
    def asset_id(self) -> int:
        """Get the asset ID."""
        return self.__asset_id
    
    @asset_id.setter
    def asset_id(self, value: int):
        """Set the asset ID."""
        self.__asset_id = value
    
    @property
    def amount(self) -> float:
        """Get the investment amount."""
        return self.__amount
    
    @amount.setter
    def amount(self, value: float):
        """Set the investment amount."""
        self.__amount = value
    
    @property
    def direction(self) -> str:
        """Get the trade direction ('call' or 'put')."""
        return self.__direction
    
    @direction.setter
    def direction(self, value: str):
        """Set the trade direction."""
        self.__direction = value
    
    @property
    def strike_time(self) -> int:
        """Get the strike time."""
        return self.__strike_time
    
    @strike_time.setter
    def strike_time(self, value: int):
        """Set the strike time."""
        self.__strike_time = value
    
    @property
    def exp_time(self) -> int:
        """Get the expiration time."""
        return self.__exp_time
    
    @exp_time.setter
    def exp_time(self, value: int):
        """Set the expiration time."""
        self.__exp_time = value
    
    @property
    def profit(self) -> float:
        """Get the profit amount."""
        return self.__profit
    
    @profit.setter
    def profit(self, value: float):
        """Set the profit amount."""
        self.__profit = value
    
    @property
    def status(self) -> int:
        """Get the order status (1 for closed, 0 for open)."""
        return self.__status
    
    @status.setter
    def status(self, value: int):
        """Set the order status."""
        self.__status = value