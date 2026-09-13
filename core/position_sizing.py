"""
Position sizing per strategy doc sections 17-18: fixed 1% risk of
paper equity per trade, quantity derived from stop distance - never
a fixed share count.
"""
from dataclasses import dataclass
import math


@dataclass
class PositionSize:
    quantity: int
    risk_amount: float
    risk_per_share: float


def calculate_position_size(account_equity: float, entry_price: float, stop_loss_price: float, risk_pct: float = 1.0) -> PositionSize:
    risk_per_share = abs(entry_price - stop_loss_price)
    if risk_per_share <= 0:
        raise ValueError("Stop loss must differ from entry price")

    risk_amount = account_equity * (risk_pct / 100)
    quantity = math.floor(risk_amount / risk_per_share)

    return PositionSize(quantity=quantity, risk_amount=risk_amount, risk_per_share=risk_per_share)
