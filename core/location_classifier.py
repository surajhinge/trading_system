"""
Location classifier - answers "where is current price relative to
structure?" per strategy doc section 3. Uses recent swing highs/lows
as the support/resistance reference points.
"""
from dataclasses import dataclass
from core.swing_points import find_swing_points


@dataclass
class Location:
    zone: str  # "near_support", "near_resistance", "middle", "breakout", "breakdown"
    nearest_support: float
    nearest_resistance: float


def classify_location(candles, current_price: float, window: int = 2, edge_threshold_pct: float = 15.0):
    swings = find_swing_points(candles, window=window)
    highs = [s.price for s in swings if s.kind == "high"]
    lows = [s.price for s in swings if s.kind == "low"]

    if not highs or not lows:
        raise ValueError("Not enough swing data to classify location")

    resistance = max(highs)
    support = min(lows)
    range_size = resistance - support
    if range_size <= 0:
        raise ValueError("Invalid range: resistance <= support")

    threshold = range_size * (edge_threshold_pct / 100)

    if current_price > resistance:
        zone = "breakout"
    elif current_price < support:
        zone = "breakdown"
    elif current_price <= support + threshold:
        zone = "near_support"
    elif current_price >= resistance - threshold:
        zone = "near_resistance"
    else:
        zone = "middle"

    return Location(zone=zone, nearest_support=support, nearest_resistance=resistance)
