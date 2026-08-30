from core.level_engine import Levels
from core.setup_detector import detect_breakout


def test_price_above_prev_high_triggers():
    levels = Levels(prev_high=110, prev_low=95, prev_close=105)
    setup = detect_breakout("RELIANCE", current_price=112, levels=levels)
    assert setup.triggered is True


def test_price_below_prev_high_does_not_trigger():
    levels = Levels(prev_high=110, prev_low=95, prev_close=105)
    setup = detect_breakout("RELIANCE", current_price=108, levels=levels)
    assert setup.triggered is False


def test_price_exactly_at_prev_high_does_not_trigger():
    # boundary case: "above" should mean strictly above, not equal
    levels = Levels(prev_high=110, prev_low=95, prev_close=105)
    setup = detect_breakout("RELIANCE", current_price=110, levels=levels)
    assert setup.triggered is False
