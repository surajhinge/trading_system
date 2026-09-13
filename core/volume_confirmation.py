"""Volume confirmation used as a supporting signal."""

from dataclasses import dataclass
from core.level_engine import Candle


@dataclass
class VolumeConfirmation:
    confirmed: bool
    current_volume: float | None
    average_volume: float | None
    volume_ratio: float | None
    reason: str


def confirm_volume(
    candles: list[Candle],
    lookback: int = 20,
    minimum_ratio: float = 1.20,
) -> VolumeConfirmation:
    """Compare the latest candle volume with previous average volume.

    Volume is a bonus, not a hard rejection condition.
    """
    if not candles:
        return VolumeConfirmation(False, None, None, None, "No candles available")

    if lookback <= 0:
        raise ValueError("lookback must be greater than zero")
    if minimum_ratio <= 0:
        raise ValueError("minimum_ratio must be greater than zero")

    latest = candles[-1].volume
    if latest is None or latest <= 0:
        return VolumeConfirmation(False, latest, None, None, "Latest candle has no valid volume")

    previous = [
        c.volume for c in candles[:-1]
        if c.volume is not None and c.volume > 0
    ][-lookback:]

    if not previous:
        return VolumeConfirmation(False, latest, None, None, "Not enough previous volume data")

    average = sum(previous) / len(previous)
    ratio = latest / average if average > 0 else None

    if ratio is None:
        return VolumeConfirmation(False, latest, average, None, "Average volume is invalid")

    confirmed = ratio >= minimum_ratio
    reason = (
        f"Volume {ratio:.2f}x average - confirmed"
        if confirmed
        else f"Volume {ratio:.2f}x average - below confirmation threshold"
    )

    return VolumeConfirmation(
        confirmed=confirmed,
        current_volume=latest,
        average_volume=round(average, 2),
        volume_ratio=round(ratio, 2),
        reason=reason,
    )
