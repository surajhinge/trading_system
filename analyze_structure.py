import os
from dotenv import load_dotenv

from data.historical_data import fetch_candles
from data.watchlist import WATCHLIST, get_ltp
from core.trade_signal import evaluate
from core.position_sizing import calculate_position_size
from core.target_calculator import find_next_target, build_trade_plan

ACCOUNT_EQUITY = 10000


def analyze(symbol, instrument_key, access_token):
    print(f"\n--- {symbol} ---")
    daily_candles = fetch_candles(access_token, instrument_key, unit="days", interval="1", lookback_days=30)
    hourly_candles = fetch_candles(access_token, instrument_key, unit="hours", interval="1", lookback_days=20)
    fifteen_min_candles = fetch_candles(access_token, instrument_key, unit="minutes", interval="15", lookback_days=5)
    current_price = get_ltp(access_token, instrument_key)

    signal = evaluate(daily_candles, hourly_candles, fifteen_min_candles, current_price)
    print(f"Daily context: {signal.daily_context} | Zone: {signal.zone}")
    print(f"Signal: {signal.direction.upper()} - {signal.reason}")

    if signal.direction == "no_trade":
        return

    target = find_next_target(hourly_candles, current_price, signal.direction)
    if target is None:
        print("No next-level target found - cannot size a trade plan")
        return

    size = calculate_position_size(ACCOUNT_EQUITY, current_price, signal.stop_price)
    plan = build_trade_plan(entry=current_price, stop=signal.stop_price, target=target, quantity=size.quantity)

    if not plan.meets_minimum_rr:
        print(f"Trade REJECTED - R:R is 1:{plan.risk_reward_ratio}, below the required 1:2 minimum")
        return

    print(f"Entry: Rs.{plan.entry} | Stop: Rs.{plan.stop} | Target: Rs.{plan.target}")
    print(f"Quantity: {plan.quantity} | Risk: Rs.{plan.risk_amount} | Reward: Rs.{plan.reward_amount} | R:R = 1:{plan.risk_reward_ratio}")


if __name__ == "__main__":
    load_dotenv()
    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")
    print(f"Watchlist has {len(WATCHLIST)} symbols: {list(WATCHLIST.keys())}")
    for symbol, key in WATCHLIST.items():
        analyze(symbol, key, token)
