"""Run the complete trading-analysis pipeline and print all key details."""

import os

from dotenv import load_dotenv

from data.watchlist import WATCHLIST, get_ltp
from data.historical_data import (
    fetch_daily_candles,
    fetch_hourly_candles,
    fetch_fifteen_minute_candles,
)
from core.trade_signal import evaluate


NIFTY_50_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"
ACCOUNT_EQUITY = 10_000.0
RISK_PERCENT = 1.0


def _money(value):
    return f"₹{value:.2f}" if value is not None else "N/A"


def print_signal(symbol, price, signal):
    print("\n" + "=" * 80)
    print(f"{symbol} | CURRENT PRICE: {_money(price)}")
    print("=" * 80)

    print(f"STATUS              : {signal.status}")
    print(f"DIRECTION           : {signal.direction.upper()}")
    print(f"REASON              : {signal.reason}")
    print()

    print("--- MARKET CONTEXT ---")
    print(f"Daily context       : {signal.daily_context}")
    print(f"NIFTY regime        : {signal.nifty_regime}")
    print()

    print("--- 1H LOCATION ---")
    print(f"Zone                : {signal.zone}")
    print(f"Support             : {_money(signal.support)}")
    print(f"Resistance          : {_money(signal.resistance)}")
    print(f"Support touches     : {signal.support_touches}")
    print(f"Resistance touches  : {signal.resistance_touches}")
    print()

    print("--- 15M CONFIRMATION ---")
    print(f"Rejection           : {'YES' if signal.rejection_confirmed else 'NO'}")
    print(f"Structure HL/LH     : {'YES' if signal.structure_confirmed else 'NO'}")
    print(f"Trigger broken      : {'YES' if signal.trigger_confirmed else 'NO'}")
    print(f"Trigger price       : {_money(signal.trigger_price)}")
    print(f"Stop loss           : {_money(signal.stop_price)}")
    print()

    print("--- CONFLUENCE ---")
    print(f"Volume confirmation : {'YES' if signal.volume_confirmed else 'NO'}")
    print(f"Volume ratio        : {signal.volume_ratio:.2f}x" if signal.volume_ratio is not None else "Volume ratio        : N/A")
    print(f"Fibonacci golden    : {'YES' if signal.fibonacci_confirmed else 'NO'}")
    print(f"Fib retracement     : {signal.fibonacci_retracement_pct:.1f}%" if signal.fibonacci_retracement_pct is not None else "Fib retracement     : N/A")
    print()

    print("--- TRADE PLAN ---")
    print(f"Entry               : {_money(signal.entry_price)}")
    print(f"Target              : {_money(signal.target_price)}")
    print(f"Risk/share          : {_money(signal.risk_per_share)}")
    print(f"Reward/share        : {_money(signal.reward_per_share)}")
    print(f"R:R                 : {signal.risk_reward_ratio:.2f}" if signal.risk_reward_ratio is not None else "R:R                 : N/A")
    print(f"Minimum R:R met     : {'YES' if signal.meets_minimum_rr else 'NO'}")
    print(f"Account equity      : {_money(ACCOUNT_EQUITY)}")
    print(f"Risk allowed        : {_money(signal.allowed_risk)}")
    print(f"Quantity            : {signal.quantity if signal.quantity is not None else 'N/A'}")
    print(f"Actual risk         : {_money(signal.actual_risk)}")
    print()

    print("--- SCORE ---")
    print(f"Score               : {signal.score}/100")
    print(f"Grade               : {signal.grade}")
    for name, points in signal.score_breakdown.items():
        print(f"{name:<20}: {points}")


def run():
    load_dotenv()

    token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if not token:
        raise SystemExit("Set UPSTOX_ACCESS_TOKEN in your .env file first.")

    print("=" * 80)
    print("TRADING SYSTEM - FULL ANALYSIS")
    print(f"Paper equity: ₹{ACCOUNT_EQUITY:.2f} | Risk/trade: {RISK_PERCENT:.2f}%")
    print("=" * 80)

    # NIFTY is fetched once because it is the market-regime filter for all stocks.
    try:
        nifty_daily = fetch_daily_candles(
            token,
            NIFTY_50_INSTRUMENT_KEY,
            lookback_days=120,
        )
        print(f"NIFTY 50 daily candles loaded: {len(nifty_daily)}")
    except Exception as exc:
        nifty_daily = None
        print(f"WARNING: Could not load NIFTY 50 data: {exc}")

    for symbol, instrument_key in WATCHLIST.items():
        try:
            price = get_ltp(token, instrument_key)

            daily = fetch_daily_candles(
                token,
                instrument_key,
                lookback_days=120,
            )
            hourly = fetch_hourly_candles(
                token,
                instrument_key,
                lookback_days=30,
            )
            fifteen = fetch_fifteen_minute_candles(
                token,
                instrument_key,
                lookback_days=10,
            )

            signal = evaluate(
                daily_candles=daily,
                hourly_candles=hourly,
                fifteen_min_candles=fifteen,
                current_price=price,
                account_equity=ACCOUNT_EQUITY,
                risk_pct=RISK_PERCENT,
                nifty_daily_candles=nifty_daily,
            )

            print_signal(symbol, price, signal)

        except Exception as exc:
            print("\n" + "=" * 80)
            print(f"{symbol} | ERROR")
            print("=" * 80)
            print(f"{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    run()
