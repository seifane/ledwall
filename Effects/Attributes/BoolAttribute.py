from Effects.Attributes.BaseAttribute import BaseAttribute


class BoolAttribute(BaseAttribute):
    value: bool

    def __init__(self, value: bool = False):
        self.value = value
