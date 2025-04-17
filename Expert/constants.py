"""Constants for the ExpertOption API."""
from typing import Dict, List

# Mapping of asset IDs to symbols
ASSET_MAPPING: Dict[int, str] = {
    142: "EURUSD_otc",
    151: "AUDCAD",
    152: "AUDJPY",
    153: "AUDUSD",
    154: "EURGBP",
    155: "GBPUSD",
    156: "NZDUSD",
    157: "USDCAD",
    158: "USDCHF",
    159: "USDJPY",
    160: "BTCUSD",
    162: "ETHUSD",
    163: "BTCLTC",
    167: "BCHUSD",
    168: "IOTAUSD",
    170: "XAUTRY",
    171: "XMRUSD",
    172: "ZECUSD",
    175: "ETCUSD",
    176: "GOLD",
    177: "OILBRENT",
    178: "SILVER",
    179: "EURUSD_otc",
    180: "GBPUSD_otc",
    181: "USDJPY_otc",
    182: "USDCHF_otc",
    183: "EURGBP_otc",
    184: "AUDUSD_otc",
    185: "USDCAD_otc",
    186: "NZDUSD_otc",
    187: "EURJPY_otc",
    188: "EURCAD_otc",
    189: "META",
    190: "BABA",
    191: "GOOGL",
    192: "AAPL",
    193: "AMZN",
    194: "MSFT",
    195: "TSLA",
    196: "LMT",
    197: "VRX",
    199: "YUM",
    200: "IBM",
    201: "YHOO",
    202: "MCD",
    203: "DIS",
    204: "F",
    205: "CITI",
    206: "GS",
    207: "KO",
    208: "BIDU",
    209: "NFLX",
    210: "USDNOK",
    211: "EURAUD",
    212: "EURCHF",
    214: "GBPCAD",
    216: "GBPCHF",
    217: "EURJPY",
    218: "AUDCHF",
    219: "AUDNZD",
    221: "PLATINUM",
    229: "ALTINDEX",
    230: "TOPCRYPTO",
    231: "BINANCEINDEX",
    232: "BTCTRY",
    233: "USDINDEX",
    239: "QQQ",
    240: "SMARTY",
    247: "COPPER",
    252: "SP500",
    253: "TOTALSTOCK",
    254: "EMERGINGETF",
    255: "RUSSELL2000",
    256: "GOLDETF",
    257: "TREASURYBOND",
    258: "DEVETFS",
    259: "JAPANETF",
    260: "USOILETF",
    262: "TECHETF",
    263: "FINANCIALETF",
    264: "ENERGYETF",
    265: "REALESTATEETF",
    266: "MATERIALSECTOR",
    272: "INDIAINDEX",
    276: "CRICKETINDEX",
    277: "CAMELINDEX",
    278: "FOOTBALLINDEX",
    279: "CISCO",
    280: "NVIDIA",
    281: "XOM",
    282: "PG",
    283: "GM",
    284: "NIKE",
    285: "AIINDEX",
    286: "LUXURYINDEX",
    316: "TRUMP",
}

# Reverse mapping for symbol to ID
SYMBOL_TO_ID: Dict[str, int] = {v: k for k, v in ASSET_MAPPING.items()}

# WebSocket server regions
REGIONS: Dict[str, str] = {
    "EUROPE": "wss://fr24g1eu.expertoption.com/",
    "INDIA": "wss://fr24g1in.expertoption.com/",
    "HONG_KONG": "wss://fr24g1hk.expertoption.com/",
    "SINGAPORE": "wss://fr24g1sg.expertoption.com/",
    "UNITED_STATES": "wss://fr24g1us.expertoption.com/",
}

def get_asset_id(symbol: str) -> int:
    """Retrieve asset ID from symbol.
    
    Args:
        symbol: The asset symbol (e.g., 'EURUSD_otc').
    
    Returns:
        The corresponding asset ID or None if not found.
    """
    return SYMBOL_TO_ID.get(symbol.upper())

def get_asset_symbol(asset_id: int) -> str:
    """Retrieve asset symbol from ID.
    
    Args:
        asset_id: The asset ID.
    
    Returns:
        The corresponding asset symbol or None if not found.
    """
    return ASSET_MAPPING.get(asset_id)

def get_available_regions() -> List[str]:
    """Return list of available server regions.
    
    Returns:
        List of WebSocket server URIs.
    """
    return list(REGIONS.values())

def get_default_multiple_action(token: str) -> Dict:
    """Generate default data for multiple action request.
    
    Args:
        token: API authentication token.
    
    Returns:
        Dictionary containing the request data.
    """
    return {
        "token": token,
        "v": 18,
        "action": "multipleAction",
        "message": {
            "token": token,
            "actions": [
                {"action": "getCountries", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "getCurrency", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "profile", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "environment", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "assets", "message": {"mode": ["vanilla", "binary"], "subscribeMode": ["vanilla"]}, "ns": None, "v": 18, "token": token},
                {"action": "openOptions", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "userGroup", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "setTimeZone", "message": {"timeZone": 360}, "ns": None, "v": 18, "token": token},
                {"action": "historySteps", "message": None, "ns": None, "v": 18, "token": token},
                {"action": "tradeHistory", "message": {"mode": ["binary", "vanilla"], "count": 100, "index_from": 0}, "ns": None, "v": 18, "token": token},
            ],
        },
    }