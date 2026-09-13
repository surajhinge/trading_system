"""
Full decision pipeline on REAL data: daily context + 1H location +
1H structure -> trade signal -> position size, per your strategy doc.
"""

import os
from dotenv import load_dotenv

from data.historical_data import fetch_candles
from data.watchlist import WATCHLIST, get_ltp
from core.swing_points import find_swing_points
from core.structure_classifier import classify_structure
from core.trade_signal import evaluate
from core.position_sizing import calculate_position_size

ACCOUNT_EQUITY = 10000  # paper trading equity per your doc's section 17


def analyze(symbol: str, instrument_key: str, access_token: str):
    print(f"\n--- {symbol} ---")

    daily_candles = fetch_candles(access_token, instrument_key, unit="days", interval="1", lookback_days=30)
    hourly_candles = fetch_candles(access_token, instrument_key, unit="hours", interval="1", lookback_days=20)
    current_price = get_ltp(access_token, instrument_key)

    signal = evaluate(daily_candles, hourly_candles, current_price)
    print(f"Daily context: {signal.daily_context} | Zone: {signal.zone}")
    print(f"Signal: {signal.direction.upper()} - {signal.reason}")

    if signal.direction == "no_trade":
        return

    # Stop loss = the most recent swing low (for longs) or swing high (for shorts)
    # that formed the confirming HL/LH - i.e. the structural invalidation point.
    swings = find_swing_points(hourly_candles, window=2)
    structure = classify_structure(swings)

    if signal.direction == "long":
        recent_lows = [p.swing.price for p in structure if p.swing.kind == "low"]
        stop_loss = min(recent_lows[-2:])  # a bit below the HL that confirmed the setup
    else:
        recent_highs = [p.swing.price for p in structure if p.swing.kind == "high"]
        stop_loss = max(recent_highs[-2:])

    size = calculate_position_size(ACCOUNT_EQUITY, current_price, stop_loss)
    print(f"Entry: Rs.{current_price} | Stop: Rs.{stop_loss} | Risk: Rs.{size.risk_amount} | Quantity: {size.quantity}")


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    for symbol, key in WATCHLIST.items():
        analyze(symbol, key, token)
