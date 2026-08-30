import pytest
from core.level_engine import Candle, compute_levels


def test_levels_from_single_candle():
    candles = [Candle(high=110, low=95, close=105)]
    levels = compute_levels(candles)
    assert levels.prev_high == 110
    assert levels.prev_low == 95
    assert levels.prev_close == 105


def test_uses_last_candle_when_multiple_given():
    candles = [
        Candle(high=100, low=90, close=95),   # older day — should be ignored
        Candle(high=120, low=100, close=115), # most recent — this one matters
    ]
    levels = compute_levels(candles)
    assert levels.prev_high == 120


def test_empty_list_raises():
    with pytest.raises(ValueError):
        compute_levels([])
