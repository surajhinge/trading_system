from core.level_engine import Candle
from core.trade_signal import evaluate
from core.position_sizing import calculate_position_size


def make_series(raw):
    return [Candle(high=p + 1.5, low=p - 1.5, close=p) for p in raw]


def test_middle_of_range_is_no_trade():
    daily = make_series([1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2)
    hourly = make_series([1288, 1284, 1281, 1283, 1287, 1291, 1289, 1285, 1283, 1286,
                          1290, 1294, 1292, 1288, 1284, 1289, 1293, 1297, 1295, 1291])
    # 15M content doesn't matter for this case - location is "middle", so
    # evaluate() should short-circuit before ever looking at 15M data.
    fifteen = make_series([1289] * 10)
    signal = evaluate(daily, hourly, fifteen, current_price=1289)
    assert signal.direction == "no_trade"
    assert signal.zone == "middle"


def test_near_support_with_15m_hl_triggers_long():
    daily = make_series([1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2)
    hourly = make_series([1288, 1284, 1281, 1283, 1287, 1291, 1289, 1285, 1283, 1286,
                          1290, 1294, 1292, 1288, 1284, 1289, 1293, 1297, 1295, 1291])
    # This 15M series is the confirmed-HL pattern from entry_confirmation's own tests
    fifteen = make_series([1284, 1281, 1279, 1282, 1287, 1291, 1289, 1285, 1283, 1286,
                          1290, 1294, 1292, 1288, 1284, 1289, 1293])
    signal = evaluate(daily, hourly, fifteen, current_price=1281.0)
    assert signal.direction == "long"
    assert signal.trigger_price is not None


def test_near_support_without_15m_confirmation_is_no_trade():
    daily = make_series([1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2)
    hourly = make_series([1288, 1284, 1281, 1283, 1287, 1291, 1289, 1285, 1283, 1286,
                          1290, 1294, 1292, 1288, 1284, 1289, 1293, 1297, 1295, 1291])
    # Flat 15M data - no swings at all, so no HL can ever be confirmed
    fifteen = make_series([1281] * 10)
    signal = evaluate(daily, hourly, fifteen, current_price=1281.0)
    assert signal.direction == "no_trade"


def test_position_sizing_risks_exactly_one_percent():
    size = calculate_position_size(account_equity=10000, entry_price=1281.0, stop_loss_price=1278.0)
    assert size.risk_amount == 100.0
    assert size.quantity == 33
