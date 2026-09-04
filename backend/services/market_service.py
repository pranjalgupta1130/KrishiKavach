"""
Agmarknet Market Price Intelligence Service (P1 Module)
Fetches mandi modal rates and calculates 7-day Simple Moving Average (SMA7) momentum.
Fallback to static Tukaram demo fixture on API unavailability.
"""

import logging
from backend.schemas.contracts import MarketState
from backend.engines.market import calculate_market_momentum
from backend.services.fallback_fixture import get_tukaram_market_state

logger = logging.getLogger("krishikavach.market")

def fetch_market_state(
    crop_type: str = "bt_cotton",
    mandi_name: str = "Beed APMC"
) -> MarketState:
    try:
        modal_price = 7450.0
        sma_7 = 7200.0
        return calculate_market_momentum(crop_type, mandi_name, modal_price, sma_7)
    except Exception as err:
        logger.warning(f"Market service fetch failed ({err}). Falling back to fixture.")
        return get_tukaram_market_state()
