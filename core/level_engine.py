"""
Core candle and daily level models.

Candle is the common market-data object used by the strategy.
Optional fields keep backward compatibility with the existing tests
while allowing live OHLCV data to be used by the strategy.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candle:
    """
    One OHLCV market candle.

    open/high/low/close/volume/timestamp are supported so the strategy
    can use price-action, volume and timeframe-aware logic.

    The optional fields have defaults so existing code/tests that only
    provide high, low and close continue to work.
    """

    high: float
    low: float
    close: float
    open: float | None = None
    volume: float | None = None
    timestamp: datetime | None = None


@dataclass
class Levels:
    prev_high: float
    prev_low: float
    prev_close: float


def compute_levels(daily_candles: list[Candle]) -> Levels:
    """
    Calculate levels from the most recently supplied completed daily candle.

    IMPORTANT:
    This function assumes the caller has already removed any incomplete
    current-day candle.

    The historical-data layer will be responsible for ensuring that only
    completed candles are passed here.
    """
    if not daily_candles:
        raise ValueError("At least one daily candle is required")

    prev_day = daily_candles[-1]

    return Levels(
        prev_high=prev_day.high,
        prev_low=prev_day.low,
        prev_close=prev_day.close,
    )
