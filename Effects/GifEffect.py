import time

from PIL import Image

from Core import Core
from Effects.BaseEffect import BaseEffect


class GifEffect(BaseEffect):
    def __init__(self, core: Core):
        super().__init__()

        self.attributes = {
        }
        self.core = core
        self.ledGroup = core.group
        self.currentFile = None
        self.currentFrame = 0
        self.lastFrameTime = 0
        self.open_file("tenor.gif")

    def __del__(self):
        self.stop()

    @staticmethod
    def get_name():
        return 'Gif effect'

    def get_attributes(self):
        return self.attributes

    def get_attribute_value(self, attribute_name: str):
        return self.attributes[attribute_name].value

    def set_attribute_value(self, attribute_name: str, value: any):
        self.attributes[attribute_name].value = value

    def stop(self):
        self.is_active = False

    def open_file(self, path: str):
        self.currentFile = Image.open(path)
        if not self.currentFile.is_animated:
            self.currentFile = None
            return
        self.currentFile.thumbnail((self.core.group.height, self.core.group.width))
        self.currentFrame = 0



    def draw(self, buffer: [[int, int, int, int]]) -> [[int, int, int, int]]:
        diff = time.time_ns() / 1000000 - self.lastFrameTime

        self.currentFile.seek(self.currentFrame)
        rgb_image = self.currentFile.convert('RGB')
        rgb_image = rgb_image.resize((self.core.group.width, self.core.group.height))
        for x in range(self.core.group.width):
            for y in range(self.core.group.height):
                r, g, b = rgb_image.getpixel((x, y))
                buffer[x][y] = (r, g, b, 255)

        if diff < self.currentFile.info['duration']:
            return buffer

        self.currentFrame += 1
        if self.currentFrame >= self.currentFile.n_frames:
            self.currentFrame = 0
        self.lastFrameTime = time.time_ns() / 1000000
        return buffer