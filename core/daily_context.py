"""
Daily context classifier - answers "what is the environment?" per the
strategy doc, section 2. Uses the same swing/structure pipeline already
built, just applied to daily candles instead of 1H/15M.
"""
from core.structure_classifier import classify_structure
from core.swing_points import find_swing_points


def classify_daily_context(daily_candles, window=2):
    """
    - Bullish: recent highs AND lows are mostly HH/HL
    - Bearish: recent highs AND lows are mostly LH/LL
    - Range: mixed / no consistent direction
    - Transition: too few confirmed swings yet to say either way
    """
    swings = find_swing_points(daily_candles, window=window)
    structure = classify_structure(swings)

    labeled = [p.label for p in structure if p.label != "first"]
    if len(labeled) < 2:
        return "Transition"

    recent = labeled[-4:]
    bullish_count = recent.count("HH") + recent.count("HL")
    bearish_count = recent.count("LH") + recent.count("LL")

    if bullish_count >= len(recent) * 0.75:
        return "Bullish"
    if bearish_count >= len(recent) * 0.75:
        return "Bearish"
    return "Range"