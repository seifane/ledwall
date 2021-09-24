import sys
import threading
import time
from enum import Enum

from PySide6.QtCore import Signal, QObject

from Effects.BaseEffect import BaseEffect
from FFTProvider import FFTProvider
from LedGroup import LedGroup
from typing import List


class MergeMode(Enum):
    BLEND = 0
    SHAPE_A = 1
    SHAPE_B = 2


class Core(QObject):
    group: LedGroup
    current_effects: List[BaseEffect] = []
    effect_a = None
    effect_b = None

    effectAddedCallback = None
    effectRemovedCallback = None
    effectMovedCallback = None

    size = width, height = 960, 480

    LED_SIZE = 30

    TARGET_TIME = 1 / 30

    onFrame = Signal(str)

    is_running = False
    current_thread = None

    fft_provider: FFTProvider

    def __init__(self):
        super().__init__()
        self.buffer_effect_a = None
        self.buffer_effect_b = None
        self.buffer_merge = None

        self.merge_mode = MergeMode.SHAPE_A
        self.fader = 0

        self.last_chunk_time = 0
        self.frame_count = 0

        self.fft_provider = FFTProvider()

    def __del__(self):
        self.stop()

    def start(self):
        if self.current_thread is not None:
            return

        self.fft_provider.start()
        self.is_running = True
        self.current_thread = threading.Thread(target=self.loop)
        self.current_thread.start()

    def stop(self):
        if self.current_thread is None:
            return

        self.is_running = False
        self.current_thread.join()
        self.current_thread = None
        self.fft_provider.stop()
        self.group.stop()

    def add_effect(self, effect):
        self.current_effects.append(effect)
        if self.effectAddedCallback is not None:
            self.effectAddedCallback()

    def remove_effect_at(self, index: int):
        del self.current_effects[index]
        if self.effectRemovedCallback is not None:
            self.effectRemovedCallback()

    def remove_effect(self, obj):
        self.current_effects.remove(obj)
        if self.effectRemovedCallback is not None:
            self.effectRemovedCallback()

    def reorder_effect(self, old_index, new_index):
        self.current_effects.insert(new_index, self.current_effects.pop(old_index))
        if self.effectMovedCallback is not None:
            self.effectMovedCallback()

    def start_thread_effect(self, effectName):
        buffer = self.group.create_buffer()
        effect = getattr(self, effectName)
        if effect is not None:
            setattr(self, 'buffer_' + effectName, effect.draw(buffer))

    def loop(self):
        while self.is_running:
            frame_start_time = time.time_ns() / 1000000000

            # effect_a_thread = threading.Thread(target=self.start_thread_effect, args=('effect_a',))  # <- note extra ','
            # effect_a_thread.start()
            #
            # effect_b_thread = threading.Thread(target=self.start_thread_effect,
            #                                    args=('effect_b',))  # <- note extra ','
            # effect_b_thread.start()
            #
            # effect_a_thread.join()
            # effect_b_thread.join()

            self.start_thread_effect('effect_a')
            self.start_thread_effect('effect_b')

            # self.buffer_effect_b = self.group.create_buffer()
            # if self.effect_b is not None:
            #     self.buffer_effect_b = self.effect_b.draw(self.buffer_effect_b)

            if self.buffer_effect_a is not None:
                self.onFrame.emit('effect_a')

            if self.buffer_effect_b is not None:
                self.onFrame.emit('effect_b')

            if self.buffer_effect_a is not None and self.buffer_effect_b is not None:
                self.buffer_merge = self.group.create_buffer()
                if self.merge_mode == MergeMode.SHAPE_A:
                    for x, line in enumerate(self.buffer_effect_a):
                        for y, pix in enumerate(line):
                            color = self.buffer_effect_b[x][y]
                            alpha = (color[3] * (self.fader / 1000)) + (pix[3] * ((1000 - self.fader) / 1000))
                            self.buffer_merge[x][y] = (color[0], color[1], color[2], alpha)

            if self.buffer_merge is not None:
                self.group.set_buffer(self.buffer_merge)
                self.group.draw()
                self.onFrame.emit('merge')

            frame_end_time = time.time_ns() / 1000000000
            diff = frame_end_time - frame_start_time
            self.last_chunk_time += diff
            if diff < 0.025:
                # print(0.025 - diff)
                time.sleep(0.025 - diff)
            else:
                print("/!\\ diff HIGH" + str(diff))
