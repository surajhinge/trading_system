"""Trade-quality scoring."""

from dataclasses import dataclass


@dataclass
class TradeScore:
    score: int
    grade: str
    breakdown: dict[str, int]


def calculate_trade_score(
    direction: str,
    daily_context: str,
    location_valid: bool,
    rejection_confirmed: bool,
    structure_confirmed: bool,
    trigger_confirmed: bool,
    volume_confirmed: bool,
    fibonacci_confirmed: bool,
    market_regime: str,
) -> TradeScore:
    """Score a setup out of 100.

    20 daily + 20 location + 15 rejection + 15 structure +
    15 trigger + 5 volume + 5 fib + 5 NIFTY = 100.
    """
    if direction not in ("long", "short"):
        raise ValueError("direction must be 'long' or 'short'")

    breakdown = {
        "daily_trend": 20 if (
            (direction == "long" and daily_context == "Bullish") or
            (direction == "short" and daily_context == "Bearish")
        ) else 0,
        "1h_location": 20 if location_valid else 0,
        "15m_rejection": 15 if rejection_confirmed else 0,
        "structure": 15 if structure_confirmed else 0,
        "trigger": 15 if trigger_confirmed else 0,
        "volume": 5 if volume_confirmed else 0,
        "fibonacci": 5 if fibonacci_confirmed else 0,
        "nifty_regime": 5 if (
            (direction == "long" and market_regime == "Bullish") or
            (direction == "short" and market_regime == "Bearish")
        ) else 0,
    }

    score = sum(breakdown.values())
    grade = "A+" if score >= 80 else "A" if score >= 70 else "B" if score >= 60 else "NO_TRADE"

    return TradeScore(score, grade, breakdown)
