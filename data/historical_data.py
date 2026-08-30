"""
Fetches daily historical candles from Upstox and converts them into
the Candle shape core.level_engine expects. Kept separate from
watchlist.py (live LTP) since historical vs live are different concerns
even though they hit the same broker.
"""

import requests
from datetime import date, timedelta
from core.level_engine import Candle

HISTORICAL_URL = "https://api.upstox.com/v3/historical-candle/{key}/days/1/{to_date}/{from_date}"


def fetch_daily_candles(access_token: str, instrument_key: str, lookback_days: int = 10) -> list[Candle]:
    """
    Fetch the last `lookback_days` of daily candles for one instrument.
    Returns oldest -> newest, matching what level_engine.compute_levels expects.
    """
    to_date = date.today().isoformat()
    from_date = (date.today() - timedelta(days=lookback_days)).isoformat()

    url = HISTORICAL_URL.format(key=instrument_key, to_date=to_date, from_date=from_date)
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    raw_candles = resp.json()["data"]["candles"]

    # Upstox returns newest-first: each row is [timestamp, open, high, low, close, volume, oi]
    # Reverse so the LAST element is the most recent completed day, as level_engine expects.
    raw_candles.reverse()

    return [
        Candle(high=row[2], low=row[3], close=row[4])
        for row in raw_candles
    ]


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from core.level_engine import compute_levels

    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    candles = fetch_daily_candles(token, "NSE_EQ|INE002A01018")  # RELIANCE
    levels = compute_levels(candles)
    print(f"Prev High: ₹{levels.prev_high}")
    print(f"Prev Low:  ₹{levels.prev_low}")
    print(f"Prev Close: ₹{levels.prev_close}")
