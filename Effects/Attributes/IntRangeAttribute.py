from Effects.Attributes.BaseAttribute import BaseAttribute


class IntRangeAttribute(BaseAttribute):
    value: (int, int)
    min: int
    max: int

    def __init__(self, min: int, max: int, value: (int, int)):
        self.value = value
        self.min = min
        self.max = max