"""NIFTY market-regime filter."""

from dataclasses import dataclass
from core.daily_context import classify_daily_context


@dataclass
class MarketRegime:
    regime: str
    long_supported: bool
    short_supported: bool
    reason: str


def classify_market_regime(nifty_daily_candles) -> MarketRegime:
    """Classify NIFTY 50 daily structure as Bullish/Bearish/Range/Transition."""
    if not nifty_daily_candles:
        return MarketRegime("Unknown", False, False, "NIFTY data not supplied")

    context = classify_daily_context(nifty_daily_candles)

    if context == "Bullish":
        return MarketRegime("Bullish", True, False, "NIFTY daily structure supports longs")
    if context == "Bearish":
        return MarketRegime("Bearish", False, True, "NIFTY daily structure supports shorts")
    if context == "Range":
        return MarketRegime("Range", False, False, "NIFTY is ranging; directional edge is weaker")

    return MarketRegime("Transition", False, False, "NIFTY direction is not clear")
