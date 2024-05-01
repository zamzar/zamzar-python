from enum import Enum


def after(ref):
    return Anchor(ref, Orientation.AFTER)


def before(ref):
    return Anchor(ref, Orientation.BEFORE)


class Orientation(Enum):
    AFTER = 1,
    BEFORE = 2,


class Anchor:
    def __init__(self, ref, orientation: Orientation):
        self._ref = ref
        self._orientation = orientation

    def get_after_parameter_value(self):
        return self._ref if self._orientation == Orientation.AFTER else None

    def get_before_parameter_value(self):
        return self._ref if self._orientation == Orientation.BEFORE else None

    def __str__(self):
        return f"{self._orientation.name.lower()} {self._ref}"
