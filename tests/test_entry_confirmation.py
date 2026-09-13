from core.level_engine import Candle
from core.entry_confirmation import (
    detect_bullish_rejection,
    detect_bearish_rejection,
)


def test_detects_bullish_rejection_at_support():
    candles = [
        Candle(
            open=100,
            high=103,
            low=96,
            close=102,
        )
    ]

    assert detect_bullish_rejection(
        candles,
        support_price=98,
    )


def test_rejects_bullish_candle_that_does_not_test_support():
    candles = [
        Candle(
            open=101,
            high=105,
            low=100,
            close=104,
        )
    ]

    assert not detect_bullish_rejection(
        candles,
        support_price=95,
    )


def test_detects_bearish_rejection_at_resistance():
    candles = [
        Candle(
            open=102,
            high=106,
            low=99,
            close=100,
        )
    ]

    assert detect_bearish_rejection(
        candles,
        resistance_price=104,
    )


def test_rejects_bearish_candle_that_does_not_test_resistance():
    candles = [
        Candle(
            open=100,
            high=102,
            low=98,
            close=99,
        )
    ]

    assert not detect_bearish_rejection(
        candles,
        resistance_price=108,
    )
