"""
Runs daily context classification + swing-point detection + HH/HL/LH/LL
structure classification on REAL historical data for your watchlist.
This is actual pipeline output, not a unit test.
"""

import os
from dotenv import load_dotenv

from data.historical_data import fetch_candles
from data.watchlist import WATCHLIST
from core.swing_points import find_swing_points
from core.structure_classifier import classify_structure
from core.daily_context import classify_daily_context


def analyze(symbol: str, instrument_key: str, access_token: str):
    print(f"\n--- {symbol} ---")

    daily_candles = fetch_candles(access_token, instrument_key, unit="days", interval="1", lookback_days=30)
    print(f"Daily context: {classify_daily_context(daily_candles)}")

    print(f"\n1H structure (last 20 days):")
    candles = fetch_candles(access_token, instrument_key, unit="hours", interval="1", lookback_days=20)
    swings = find_swing_points(candles, window=2)
    structure = classify_structure(swings)

    for point in structure:
        print(f"idx={point.swing.index:>3}  {point.swing.kind:<4}  price=₹{point.swing.price:<10}  label={point.label}")


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    for symbol, key in WATCHLIST.items():
        analyze(symbol, key, token)
