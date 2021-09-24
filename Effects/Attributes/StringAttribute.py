from Effects.Attributes.BaseAttribute import BaseAttribute


class StringAttribute(BaseAttribute):
    value: str

    def __init__(self, value: str = ''):
        self.value = value
