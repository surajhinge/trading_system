"""
Step 1: Watchlist — fetch and store current market data for a small set of symbols.
No trading logic here. Just: can we get a reliable price for a symbol, on demand.
"""

import requests

# Upstox uses instrument keys, not plain tickers — this is the NSE_EQ format.
# For now hardcode 2-3 symbols; we'll load this from a config file later.
WATCHLIST = {
    "RELIANCE": "NSE_EQ|INE002A01018",
    "TCS": "NSE_EQ|INE467B01029",
}

UPSTOX_QUOTE_URL = "https://api.upstox.com/v2/market-quote/ltp"


def get_ltp(access_token: str, instrument_key: str) -> float:
    """Fetch Last Traded Price for one instrument. Raises on failure — no silent None."""
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    params = {"instrument_key": instrument_key}
    resp = requests.get(UPSTOX_QUOTE_URL, headers=headers, params=params, timeout=5)
    resp.raise_for_status()
    data = resp.json()["data"]
    # response is keyed by a slightly different symbol format — grab the first (only) entry
    quote = next(iter(data.values()))
    return quote["last_price"]


def refresh_watchlist(access_token: str) -> dict:
    """Return {symbol: price} for everything in WATCHLIST."""
    prices = {}
    for symbol, key in WATCHLIST.items():
        prices[symbol] = get_ltp(access_token, key)
    return prices


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    prices = refresh_watchlist(token)
    for sym, price in prices.items():
        print(f"{sym}: ₹{price}")
