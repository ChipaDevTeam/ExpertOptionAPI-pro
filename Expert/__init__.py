"""A Python wrapper for the ExpertOption API."""
import logging

def _setup_logging():
    """Configure logging for the ExpertOption API module."""
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())
    websocket_logger = logging.getLogger("websockets")
    websocket_logger.setLevel(logging.DEBUG)
    websocket_logger.addHandler(logging.NullHandler())

_setup_logging()