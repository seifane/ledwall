from Effects.BaseEffect import BaseEffect
from LedGroup import LedGroup


class RainEffect(BaseEffect):
    ledGroup: LedGroup
    drops: List[]

    def __init__(self, ledGroup) -> None:
        super().__init__()
        self.ledGroup = ledGroup

