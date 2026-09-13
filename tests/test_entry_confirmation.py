from core.level_engine import Candle
from core.entry_confirmation import confirm_long_entry, confirm_short_entry


def test_confirms_long_on_higher_low():
    raw = [1284, 1281, 1279, 1282, 1287, 1291, 1289, 1285, 1283, 1286,
           1290, 1294, 1292, 1288, 1284, 1289, 1293]
    candles = [Candle(high=p + 1, low=p - 1, close=p) for p in raw]
    result = confirm_long_entry(candles)
    assert result.confirmed is True
    assert result.trigger_price is not None


def test_confirms_short_on_lower_high():
    raw = [1296, 1299, 1301, 1298, 1293, 1289, 1291, 1295, 1297, 1294,
           1290, 1286, 1288, 1292, 1296, 1291, 1287]
    candles = [Candle(high=p + 1, low=p - 1, close=p) for p in raw]
    result = confirm_short_entry(candles)
    assert result.confirmed is True
    assert result.trigger_price is not None
