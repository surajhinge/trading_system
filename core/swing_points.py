"""
Swing point detection: finds local highs and lows in a candle series.
This is the foundation the HH/HL/LH/LL structure logic builds on —
get this wrong and every signal built on top of it is wrong too.
"""

from dataclasses import dataclass
from core.level_engine import Candle


@dataclass
class SwingPoint:
    index: int
    price: float
    kind: str  # "high" or "low"


# def find_swing_points(candles: list[Candle], window: int = 2) -> list[SwingPoint]:
#     """
#     A candle at position i is a swing HIGH if its high is greater than
#     the high of `window` candles on both sides of it.
#     Same logic in reverse for swing LOWS.

#     window=2 means: strictly higher/lower than the 2 candles before AND
#     the 2 candles after. Larger window = fewer, more significant swings.
#     """
#     swings = []
#     for i in range(window, len(candles) - window):
#         left = candles[i - window:i]
#         right = candles[i + 1:i + 1 + window]

#         is_swing_high = all(candles[i].high > c.high for c in left + right)
#         is_swing_low = all(candles[i].low < c.low for c in left + right)

#         if is_swing_high:
#             swings.append(SwingPoint(index=i, price=candles[i].high, kind="high"))
#         elif is_swing_low:
#             swings.append(SwingPoint(index=i, price=candles[i].low, kind="low"))

#     return swings

def find_swing_points(candles: list[Candle], window: int = 2) -> list[SwingPoint]:
    """
    Finds confirmed swing highs and lows.

    A candle becomes a confirmed swing only after `window` candles
    have closed to its right.

    Example with window=2:

        C1 C2 [SWING] C4 C5
                  ↑
             confirmed
             after C5 closes

    This avoids using information that was not available at the time
    of the swing.
    """
    if window < 1:
        raise ValueError("window must be >= 1")

    swings = []

    for i in range(window, len(candles) - window):
        left = candles[i - window:i]
        right = candles[i + 1:i + 1 + window]

        is_swing_high = all(
            candles[i].high > candle.high
            for candle in left + right
        )

        is_swing_low = all(
            candles[i].low < candle.low
            for candle in left + right
        )

        if is_swing_high:
            swings.append(
                SwingPoint(
                    index=i,
                    price=candles[i].high,
                    kind="high",
                )
            )

        elif is_swing_low:
            swings.append(
                SwingPoint(
                    index=i,
                    price=candles[i].low,
                    kind="low",
                )
            )

    return swings
