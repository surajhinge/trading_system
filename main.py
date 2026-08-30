"""
End-to-end pipeline run, Milestones 1-4:
watchlist (live price) -> historical data -> level engine -> setup detector.

Still no alerts, no human confirmation, no orders yet — this just proves
the four pieces we've already tested individually work correctly together.
"""

import os
from dotenv import load_dotenv

from data.watchlist import WATCHLIST, get_ltp
from data.historical_data import fetch_daily_candles
from core.level_engine import compute_levels
from core.setup_detector import detect_breakout


def run():
    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    for symbol, instrument_key in WATCHLIST.items():
        current_price = get_ltp(token, instrument_key)
        candles = fetch_daily_candles(token, instrument_key)
        levels = compute_levels(candles)
        setup = detect_breakout(symbol, current_price, levels)

        status = "🔥 TRIGGERED" if setup.triggered else "—"
        print(f"{symbol}: ₹{current_price} | prev_high ₹{levels.prev_high} | {status} ({setup.reason})")


if __name__ == "__main__":
    run()