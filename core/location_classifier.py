"""
Location classifier v2 - now requires a support/resistance level to
have been TESTED (touched) at least twice before treating it as real.
A single recent extreme (e.g. the newest low of an ongoing downtrend)
is labeled "near_untested_low"/"near_untested_high" instead of
"near_support"/"near_resistance" - the doc's no-trade rules should
skip these, since they aren't proven levels yet.
"""
from dataclasses import dataclass
from core.swing_points import find_swing_points


@dataclass
class Location:
    zone: str  # near_support, near_resistance, near_untested_low, near_untested_high, middle, breakout, breakdown
    nearest_support: float
    nearest_resistance: float
    support_touches: int
    resistance_touches: int


def _cluster_levels(prices, tolerance_pct):
    """Group nearby prices into clusters, each representing one 'level'."""
    clusters = []
    for p in sorted(prices):
        placed = False
        for c in clusters:
            if abs(p - c["avg"]) / c["avg"] * 100 <= tolerance_pct:
                c["touches"].append(p)
                c["avg"] = sum(c["touches"]) / len(c["touches"])
                placed = True
                break
        if not placed:
            clusters.append({"touches": [p], "avg": p})
    return clusters


def classify_location(candles, current_price: float, window: int = 2, edge_threshold_pct: float = 15.0,
                       min_touches: int = 2, cluster_tolerance_pct: float = 0.5):
    swings = find_swing_points(candles, window=window)
    highs = [s.price for s in swings if s.kind == "high"]
    lows = [s.price for s in swings if s.kind == "low"]

    if not highs or not lows:
        raise ValueError("Not enough swing data to classify location")

    resistance_raw = max(highs)
    support_raw = min(lows)
    range_size = resistance_raw - support_raw
    if range_size <= 0:
        raise ValueError("Invalid range: resistance <= support")
    threshold = range_size * (edge_threshold_pct / 100)

    low_clusters = _cluster_levels(lows, cluster_tolerance_pct)
    high_clusters = _cluster_levels(highs, cluster_tolerance_pct)

    support_cluster = min(low_clusters, key=lambda c: abs(c["avg"] - support_raw))
    resistance_cluster = min(high_clusters, key=lambda c: abs(c["avg"] - resistance_raw))
    support_touches = len(support_cluster["touches"])
    resistance_touches = len(resistance_cluster["touches"])

    if current_price > resistance_raw:
        zone = "breakout"
    elif current_price < support_raw:
        zone = "breakdown"
    elif current_price <= support_raw + threshold:
        zone = "near_support" if support_touches >= min_touches else "near_untested_low"
    elif current_price >= resistance_raw - threshold:
        zone = "near_resistance" if resistance_touches >= min_touches else "near_untested_high"
    else:
        zone = "middle"

    return Location(zone=zone, nearest_support=support_raw, nearest_resistance=resistance_raw,
                     support_touches=support_touches, resistance_touches=resistance_touches)
