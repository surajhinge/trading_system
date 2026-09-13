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


def find_next_target(
    hourly_candles,
    current_price: float,
    direction: str,
    window: int = 2,
):
    """
    Find the nearest confirmed hourly swing that can act as a target.

    LONG:
        Find the nearest confirmed swing high above current price.

    SHORT:
        Find the nearest confirmed swing low below current price.

    Returns:
        Target price or None if no suitable swing exists.
    """

    swings = find_swing_points(
        hourly_candles,
        window=window,
    )

    if direction == "long":
        candidates = [
            swing.price
            for swing in swings
            if swing.kind == "high"
            and swing.price > current_price
        ]

        return min(candidates) if candidates else None

    if direction == "short":
        candidates = [
            swing.price
            for swing in swings
            if swing.kind == "low"
            and swing.price < current_price
        ]

        return max(candidates) if candidates else None

    raise ValueError("direction must be 'long' or 'short'")


def calculate_minimum_target(
    entry: float,
    stop: float,
    direction: str,
    minimum_rr: float = MIN_RR,
) -> float:
    """
    Calculate the minimum target required to achieve the desired R:R.

    Example:

        Entry = 100
        Stop  = 95

        Risk = 5

        At 1:2 R:R:
        Minimum long target = 100 + (5 * 2)
                           = 110
    """

    risk_per_share = abs(entry - stop)

    if risk_per_share <= 0:
        raise ValueError("Entry and stop must be different")

    if minimum_rr <= 0:
        raise ValueError("minimum_rr must be greater than zero")

    if direction == "long":
        return entry + (risk_per_share * minimum_rr)

    if direction == "short":
        return entry - (risk_per_share * minimum_rr)

    raise ValueError("direction must be 'long' or 'short'")


def is_target_valid(
    entry: float,
    target: float,
    direction: str,
) -> bool:
    """
    Check that the target is on the correct side of the entry.
    """

    if direction == "long":
        return target > entry

    if direction == "short":
        return target < entry

    raise ValueError("direction must be 'long' or 'short'")


def build_trade_plan(
    entry: float,
    stop: float,
    target: float,
    quantity: int,
) -> TradePlan:
    """
    Build the complete trade plan and calculate actual R:R.
    """

    if entry == stop:
        raise ValueError("Entry and stop cannot be the same")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    risk_per_share = abs(entry - stop)
    reward_per_share = abs(target - entry)

    risk_amount = round(
        risk_per_share * quantity,
        2,
    )

    reward_amount = round(
        reward_per_share * quantity,
        2,
    )

    rr = round(
        reward_per_share / risk_per_share,
        2,
    )

    return TradePlan(
        entry=entry,
        stop=stop,
        target=target,
        quantity=quantity,
        risk_amount=risk_amount,
        reward_amount=reward_amount,
        risk_reward_ratio=rr,
        meets_minimum_rr=rr >= MIN_RR,
    )
