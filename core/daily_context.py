"""
Daily context classifier.

Answers:
    "What is the current daily market environment?"

Used for:
    - Stock daily trend
    - NIFTY market regime
    - Long/short directional filtering

Strategy:
    Bullish    -> HH + HL structure dominates
    Bearish    -> LH + LL structure dominates
    Range      -> mixed structure
    Transition -> insufficient confirmed structure
"""

from core.structure_classifier import classify_structure
from core.swing_points import find_swing_points


def classify_daily_context(daily_candles, window=2):
    """
    Classify the daily market environment.

    Returns:
        "Bullish"
        "Bearish"
        "Range"
        "Transition"
    """

    # ---------------------------------------------------------
    # 1. Basic validation
    # ---------------------------------------------------------
    if not daily_candles:
        return "Transition"

    if len(daily_candles) < (window * 2 + 3):
        return "Transition"

    # ---------------------------------------------------------
    # 2. Find confirmed daily swing points
    # ---------------------------------------------------------
    swings = find_swing_points(
        daily_candles,
        window=window
    )

    if not swings:
        return "Transition"

    # ---------------------------------------------------------
    # 3. Classify swing structure
    # ---------------------------------------------------------
    structure = classify_structure(swings)

    if not structure:
        return "Transition"

    # Remove the first swing because it has no previous
    # swing for comparison.
    labeled = [
        point.label
        for point in structure
        if point.label in {"HH", "HL", "LH", "LL"}
    ]

    # We need enough structure to make a meaningful decision.
    if len(labeled) < 3:
        return "Transition"

    # ---------------------------------------------------------
    # 4. Look at the most recent confirmed structure
    # ---------------------------------------------------------
    recent = labeled[-6:]

    bullish_count = (
        recent.count("HH") +
        recent.count("HL")
    )

    bearish_count = (
        recent.count("LH") +
        recent.count("LL")
    )

    total = len(recent)

    bullish_ratio = bullish_count / total
    bearish_ratio = bearish_count / total

    # ---------------------------------------------------------
    # 5. Determine daily environment
    # ---------------------------------------------------------
    if bullish_ratio >= 0.67 and bullish_count > bearish_count:
        return "Bullish"

    if bearish_ratio >= 0.67 and bearish_count > bullish_count:
        return "Bearish"

    return "Range"
