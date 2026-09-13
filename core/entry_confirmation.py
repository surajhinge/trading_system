from dataclasses import dataclass
from core.swing_points import find_swing_points
from core.structure_classifier import classify_structure


@dataclass
class EntryConfirmation:
    confirmed: bool
    reason: str
    trigger_price: float | None   # break level to enter on
    stop_price: float | None      # the ACTUAL structural HL/LH price - the real invalidation point


def confirm_long_entry(fifteen_min_candles, window: int = 2) -> EntryConfirmation:
    swings = find_swing_points(fifteen_min_candles, window=window)
    structure = classify_structure(swings)
    lows = [p for p in structure if p.swing.kind == "low"]
    highs = [p for p in structure if p.swing.kind == "high"]

    if len(lows) < 2:
        return EntryConfirmation(False, "Not enough 15M swing lows yet to confirm HL", None, None)

    last_low = lows[-1]
    if last_low.label != "HL":
        return EntryConfirmation(False, f"Most recent 15M low is {last_low.label}, not HL - no confirmation yet", None, None)

    prior_high_candidates = [h for h in highs if h.swing.index < last_low.swing.index]
    if not prior_high_candidates:
        return EntryConfirmation(False, "HL confirmed but no prior swing high to use as break level", None, None)

    trigger_price = prior_high_candidates[-1].swing.price
    stop_price = last_low.swing.price
    return EntryConfirmation(True, "15M HL confirmed - waiting for break above trigger to enter", trigger_price, stop_price)


def confirm_short_entry(fifteen_min_candles, window: int = 2) -> EntryConfirmation:
    swings = find_swing_points(fifteen_min_candles, window=window)
    structure = classify_structure(swings)
    lows = [p for p in structure if p.swing.kind == "low"]
    highs = [p for p in structure if p.swing.kind == "high"]

    if len(highs) < 2:
        return EntryConfirmation(False, "Not enough 15M swing highs yet to confirm LH", None, None)

    last_high = highs[-1]
    if last_high.label != "LH":
        return EntryConfirmation(False, f"Most recent 15M high is {last_high.label}, not LH - no confirmation yet", None, None)

    prior_low_candidates = [l for l in lows if l.swing.index < last_high.swing.index]
    if not prior_low_candidates:
        return EntryConfirmation(False, "LH confirmed but no prior swing low to use as break level", None, None)

    trigger_price = prior_low_candidates[-1].swing.price
    stop_price = last_high.swing.price
    return EntryConfirmation(True, "15M LH confirmed - waiting for break below trigger to enter", trigger_price, stop_price)
