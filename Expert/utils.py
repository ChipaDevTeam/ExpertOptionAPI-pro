"""Utility functions for the ExpertOption API."""
import logging
import time
from typing import List

logger = logging.getLogger("ExpertOptionUtils")

def validate_asset_id(asset_id: int, active_assets: dict) -> bool:
    """Validate if an asset ID is active.
    
    Args:
        asset_id: The ID of the asset.
        active_assets: Dictionary of active assets.
    
    Returns:
        True if the asset is active, False otherwise.
    """
    return asset_id in active_assets

def validate_symbol(symbol: str) -> bool:
    """Validate if a symbol is valid.
    
    Args:
        symbol: The symbol to validate (e.g., 'BTCUSD').
    
    Returns:
        True if the symbol is valid, False otherwise.
    """
    from Expert.constants import get_asset_id
    try:
        get_asset_id(symbol)
        return True
    except KeyError:
        return False

def validate_expiration_time(expiration_time: int, server_time: int) -> bool:
    """Validate if an expiration time is valid.
    
    Args:
        expiration_time: The expiration time to validate (Unix timestamp).
        server_time: Current server time (Unix timestamp).
    
    Returns:
        True if the expiration time is valid (in the future), False otherwise.
    """
    if not isinstance(expiration_time, int) or not isinstance(server_time, int):
        logger.error(f"Invalid types: expiration_time={type(expiration_time)}, server_time={type(server_time)}")
        return False
    
    if expiration_time <= server_time:
        logger.warning(f"Expiration time {expiration_time} is not in the future (server time: {server_time})")
        return False
    
    # Additional validation: ensure expiration time is within a reasonable range (e.g., next 24 hours)
    max_expiration = server_time + 86400  # 24 hours from server time
    if expiration_time > max_expiration:
        logger.warning(f"Expiration time {expiration_time} is too far in the future (max: {max_expiration})")
        return False
    
    logger.debug(f"Expiration time {expiration_time} is valid")
    return True

def get_next_expiration_time(exp_times: List[int], server_time: int) -> int:
    """Get the next valid expiration time.
    
    Args:
        exp_times: List of expiration times.
        server_time: Current server time.
    
    Returns:
        The next valid expiration time.
    """
    logger.debug(f"Expiration times: {exp_times}, Server time: {server_time}")
    
    if not exp_times:
        logger.warning("No valid expiration times found, using fallback")
        return server_time + 60  # Fallback to 1 minute from now
    
    valid_times = [t for t in exp_times if t > server_time]
    if not valid_times:
        logger.warning("No future expiration times found, using fallback")
        return server_time + 60
    
    next_time = min(valid_times)
    logger.debug(f"Selected next expiration time: {next_time}")
    return next_time