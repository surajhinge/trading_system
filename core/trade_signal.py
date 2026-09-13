from dataclasses import dataclass
from core.daily_context import classify_daily_context
from core.location_classifier import classify_location
from core.entry_confirmation import confirm_long_entry, confirm_short_entry
from core.fibonacci import compute_fib_zone


@dataclass
class TradeSignal:
    direction: str
    reason: str
    daily_context: str
    zone: str
    trigger_price: float = None
    stop_price: float = None


def evaluate(daily_candles, hourly_candles, fifteen_min_candles, current_price):
    context = classify_daily_context(daily_candles)
    location = classify_location(hourly_candles, current_price, edge_threshold_pct=15)

    if location.zone == "middle":
        return TradeSignal("no_trade", "Price is in the middle of the range - no location edge", context, location.zone)

    if location.zone in ("near_untested_low", "near_untested_high"):
        touches = location.support_touches if "low" in location.zone else location.resistance_touches
        return TradeSignal("no_trade", f"Level only touched {touches} time(s) - not a proven level yet", context, location.zone)

    if location.zone == "near_support":
        if context == "Bearish":
            return TradeSignal("no_trade", "Daily context is Bearish - counter-trend long at support skipped", context, location.zone)

        entry = confirm_long_entry(fifteen_min_candles)
        if not entry.confirmed:
            return TradeSignal("no_trade", entry.reason, context, location.zone)

        fib = compute_fib_zone(location.nearest_support, location.nearest_resistance, current_price, "long")
        if not fib.in_golden_zone:
            return TradeSignal("no_trade", f"Structure confirmed HL, but price is at {fib.current_retracement_pct*100:.1f}% retracement - not in Fib golden zone (50-61.8%)", context, location.zone)

        return TradeSignal("long", f"{entry.reason} AND Fib golden zone confirmed ({fib.current_retracement_pct*100:.1f}% retracement)", context, location.zone, entry.trigger_price, entry.stop_price)

    if location.zone == "near_resistance":
        if context == "Bullish":
            return TradeSignal("no_trade", "Daily context is Bullish - counter-trend short at resistance skipped", context, location.zone)

        entry = confirm_short_entry(fifteen_min_candles)
        if not entry.confirmed:
            return TradeSignal("no_trade", entry.reason, context, location.zone)

        fib = compute_fib_zone(location.nearest_support, location.nearest_resistance, current_price, "short")
        if not fib.in_golden_zone:
            return TradeSignal("no_trade", f"Structure confirmed LH, but price is at {fib.current_retracement_pct*100:.1f}% retracement - not in Fib golden zone (50-61.8%)", context, location.zone)

        return TradeSignal("short", f"{entry.reason} AND Fib golden zone confirmed ({fib.current_retracement_pct*100:.1f}% retracement)", context, location.zone, entry.trigger_price, entry.stop_price)

    return TradeSignal("no_trade", f"Zone is {location.zone} - not handled by this ruleset yet", context, location.zone)
