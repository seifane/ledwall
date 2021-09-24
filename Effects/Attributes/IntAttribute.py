from Effects.Attributes.BaseAttribute import BaseAttribute


class IntAttribute(BaseAttribute):
    value: int
    min: int
    max: int

    def __init__(self, min: int, max: int, value: int = 0):
        self.value = value
        self.min = min
        self.max = max