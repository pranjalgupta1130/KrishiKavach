"""
Agmarknet Mandi Price Intelligence Engine (P1)
Calculates Simple Moving Average (SMA7) momentum and trend indicators.
"""

from backend.schemas.contracts import MarketState

def calculate_market_momentum(
    crop_type: str,
    mandi_name: str,
    modal_price: float,
    sma_7: float
) -> MarketState:
    """
    Computes price momentum percentage relative to SMA7.
    Momentum % = ((modal_price - sma_7) / sma_7) * 100
    """
    if sma_7 <= 0:
        momentum_pct = 0.0
    else:
        momentum_pct = ((modal_price - sma_7) / sma_7) * 100.0

    if momentum_pct >= 2.0:
        trend = "FAVORABLE"
    elif momentum_pct <= -2.0:
        trend = "UNFAVORABLE"
    else:
        trend = "NEUTRAL"

    return MarketState(
        crop_type=crop_type,
        mandi_name=mandi_name,
        modal_price_inr=round(modal_price, 2),
        sma_7_inr=round(sma_7, 2),
        price_momentum_percent=round(momentum_pct, 2),
        trend=trend
    )
