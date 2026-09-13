"""
Position sizing per strategy doc sections 17-18.

Rules:
- Risk a fixed percentage of paper equity per trade.
- Default risk = 1% of account equity.
- Quantity is calculated from entry-to-stop distance.
- Never use a fixed share quantity.
- Never allow zero quantity.
"""

from dataclasses import dataclass
import math


@dataclass
class PositionSize:
    quantity: int
    risk_amount: float
    risk_per_share: float


def calculate_position_size(
    account_equity: float,
    entry_price: float,
    stop_loss_price: float,
    risk_pct: float = 1.0,
) -> PositionSize:
    """
    Calculate position size from account risk and stop distance.

    Example:

        Account equity = ₹10,000
        Risk           = 1%
        Entry          = ₹1281
        Stop           = ₹1278

        Maximum risk = ₹100
        Risk/share   = ₹3
        Quantity     = floor(100 / 3)
                     = 33

        Actual risk  = 33 × ₹3
                     = ₹99
    """

    if account_equity <= 0:
        raise ValueError("Account equity must be greater than zero")

    if risk_pct <= 0:
        raise ValueError("Risk percentage must be greater than zero")

    risk_per_share = abs(entry_price - stop_loss_price)

    if risk_per_share <= 0:
        raise ValueError("Stop loss must differ from entry price")

    risk_amount = account_equity * (risk_pct / 100)

    quantity = math.floor(
        risk_amount / risk_per_share
    )

    if quantity <= 0:
        raise ValueError(
            "Risk per share is too large for the allowed account risk"
        )

    return PositionSize(
        quantity=quantity,
        risk_amount=round(risk_amount, 2),
        risk_per_share=round(risk_per_share, 2),
    )
