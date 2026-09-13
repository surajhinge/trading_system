from dataclasses import dataclass
from core.swing_points import find_swing_points

MIN_RR = 2.0


@dataclass
class TradePlan:
    entry: float
    stop: float
    target: float
    quantity: int
    risk_amount: float
    reward_amount: float
    risk_reward_ratio: float
    meets_minimum_rr: bool


def find_next_target(hourly_candles, current_price: float, direction: str, window: int = 2):
    swings = find_swing_points(hourly_candles, window=window)
    if direction == "long":
        candidates = [s.price for s in swings if s.kind == "high" and s.price > current_price]
        return min(candidates) if candidates else None
    else:
        candidates = [s.price for s in swings if s.kind == "low" and s.price < current_price]
        return max(candidates) if candidates else None


def build_trade_plan(entry: float, stop: float, target: float, quantity: int) -> TradePlan:
    risk_per_share = abs(entry - stop)
    reward_per_share = abs(target - entry)
    risk_amount = round(risk_per_share * quantity, 2)
    reward_amount = round(reward_per_share * quantity, 2)
    rr = round(reward_per_share / risk_per_share, 2) if risk_per_share > 0 else 0.0
    return TradePlan(entry=entry, stop=stop, target=target, quantity=quantity,
                      risk_amount=risk_amount, reward_amount=reward_amount,
                      risk_reward_ratio=rr, meets_minimum_rr=(rr >= MIN_RR))
