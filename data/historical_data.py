"""
Fetches historical candles from Upstox at any timeframe (days, hours, minutes)
and converts them into the Candle shape used everywhere else in the system.
"""

import requests
from datetime import date, timedelta
from core.level_engine import Candle

HISTORICAL_URL = "https://api.upstox.com/v3/historical-candle/{key}/{unit}/{interval}/{to_date}/{from_date}"


def fetch_candles(access_token: str, instrument_key: str, unit: str = "days", interval: str = "1", lookback_days: int = 10) -> list[Candle]:
    """
    unit: "days", "hours", or "minutes" (per Upstox V3 API)
    interval: the number within that unit, e.g. unit="hours", interval="1" -> 1H candles
    """
    to_date = date.today().isoformat()
    from_date = (date.today() - timedelta(days=lookback_days)).isoformat()

    url = HISTORICAL_URL.format(key=instrument_key, unit=unit, interval=interval, to_date=to_date, from_date=from_date)
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}

    resp = requests.get(url, headers=headers, timeout=5)
    resp.raise_for_status()
    raw_candles = resp.json()["data"]["candles"]
    raw_candles.reverse()  # Upstox returns newest-first; we want oldest-first

    return [Candle(high=row[2], low=row[3], close=row[4]) for row in raw_candles]


def fetch_daily_candles(access_token: str, instrument_key: str, lookback_days: int = 10) -> list[Candle]:
    return fetch_candles(access_token, instrument_key, unit="days", interval="1", lookback_days=lookback_days)


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
