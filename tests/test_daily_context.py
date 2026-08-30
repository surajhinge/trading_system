from core.level_engine import Candle
from core.daily_context import classify_daily_context


def make_candle(price):
    return Candle(high=price + 1.5, low=price - 1.5, close=price)


def test_trending_series_is_bullish():
    raw = [1288, 1284, 1281, 1283, 1287, 1291, 1289, 1285, 1283, 1286,
           1290, 1294, 1292, 1288, 1284, 1289, 1293, 1297, 1295, 1291,
           1296, 1300, 1298, 1294, 1290]
    candles = [make_candle(p) for p in raw]
    assert classify_daily_context(candles) == "Bullish"


def test_choppy_series_is_range():
    raw = [1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278,
           1290, 1282, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278]
    candles = [make_candle(p) for p in raw]
    assert classify_daily_context(candles) == "Range"


def test_too_few_swings_is_transition():
    candles = [make_candle(p) for p in [1290, 1291, 1292]]
    assert classify_daily_context(candles) == "Transition"
