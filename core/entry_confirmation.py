# from dataclasses import dataclass
# from core.swing_points import find_swing_points
# from core.structure_classifier import classify_structure


# @dataclass
# class EntryConfirmation:
#     confirmed: bool
#     reason: str
#     trigger_price: float | None   # break level to enter on
#     stop_price: float | None      # the ACTUAL structural HL/LH price - the real invalidation point


# def confirm_long_entry(fifteen_min_candles, window: int = 2) -> EntryConfirmation:
#     swings = find_swing_points(fifteen_min_candles, window=window)
#     structure = classify_structure(swings)
#     lows = [p for p in structure if p.swing.kind == "low"]
#     highs = [p for p in structure if p.swing.kind == "high"]

#     if len(lows) < 2:
#         return EntryConfirmation(False, "Not enough 15M swing lows yet to confirm HL", None, None)

#     last_low = lows[-1]
#     if last_low.label != "HL":
#         return EntryConfirmation(False, f"Most recent 15M low is {last_low.label}, not HL - no confirmation yet", None, None)

#     prior_high_candidates = [h for h in highs if h.swing.index < last_low.swing.index]
#     if not prior_high_candidates:
#         return EntryConfirmation(False, "HL confirmed but no prior swing high to use as break level", None, None)

#     trigger_price = prior_high_candidates[-1].swing.price
#     stop_price = last_low.swing.price
#     return EntryConfirmation(True, "15M HL confirmed - waiting for break above trigger to enter", trigger_price, stop_price)


# def confirm_short_entry(fifteen_min_candles, window: int = 2) -> EntryConfirmation:
#     swings = find_swing_points(fifteen_min_candles, window=window)
#     structure = classify_structure(swings)
#     lows = [p for p in structure if p.swing.kind == "low"]
#     highs = [p for p in structure if p.swing.kind == "high"]

#     if len(highs) < 2:
#         return EntryConfirmation(False, "Not enough 15M swing highs yet to confirm LH", None, None)

#     last_high = highs[-1]
#     if last_high.label != "LH":
#         return EntryConfirmation(False, f"Most recent 15M high is {last_high.label}, not LH - no confirmation yet", None, None)

#     prior_low_candidates = [l for l in lows if l.swing.index < last_high.swing.index]
#     if not prior_low_candidates:
#         return EntryConfirmation(False, "LH confirmed but no prior swing low to use as break level", None, None)

#     trigger_price = prior_low_candidates[-1].swing.price
#     stop_price = last_high.swing.price
#     return EntryConfirmation(True, "15M LH confirmed - waiting for break below trigger to enter", trigger_price, stop_price)

from dataclasses import dataclass

from core.level_engine import Candle
from core.swing_points import find_swing_points
from core.structure_classifier import classify_structure


@dataclass
class EntryConfirmation:
    confirmed: bool
    reason: str
    trigger_price: float | None
    stop_price: float | None


def detect_bullish_rejection(
    candles: list[Candle],
    support_price: float,
    tolerance_pct: float = 0.20,
) -> bool:
    """
    Detect bullish rejection near a support level.

    Conditions:
    1. Latest candle must have OHLC data.
    2. Candle low must reach close to / below support.
    3. Candle must close above support.
    4. Lower wick should be meaningful compared with the candle body.

    This indicates that sellers pushed price toward support,
    but buyers rejected the lower prices.
    """

    if not candles:
        return False

    candle = candles[-1]

    if candle.open is None:
        return False

    tolerance = support_price * (tolerance_pct / 100)

    # Candle must actually test the support area.
    if candle.low > support_price + tolerance:
        return False

    # Candle must recover and close above support.
    if candle.close <= support_price:
        return False

    body = abs(candle.close - candle.open)

    lower_wick = min(candle.open, candle.close) - candle.low

    # Avoid treating a doji with zero body as a strong rejection.
    if body <= 0:
        return False

    # Lower wick should be at least as large as the body.
    if lower_wick < body:
        return False

    return True


def detect_bearish_rejection(
    candles: list[Candle],
    resistance_price: float,
    tolerance_pct: float = 0.20,
) -> bool:
    """
    Detect bearish rejection near a resistance level.

    Conditions:
    1. Latest candle must have OHLC data.
    2. Candle high must reach close to / above resistance.
    3. Candle must close below resistance.
    4. Upper wick should be meaningful compared with the candle body.

    This indicates that buyers pushed price toward resistance,
    but sellers rejected the higher prices.
    """

    if not candles:
        return False

    candle = candles[-1]

    if candle.open is None:
        return False

    tolerance = resistance_price * (tolerance_pct / 100)

    # Candle must actually test the resistance area.
    if candle.high < resistance_price - tolerance:
        return False

    # Candle must reject the resistance and close below it.
    if candle.close >= resistance_price:
        return False

    body = abs(candle.close - candle.open)

    upper_wick = candle.high - max(candle.open, candle.close)

    # Avoid treating a doji with zero body as a strong rejection.
    if body <= 0:
        return False

    # Upper wick should be at least as large as the body.
    if upper_wick < body:
        return False

    return True


def confirm_long_entry(
    fifteen_min_candles,
    window: int = 2,
    check_trigger: bool = False,
) -> EntryConfirmation:
    """
    Confirm a LONG setup.

    Step 1:
        Find a confirmed HL.

    Step 2:
        Find the previous swing high before that HL.
        This becomes the trigger price.

    Step 3:
        If check_trigger=True, require the latest confirmed
        candle close to be above the trigger.
    """

    swings = find_swing_points(fifteen_min_candles, window=window)
    structure = classify_structure(swings)

    lows = [p for p in structure if p.swing.kind == "low"]
    highs = [p for p in structure if p.swing.kind == "high"]

    if len(lows) < 2:
        return EntryConfirmation(
            False,
            "Not enough 15M swing lows yet to confirm HL",
            None,
            None,
        )

    last_low = lows[-1]

    if last_low.label != "HL":
        return EntryConfirmation(
            False,
            f"Most recent 15M low is {last_low.label}, not HL - no confirmation yet",
            None,
            None,
        )

    prior_high_candidates = [
        h for h in highs
        if h.swing.index < last_low.swing.index
    ]

    if not prior_high_candidates:
        return EntryConfirmation(
            False,
            "HL confirmed but no prior swing high to use as break level",
            None,
            None,
        )

    trigger_price = prior_high_candidates[-1].swing.price
    stop_price = last_low.swing.price

    if not check_trigger:
        return EntryConfirmation(
            True,
            "15M HL confirmed - waiting for break above trigger to enter",
            trigger_price,
            stop_price,
        )

    latest_close = fifteen_min_candles[-1].close

    if latest_close <= trigger_price:
        return EntryConfirmation(
            False,
            (
                f"15M HL confirmed but trigger ₹{trigger_price:.2f} "
                f"has not broken - latest close ₹{latest_close:.2f}"
            ),
            trigger_price,
            stop_price,
        )

    return EntryConfirmation(
        True,
        (
            f"15M HL confirmed and trigger broken - "
            f"latest close ₹{latest_close:.2f} > trigger ₹{trigger_price:.2f}"
        ),
        trigger_price,
        stop_price,
    )


def confirm_short_entry(
    fifteen_min_candles,
    window: int = 2,
    check_trigger: bool = False,
) -> EntryConfirmation:
    """
    Confirm a SHORT setup.

    Step 1:
        Find a confirmed LH.

    Step 2:
        Find the previous swing low before that LH.
        This becomes the trigger price.

    Step 3:
        If check_trigger=True, require the latest confirmed
        candle close to be below the trigger.
    """

    swings = find_swing_points(fifteen_min_candles, window=window)
    structure = classify_structure(swings)

    lows = [p for p in structure if p.swing.kind == "low"]
    highs = [p for p in structure if p.swing.kind == "high"]

    if len(highs) < 2:
        return EntryConfirmation(
            False,
            "Not enough 15M swing highs yet to confirm LH",
            None,
            None,
        )

    last_high = highs[-1]

    if last_high.label != "LH":
        return EntryConfirmation(
            False,
            f"Most recent 15M high is {last_high.label}, not LH - no confirmation yet",
            None,
            None,
        )

    prior_low_candidates = [
        l for l in lows
        if l.swing.index < last_high.swing.index
    ]

    if not prior_low_candidates:
        return EntryConfirmation(
            False,
            "LH confirmed but no prior swing low to use as break level",
            None,
            None,
        )

    trigger_price = prior_low_candidates[-1].swing.price
    stop_price = last_high.swing.price

    if not check_trigger:
        return EntryConfirmation(
            True,
            "15M LH confirmed - waiting for break below trigger to enter",
            trigger_price,
            stop_price,
        )

    latest_close = fifteen_min_candles[-1].close

    if latest_close >= trigger_price:
        return EntryConfirmation(
            False,
            (
                f"15M LH confirmed but trigger ₹{trigger_price:.2f} "
                f"has not broken - latest close ₹{latest_close:.2f}"
            ),
            trigger_price,
            stop_price,
        )

    return EntryConfirmation(
        True,
        (
            f"15M LH confirmed and trigger broken - "
            f"latest close ₹{latest_close:.2f} < trigger ₹{trigger_price:.2f}"
        ),
        trigger_price,
        stop_price,
    )

