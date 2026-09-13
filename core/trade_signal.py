"""Complete setup evaluation and detailed trade diagnostics.

Strategy:
Daily trend -> 1H location -> 15M rejection -> HL/LH -> trigger
-> volume/Fibonacci/NIFTY confluence -> target -> R:R -> position size -> score.

Fibonacci and volume are bonuses. R:R and structural invalidation are risk gates.
"""

from dataclasses import dataclass, field

from core.daily_context import classify_daily_context
from core.location_classifier import classify_location
from core.entry_confirmation import (
    confirm_long_entry,
    confirm_short_entry,
    detect_bullish_rejection,
    detect_bearish_rejection,
)
from core.fibonacci import compute_fib_zone
from core.market_regime import classify_market_regime
from core.position_sizing import calculate_position_size
from core.target_calculator import find_next_target, build_trade_plan, MIN_RR
from core.trade_score import calculate_trade_score
from core.volume_confirmation import confirm_volume


@dataclass
class TradeSignal:
    direction: str
    status: str
    reason: str
    daily_context: str
    zone: str
    support: float | None = None
    resistance: float | None = None
    support_touches: int = 0
    resistance_touches: int = 0
    rejection_confirmed: bool = False
    structure_confirmed: bool = False
    trigger_confirmed: bool = False
    trigger_price: float | None = None
    stop_price: float | None = None
    entry_price: float | None = None
    target_price: float | None = None
    risk_per_share: float | None = None
    reward_per_share: float | None = None
    risk_reward_ratio: float | None = None
    meets_minimum_rr: bool = False
    quantity: int | None = None
    allowed_risk: float | None = None
    actual_risk: float | None = None
    volume_confirmed: bool = False
    volume_ratio: float | None = None
    fibonacci_confirmed: bool = False
    fibonacci_retracement_pct: float | None = None
    nifty_regime: str = "Unknown"
    score: int = 0
    grade: str = "NO_TRADE"
    score_breakdown: dict[str, int] = field(default_factory=dict)


def _has_recent_rejection(candles, price, direction, lookback=6):
    if len(candles) < 2:
        return False

    start = max(0, len(candles) - lookback - 1)
    end = len(candles) - 1

    detector = detect_bullish_rejection if direction == "long" else detect_bearish_rejection
    kw = "support_price" if direction == "long" else "resistance_price"

    for i in range(start, end):
        if detector(candles[i:i + 1], **{kw: price}):
            return True
    return False


def _base_no_trade(context, location, reason, **kwargs):
    return TradeSignal(
        direction="no_trade",
        status="WAIT",
        reason=reason,
        daily_context=context,
        zone=location.zone,
        support=location.nearest_support,
        resistance=location.nearest_resistance,
        support_touches=location.support_touches,
        resistance_touches=location.resistance_touches,
        **kwargs,
    )


def evaluate(
    daily_candles,
    hourly_candles,
    fifteen_min_candles,
    current_price,
    account_equity: float = 10_000.0,
    risk_pct: float = 1.0,
    nifty_daily_candles=None,
):
    """Evaluate one stock and return every important decision field.

    `nifty_daily_candles` is optional for backward compatibility. When supplied,
    NIFTY contributes to the score and market-context diagnostics.
    """
    context = classify_daily_context(daily_candles)
    location = classify_location(hourly_candles, current_price, edge_threshold_pct=15)
    market = classify_market_regime(nifty_daily_candles)

    if location.zone == "middle":
        return _base_no_trade(context, location, "Price is in the middle of the 1H range")

    if location.zone in ("near_untested_low", "near_untested_high"):
        return _base_no_trade(
            context,
            location,
            f"Level only touched {location.support_touches if 'low' in location.zone else location.resistance_touches} time(s) - not a proven level",
        )

    if location.zone not in ("near_support", "near_resistance"):
        return _base_no_trade(context, location, f"1H zone is {location.zone} - no setup evaluated")

    direction = "long" if location.zone == "near_support" else "short"

    if direction == "long" and context == "Bearish":
        return _base_no_trade(context, location, "Daily context is Bearish - counter-trend long skipped")

    if direction == "short" and context == "Bullish":
        return _base_no_trade(context, location, "Daily context is Bullish - counter-trend short skipped")

    level = location.nearest_support if direction == "long" else location.nearest_resistance
    rejection = _has_recent_rejection(fifteen_min_candles, level, direction)

    if not rejection:
        return _base_no_trade(
            context,
            location,
            f"Near {('support' if direction == 'long' else 'resistance')} but no recent 15M rejection",
            nifty_regime=market.regime,
        )

    confirmation = (
        confirm_long_entry(fifteen_min_candles, check_trigger=True)
        if direction == "long"
        else confirm_short_entry(fifteen_min_candles, check_trigger=True)
    )

    if not confirmation.confirmed:
        return _base_no_trade(
            context,
            location,
            f"Rejection found, but {confirmation.reason}",
            rejection_confirmed=True,
            trigger_price=confirmation.trigger_price,
            stop_price=confirmation.stop_price,
            nifty_regime=market.regime,
        )

    entry = current_price
    stop = confirmation.stop_price

    if stop is None:
        return _base_no_trade(context, location, "No structural stop available", rejection_confirmed=True,
                              structure_confirmed=True, trigger_confirmed=True, nifty_regime=market.regime)

    # Structural invalidation must be on the correct side of entry.
    if direction == "long" and stop >= entry:
        return _base_no_trade(context, location, "Structural stop is not below the long entry",
                              rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
                              trigger_price=confirmation.trigger_price, stop_price=stop, nifty_regime=market.regime)
    if direction == "short" and stop <= entry:
        return _base_no_trade(context, location, "Structural stop is not above the short entry",
                              rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
                              trigger_price=confirmation.trigger_price, stop_price=stop, nifty_regime=market.regime)

    volume = confirm_volume(fifteen_min_candles)
    fib = compute_fib_zone(location.nearest_support, location.nearest_resistance, current_price, direction)
    target = find_next_target(hourly_candles, entry, direction)

    if target is None:
        return _base_no_trade(context, location, "No confirmed 1H swing available as target",
                              rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
                              trigger_price=confirmation.trigger_price, stop_price=stop,
                              volume_confirmed=volume.confirmed, volume_ratio=volume.volume_ratio,
                              fibonacci_confirmed=fib.in_golden_zone,
                              fibonacci_retracement_pct=fib.current_retracement_pct * 100,
                              nifty_regime=market.regime)

    plan = build_trade_plan(entry, stop, target, 1)
    size = calculate_position_size(account_equity, entry, stop, risk_pct)

    score = calculate_trade_score(
        direction=direction,
        daily_context=context,
        location_valid=True,
        rejection_confirmed=True,
        structure_confirmed=True,
        trigger_confirmed=True,
        volume_confirmed=volume.confirmed,
        fibonacci_confirmed=fib.in_golden_zone,
        market_regime=market.regime,
    )

    if not plan.meets_minimum_rr:
        return _base_no_trade(
            context, location,
            f"Actual target gives R:R {plan.risk_reward_ratio:.2f}, below minimum {MIN_RR:.2f}",
            rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
            trigger_price=confirmation.trigger_price, stop_price=stop, entry_price=entry,
            target_price=target, risk_per_share=abs(entry - stop),
            reward_per_share=abs(target - entry), risk_reward_ratio=plan.risk_reward_ratio,
            meets_minimum_rr=False, quantity=size.quantity,
            allowed_risk=size.risk_amount, actual_risk=round(size.quantity * size.risk_per_share, 2),
            volume_confirmed=volume.confirmed, volume_ratio=volume.volume_ratio,
            fibonacci_confirmed=fib.in_golden_zone,
            fibonacci_retracement_pct=fib.current_retracement_pct * 100,
            nifty_regime=market.regime, score=score.score, grade=score.grade,
            score_breakdown=score.breakdown,
        )

    if score.score < 70:
        return _base_no_trade(
            context, location,
            f"Setup passed structure and R:R, but score {score.score}/100 is below 70",
            rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
            trigger_price=confirmation.trigger_price, stop_price=stop, entry_price=entry,
            target_price=target, risk_per_share=abs(entry - stop), reward_per_share=abs(target - entry),
            risk_reward_ratio=plan.risk_reward_ratio, meets_minimum_rr=True,
            quantity=size.quantity, allowed_risk=size.risk_amount,
            actual_risk=round(size.quantity * size.risk_per_share, 2),
            volume_confirmed=volume.confirmed, volume_ratio=volume.volume_ratio,
            fibonacci_confirmed=fib.in_golden_zone,
            fibonacci_retracement_pct=fib.current_retracement_pct * 100,
            nifty_regime=market.regime, score=score.score, grade=score.grade,
            score_breakdown=score.breakdown,
        )

    if direction == "long" and market.regime == "Bearish":
        return _base_no_trade(context, location, "NIFTY regime is Bearish - long not supported",
                              rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
                              trigger_price=confirmation.trigger_price, stop_price=stop, entry_price=entry,
                              target_price=target, risk_reward_ratio=plan.risk_reward_ratio,
                              quantity=size.quantity, allowed_risk=size.risk_amount, actual_risk=round(size.quantity * size.risk_per_share, 2),
                              volume_confirmed=volume.confirmed, volume_ratio=volume.volume_ratio,
                              fibonacci_confirmed=fib.in_golden_zone, fibonacci_retracement_pct=fib.current_retracement_pct * 100,
                              nifty_regime=market.regime, score=score.score, grade=score.grade, score_breakdown=score.breakdown)

    if direction == "short" and market.regime == "Bullish":
        return _base_no_trade(context, location, "NIFTY regime is Bullish - short not supported",
                              rejection_confirmed=True, structure_confirmed=True, trigger_confirmed=True,
                              trigger_price=confirmation.trigger_price, stop_price=stop, entry_price=entry,
                              target_price=target, risk_reward_ratio=plan.risk_reward_ratio,
                              quantity=size.quantity, allowed_risk=size.risk_amount, actual_risk=round(size.quantity * size.risk_per_share, 2),
                              volume_confirmed=volume.confirmed, volume_ratio=volume.volume_ratio,
                              fibonacci_confirmed=fib.in_golden_zone, fibonacci_retracement_pct=fib.current_retracement_pct * 100,
                              nifty_regime=market.regime, score=score.score, grade=score.grade, score_breakdown=score.breakdown)

    actual_risk = round(size.quantity * size.risk_per_share, 2)
    reason = (
        f"{direction.upper()} confirmed | rejection + structure + trigger | "
        f"target ₹{target:.2f} | R:R {plan.risk_reward_ratio:.2f} | score {score.score}/100 ({score.grade})"
    )

    return TradeSignal(
        direction=direction,
        status="TRADE",
        reason=reason,
        daily_context=context,
        zone=location.zone,
        support=location.nearest_support,
        resistance=location.nearest_resistance,
        support_touches=location.support_touches,
        resistance_touches=location.resistance_touches,
        rejection_confirmed=True,
        structure_confirmed=True,
        trigger_confirmed=True,
        trigger_price=confirmation.trigger_price,
        stop_price=stop,
        entry_price=entry,
        target_price=target,
        risk_per_share=size.risk_per_share,
        reward_per_share=round(abs(target - entry), 2),
        risk_reward_ratio=plan.risk_reward_ratio,
        meets_minimum_rr=True,
        quantity=size.quantity,
        allowed_risk=size.risk_amount,
        actual_risk=actual_risk,
        volume_confirmed=volume.confirmed,
        volume_ratio=volume.volume_ratio,
        fibonacci_confirmed=fib.in_golden_zone,
        fibonacci_retracement_pct=fib.current_retracement_pct * 100,
        nifty_regime=market.regime,
        score=score.score,
        grade=score.grade,
        score_breakdown=score.breakdown,
    )
