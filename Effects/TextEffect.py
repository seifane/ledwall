import math

import numpy as np
from PIL import ImageFont, ImageDraw, Image

from Core import Core
from Effects.Attributes.IntAttribute import IntAttribute
from Effects.Attributes.StringAttribute import StringAttribute
from Effects.BaseEffect import BaseEffect


class TextEffect(BaseEffect):
    def __init__(self, core: Core):
        super().__init__()

        self.attributes = {
            'text': StringAttribute("test"),
            'slide_rate': IntAttribute(-2000, 2000, 500)
        }
        self.core = core
        self.offset = 0
        self.last_text = ''
        self.last_text_buffer = None

    @staticmethod
    def get_name():
        return 'Text effect'

    def get_attributes(self):
        return self.attributes

    def get_attribute_value(self, attribute_name: str):
        return self.attributes[attribute_name].value

    def set_attribute_value(self, attribute_name: str, value: any):
        self.attributes[attribute_name].value = value

    def stop(self):
        self.is_active = False

    def draw(self, buffer: [[int, int, int, int]]) -> [[int, int, int, int]]:
        slideRate = -self.get_attribute_value('slide_rate')
        text = self.get_attribute_value('text')
        if text == '':
            return buffer
        if self.last_text != text or self.last_text_buffer is None:
            self.last_text_buffer = self.char_to_pixels(text)
        for x, line in enumerate(buffer):
            for y, pix in enumerate(line):
                pixt = 0
                x_text = int(math.floor(x + self.offset)) % (self.last_text_buffer.shape[1] + 5)
                if len(self.last_text_buffer) > y and len(self.last_text_buffer[y]) > x_text:
                    pixt = self.last_text_buffer[y][x_text]
                color = (255 * pixt, 255 * pixt, 255 * pixt, 255 * pixt)
                buffer[x][y] = color
        self.offset += slideRate / 1000
        return buffer

    def char_to_pixels(self, text, fontsize=13, path='fonts/connection.otf'):
        """
        Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
        """
        font = ImageFont.truetype(path, fontsize)
        w, h = font.getsize(text)
        h *= 2
        image = Image.new('L', (w, h), 1)
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), text, font=font)
        arr = np.asarray(image)
        arr = np.where(arr, 0, 1)
        arr = arr[(arr != 0).any(axis=1)]
        return arr