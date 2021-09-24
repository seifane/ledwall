from Effects.BaseEffect import BaseEffect
from LedGroup import LedGroup
from colorutils import Color

class Effect(BaseEffect):
    ledGroup: LedGroup
    currentOn: int = 0

    def __init__(self, ledGroup) -> None:
        super().__init__()
        self.ledGroup = ledGroup

    def draw(self):
        size = self.ledGroup.width * self.ledGroup.height
        done = 0
        for x in range(self.ledGroup.width):
            for y in range(self.ledGroup.height):
                if done < self.currentOn:
                    self.ledGroup.buffer[x][y] = Color((255, 0, 0))
                else:
                    self.ledGroup.buffer[x][y] = Color((0, 0, 0))
                done += 1
        self.currentOn += 1
        if self.currentOn > size:
            self.currentOn = 0
