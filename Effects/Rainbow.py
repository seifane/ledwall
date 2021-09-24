from Core import Core
from Effects.Attributes.BoolAttribute import BoolAttribute
from Effects.Attributes.IntAttribute import IntAttribute
from Effects.Attributes.IntRangeAttribute import IntRangeAttribute
from Effects.BaseEffect import BaseEffect
from helpers import hsv_to_rgb


class Rainbow(BaseEffect):

    def __init__(self, core: Core):
        super().__init__()

        self.core = core
        self.currentHue = 0

        self.attributes = {
            'hsv_padding': IntAttribute(0, 360, 1),
            'hsv_padding_rate': IntAttribute(0, 5000, 10),
            'hsv_step': IntAttribute(1, 2000, 20),
            'is_vertical': BoolAttribute(False),
        }

    @staticmethod
    def get_name():
        return 'Rainbow'

    def get_attributes(self):
        return self.attributes

    def get_attribute_value(self, attribute_name: str):
        return self.attributes[attribute_name].value

    def set_attribute_value(self, attribute_name: str, value: any):
        self.attributes[attribute_name].value = value

    def stop(self):
        self.is_active = False

    def draw(self, buffer: [[int, int, int, int]]) -> [[int, int, int, int]]:
        total_hsv_step = 0
        for x in range(self.core.group.width):
            for y in range(self.core.group.height):
                correctedHue = (self.currentHue + total_hsv_step) % 360
                rgba = hsv_to_rgb((int(correctedHue), 100, 100))
                buffer[x][y] = rgba
            total_hsv_step = (total_hsv_step + self.get_attribute_value('hsv_step') / 100)

        padding_rate = self.get_attribute_value('hsv_padding_rate') / 1000
        if padding_rate > 0:
            self.currentHue += padding_rate
        else:
            self.currentHue = self.get_attribute_value('hsv_padding')
        self.currentHue = self.currentHue % 360
        return buffer
