"""
Classifies consecutive swing points into structure labels:
HH (Higher High), LH (Lower High), HL (Higher Low), LL (Lower Low).

This is compared only against the PREVIOUS swing of the SAME kind —
a high is only compared to the prior high, a low only to the prior low.
That's what lets us track "are buyers/sellers gaining control" over time.
"""

from dataclasses import dataclass
from core.swing_points import SwingPoint


@dataclass
class StructurePoint:
    swing: SwingPoint
    label: str  # "HH", "LH", "HL", "LL", or "first" (no prior same-kind swing yet)


def classify_structure(swings: list[SwingPoint]) -> list[StructurePoint]:
    structure = []
    last_high: SwingPoint | None = None
    last_low: SwingPoint | None = None

    for swing in swings:
        if swing.kind == "high":
            if last_high is None:
                label = "first"
            else:
                label = "HH" if swing.price > last_high.price else "LH"
            last_high = swing
        else:  # "low"
            if last_low is None:
                label = "first"
            else:
                label = "HL" if swing.price > last_low.price else "LL"
            last_low = swing

        structure.append(StructurePoint(swing=swing, label=label))

    return structure
