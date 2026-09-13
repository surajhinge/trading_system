from core.level_engine import Candle
from core.location_classifier import classify_location


def make_series():
    raw = [1288, 1284, 1281, 1283, 1287, 1291, 1289, 1285, 1283, 1286,
           1290, 1294, 1292, 1288, 1284, 1289, 1293, 1297, 1295, 1291]
    return [Candle(high=p + 1.5, low=p - 1.5, close=p) for p in raw]


def test_price_near_low_is_near_support():
    loc = classify_location(make_series(), current_price=1282, edge_threshold_pct=15)
    assert loc.zone == "near_support"


def test_price_near_high_is_near_resistance():
    loc = classify_location(make_series(), current_price=1296, edge_threshold_pct=15)
    assert loc.zone == "near_resistance"


def test_price_between_is_middle():
    loc = classify_location(make_series(), current_price=1289, edge_threshold_pct=15)
    assert loc.zone == "middle"


def test_price_above_resistance_is_breakout():
    loc = classify_location(make_series(), current_price=1300, edge_threshold_pct=15)
    assert loc.zone == "breakout"
