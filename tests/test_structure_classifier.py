from core.swing_points import SwingPoint
from core.structure_classifier import classify_structure


def test_second_high_greater_is_HH():
    swings = [
        SwingPoint(index=0, price=100, kind="high"),
        SwingPoint(index=2, price=110, kind="high"),  # higher than 100
    ]
    result = classify_structure(swings)
    assert result[0].label == "first"
    assert result[1].label == "HH"


def test_second_low_greater_is_HL():
    swings = [
        SwingPoint(index=0, price=90, kind="low"),
        SwingPoint(index=2, price=95, kind="low"),  # higher than 90 -> buyers stepping in earlier
    ]
    result = classify_structure(swings)
    assert result[1].label == "HL"


def test_second_low_lower_is_LL():
    swings = [
        SwingPoint(index=0, price=90, kind="low"),
        SwingPoint(index=2, price=85, kind="low"),  # lower than 90
    ]
    result = classify_structure(swings)
    assert result[1].label == "LL"


def test_highs_and_lows_tracked_independently():
    # a low in between two highs must not affect the high/high comparison
    swings = [
        SwingPoint(index=0, price=100, kind="high"),
        SwingPoint(index=1, price=90, kind="low"),
        SwingPoint(index=2, price=105, kind="high"),  # compare to 100, not 90
    ]
    result = classify_structure(swings)
    assert result[2].label == "HH"
