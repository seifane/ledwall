import colorsys
import math

import numpy
import numpy as np
import pyaudio
from colorutils import Color

from Core import Core
from Effects.Attributes.BoolAttribute import BoolAttribute
from Effects.Attributes.IntAttribute import IntAttribute
from Effects.Attributes.IntRangeAttribute import IntRangeAttribute
from Effects.BaseEffect import BaseEffect
from LedGroup import LedGroup
from helpers import chunks, chunk_based_on_number, rgb_to_hsv, hsv_to_rgb


class BarsEffect(BaseEffect):
    RATE = 44100
    CHUNK = int(RATE / 30)

    smoothing = 0.0007 ** CHUNK / RATE

    y_merged_prime = None
    hsv_padding = 0
    is_active = True

    def __init__(self, core: Core):
        super().__init__()

        self.attributes = {
            'max_amp': IntAttribute(1, 1000, 50),
            'decay_enabled': BoolAttribute(False),
            'decay_rate': IntAttribute(1, 100, 1),
            'ftt_range': IntRangeAttribute(0, 22050, (0, 10000))
        }
        self.core = core
        self.ledGroup = core.group

    def __del__(self):
        self.stop()

    @staticmethod
    def get_name():
        return 'Bar effect'

    def get_attributes(self):
        return self.attributes

    def get_attribute_value(self, attribute_name: str):
        return self.attributes[attribute_name].value

    def set_attribute_value(self, attribute_name: str, value: any):
        self.attributes[attribute_name].value = value

    def stop(self):
        self.is_active = False

    def draw(self, buffer: [[int, int, int, int]]) -> [[int, int, int, int]]:
        if not self.is_active:
            return buffer
        fft_range = self.get_attribute_value('ftt_range')
        last_fft_frame = self.core.fft_provider.get_last_frame_range(fft_range[0], fft_range[1])
        if last_fft_frame is None:
            return buffer
        y_split = last_fft_frame[1]
        binIdxs = last_fft_frame[2]
        y_merged = np.zeros(32)

        rangeStep = 100 / (self.ledGroup.width)

        for idx, bi in enumerate(binIdxs):
            merge_idx = int(math.floor(bi / rangeStep))
            if y_split[idx] > y_merged[merge_idx]:
                y_merged[merge_idx] = y_split[idx]

        for idx, d in enumerate(y_merged):
            if y_merged[idx] > 0:
                y_merged[idx] = math.log(y_merged[idx])

        self.y_merged_prime = y_merged

        max = self.get_attribute_value('max_amp') / 10
        for x in range(self.ledGroup.width):
            if max > 0:
                normalized = y_merged[x] / max * (self.ledGroup.height - 1)
            else:
                normalized = 0
            for y in range(self.ledGroup.height):
                corrected_index = (self.ledGroup.height - 1 - y)
                normalized_corrected = normalized - corrected_index + 1
                if normalized_corrected > 1:
                    normalized_corrected = 1
                if normalized_corrected < 0:
                    normalized_corrected = 0

                idx = int(normalized_corrected * 255)
                buffer[x][y] = (255, 255, 255, idx)
        return buffer

    def smooth_value(self, idx, val):
        prevValue = 0
        if self.y_merged_prime is not None:
            prevValue = self.y_merged_prime[idx]
        return prevValue * self.smoothing + val * (1 - self.smoothing)