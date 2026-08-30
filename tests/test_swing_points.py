from core.level_engine import Candle
from core.swing_points import find_swing_points


def make_candle(high, low):
    return Candle(high=high, low=low, close=(high + low) / 2)


def test_detects_single_swing_high():
    # candle at index 2 (high=110) is higher than both neighbors on each side
    candles = [
        make_candle(100, 95), make_candle(102, 97),
        make_candle(110, 105),  # <- swing high
        make_candle(103, 98), make_candle(101, 96),
    ]
    swings = find_swing_points(candles, window=2)
    assert len(swings) == 1
    assert swings[0].kind == "high"
    assert swings[0].price == 110


def test_detects_single_swing_low():
    candles = [
        make_candle(100, 95), make_candle(98, 90),
        make_candle(97, 80),  # <- swing low
        make_candle(99, 88), make_candle(101, 92),
    ]
    swings = find_swing_points(candles, window=2)
    assert len(swings) == 1
    assert swings[0].kind == "low"
    assert swings[0].price == 80


def test_flat_series_has_no_swings():
    # no candle stands out from its neighbors -> nothing should trigger
    candles = [make_candle(100, 95) for _ in range(6)]
    swings = find_swing_points(candles, window=2)
    assert len(swings) == 0
