"""
Combines daily context + 1H location + 1H structure into ONE trade
decision, per strategy doc sections 5-9. No-trade rules take priority
over any signal - the doc is explicit that most of the time the
correct action is no trade at all.
"""
from dataclasses import dataclass
from core.daily_context import classify_daily_context
from core.location_classifier import classify_location
from core.swing_points import find_swing_points
from core.structure_classifier import classify_structure


@dataclass
class TradeSignal:
    direction: str   # "long", "short", "no_trade"
    reason: str
    daily_context: str
    zone: str


def evaluate(daily_candles, hourly_candles, current_price: float) -> TradeSignal:
    context = classify_daily_context(daily_candles)
    location = classify_location(hourly_candles, current_price, edge_threshold_pct=15)

    swings = find_swing_points(hourly_candles, window=2)
    structure = classify_structure(swings)
    recent_labels = [p.label for p in structure if p.label != "first"][-2:]

    if location.zone == "middle":
        return TradeSignal("no_trade", "Price is in the middle of the range - no location edge", context, location.zone)

    if location.zone == "near_support":
        if context == "Bearish":
            return TradeSignal("no_trade", "Daily context is Bearish - counter-trend long at support skipped", context, location.zone)
        if "HL" in recent_labels:
            return TradeSignal("long", "Near support with recent HL - structure confirms buyers stepping in", context, location.zone)
        return TradeSignal("no_trade", "Near support but no HL confirmation yet - waiting for structure", context, location.zone)

    if location.zone == "near_resistance":
        if context == "Bullish":
            return TradeSignal("no_trade", "Daily context is Bullish - counter-trend short at resistance skipped", context, location.zone)
        if "LH" in recent_labels:
            return TradeSignal("short", "Near resistance with recent LH - structure confirms sellers capping price", context, location.zone)
        return TradeSignal("no_trade", "Near resistance but no LH confirmation yet - waiting for structure", context, location.zone)

    return TradeSignal("no_trade", f"Zone is {location.zone} - not handled by this simple ruleset yet", context, location.zone)
