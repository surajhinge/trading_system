from core.level_engine import Candle

from core.trade_signal import evaluate

from core.position_sizing import calculate_position_size


def make_series(raw):
    return [
        Candle(
            high=p + 1.5,
            low=p - 1.5,
            close=p,
        )
        for p in raw
    ]


def make_ohlc(open_price, high, low, close):
    return Candle(
        open=open_price,
        high=high,
        low=low,
        close=close,
    )


def test_middle_of_range_is_no_trade():

    daily = make_series(
        [1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2
    )

    hourly = make_series(
        [
            1288, 1284, 1281, 1283, 1287,
            1291, 1289, 1285, 1283, 1286,
            1290, 1294, 1292, 1288, 1284,
            1289, 1293, 1297, 1295, 1291,
        ]
    )

    # 15M data does not matter because location is "middle".
    # evaluate() should stop before checking 15M confirmation.
    fifteen = make_series([1289] * 10)

    signal = evaluate(
        daily,
        hourly,
        fifteen,
        current_price=1289,
    )

    assert signal.direction == "no_trade"
    assert signal.zone == "middle"


def test_near_support_with_15m_rejection_hl_and_trigger_breaks_long():

    daily = make_series(
        [1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2
    )

    hourly = make_series(
        [
            1288, 1284, 1281, 1283, 1287,
            1291, 1289, 1285, 1283, 1286,
            1290, 1294, 1292, 1288, 1284,
            1289, 1293, 1297, 1295, 1291,
        ]
    )

    # 15M structure:
    #
    # 1281 -> support area
    # 1283 -> bullish rejection
    # 1291 -> swing high / trigger
    # 1284 -> HL candidate
    # 1286 -> confirmation candle
    # 1288 -> confirmation candle
    # 1294 -> trigger breakout
    #
    # window=2 requires two candles AFTER the HL candidate
    # before the HL can be confirmed as a swing low.

    fifteen = [
        # Initial move toward support
        make_ohlc(1285, 1286, 1282, 1284),

        # Support test
        make_ohlc(1283, 1284, 1279, 1281),

        # Bullish rejection of support
        make_ohlc(1280, 1284, 1277, 1283),

        # Recovery
        make_ohlc(1283, 1288, 1282, 1287),

        # Swing high / trigger
        make_ohlc(1287, 1292, 1286, 1291),

        # Pullback
        make_ohlc(1290, 1291, 1285, 1287),

        # HL candidate
        make_ohlc(1287, 1288, 1282, 1284),

        # Candle required to confirm HL
        make_ohlc(1284, 1287, 1283, 1286),

        # Second confirmation candle
        make_ohlc(1286, 1289, 1285, 1288),

        # Trigger breakout
        make_ohlc(1288, 1296, 1287, 1294),
    ]

    signal = evaluate(
        daily,
        hourly,
        fifteen,
        current_price=1294.0,
    )

    assert signal.direction == "long"
    assert signal.trigger_price is not None
    assert signal.stop_price is not None


def test_near_support_without_15m_confirmation_is_no_trade():

    daily = make_series(
        [1290, 1280, 1291, 1279, 1292, 1281, 1289, 1280, 1293, 1278] * 2
    )

    hourly = make_series(
        [
            1288, 1284, 1281, 1283, 1287,
            1291, 1289, 1285, 1283, 1286,
            1290, 1294, 1292, 1288, 1284,
            1289, 1293, 1297, 1295, 1291,
        ]
    )

    # Flat 15M data - no swings and therefore no HL confirmation.
    fifteen = make_series([1281] * 10)

    signal = evaluate(
        daily,
        hourly,
        fifteen,
        current_price=1281.0,
    )

    assert signal.direction == "no_trade"


def test_position_sizing_risks_exactly_one_percent():

    size = calculate_position_size(
        account_equity=10000,
        entry_price=1281.0,
        stop_loss_price=1278.0,
    )

    assert size.risk_amount == 100.0
    assert size.quantity == 33
