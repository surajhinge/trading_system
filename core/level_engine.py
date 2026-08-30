"""
Level Engine: turns a list of historical daily candles into reference
levels the setup detector will later compare live price against.

Kept independent of any specific API — it just takes candle data in,
so it works the same whether that data came from Upstox, a CSV, or a test.
"""

from dataclasses import dataclass


@dataclass
class Candle:
    high: float
    low: float
    close: float


@dataclass
class Levels:
    prev_high: float
    prev_low: float
    prev_close: float


def compute_levels(daily_candles: list[Candle]) -> Levels:
    """
    Compute levels from the most recently completed trading day.
    Expects daily_candles sorted oldest -> newest; uses the LAST one,
    i.e. yesterday's candle if called before today's close.
    """
    if not daily_candles:
        raise ValueError("Need at least one historical candle to compute levels")

    prev_day = daily_candles[-1]
    return Levels(
        prev_high=prev_day.high,
        prev_low=prev_day.low,
        prev_close=prev_day.close,
    )
