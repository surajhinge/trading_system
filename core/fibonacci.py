"""
Fibonacci retracement as a SECOND, independent confirming strategy.
Given the swing that formed the current move, computes standard
retracement levels and checks whether current price sits in the
"golden zone" (50%-61.8% retracement). A trade should only go through
when structure AND fib both agree - the "two strategies" confluence.
"""
from dataclasses import dataclass

FIB_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]


@dataclass
class FibZone:
    in_golden_zone: bool
    level_prices: dict
    current_retracement_pct: float


def compute_fib_zone(swing_low: float, swing_high: float, current_price: float, direction: str) -> FibZone:
    move = swing_high - swing_low
    if move <= 0:
        raise ValueError("swing_high must be greater than swing_low")

    level_prices = {}
    for lvl in FIB_LEVELS:
        if direction == "long":
            level_prices[lvl] = swing_high - move * lvl
        else:
            level_prices[lvl] = swing_low + move * lvl

    if direction == "long":
        retracement_pct = (swing_high - current_price) / move
    else:
        retracement_pct = (current_price - swing_low) / move

    in_golden_zone = 0.5 <= retracement_pct <= 0.618
    return FibZone(in_golden_zone=in_golden_zone, level_prices=level_prices,
                   current_retracement_pct=round(retracement_pct, 3))
