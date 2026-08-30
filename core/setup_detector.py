"""
Setup Detector: compares live price against precomputed levels and
flags a simple breakout setup. Deliberately dumb for now — one rule,
easy to verify by hand — we add complexity only once this is trusted.
"""

from dataclasses import dataclass
from core.level_engine import Levels


@dataclass
class Setup:
    symbol: str
    triggered: bool
    reason: str


def detect_breakout(symbol: str, current_price: float, levels: Levels) -> Setup:
    """
    Simplest possible setup: price trading above yesterday's high.
    This is intentionally the most basic rule in your pipeline diagram —
    real strategies (volume confirmation, retest, etc.) come later,
    layered on top of a detector we already trust.
    """
    if current_price > levels.prev_high:
        return Setup(
            symbol=symbol,
            triggered=True,
            reason=f"Price {current_price} broke above prev_high {levels.prev_high}",
        )
    return Setup(symbol=symbol, triggered=False, reason="No breakout")
