"""Upstox historical OHLCV data layer for Daily, 1H and 15M candles."""

from datetime import date, timedelta, datetime
import requests

from core.level_engine import Candle

HISTORICAL_URL = "https://api.upstox.com/v3/historical-candle/{key}/{unit}/{interval}/{to_date}/{from_date}"


def fetch_candles(access_token: str, instrument_key: str, unit: str = "days", interval: str = "1", lookback_days: int = 30) -> list[Candle]:
    if not access_token:
        raise ValueError("Upstox access token is required")
    if not instrument_key:
        raise ValueError("instrument_key is required")
    if lookback_days <= 0:
        raise ValueError("lookback_days must be greater than zero")

    to_date = date.today()
    from_date = to_date - timedelta(days=lookback_days)
    url = HISTORICAL_URL.format(
        key=instrument_key,
        unit=unit,
        interval=interval,
        to_date=to_date.isoformat(),
        from_date=from_date.isoformat(),
    )
    headers = {"Accept": "application/json", "Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    raw_candles = response.json().get("data", {}).get("candles", [])
    if not raw_candles:
        raise ValueError(f"No historical candles returned for {instrument_key} {unit} {interval}")

    raw_candles.reverse()
    candles = []

    for row in raw_candles:
        if len(row) < 6:
            raise ValueError("Unexpected Upstox candle format")

        timestamp = None
        if row[0]:
            try:
                timestamp = datetime.fromisoformat(str(row[0]).replace("Z", "+00:00"))
            except ValueError:
                pass

        candles.append(Candle(
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
            timestamp=timestamp,
        ))

    return candles


def fetch_daily_candles(access_token: str, instrument_key: str, lookback_days: int = 120) -> list[Candle]:
    return fetch_candles(access_token, instrument_key, "days", "1", lookback_days)


def fetch_hourly_candles(access_token: str, instrument_key: str, lookback_days: int = 30) -> list[Candle]:
    return fetch_candles(access_token, instrument_key, "hours", "1", lookback_days)


def fetch_fifteen_minute_candles(access_token: str, instrument_key: str, lookback_days: int = 10) -> list[Candle]:
    return fetch_candles(access_token, instrument_key, "minutes", "15", lookback_days)
