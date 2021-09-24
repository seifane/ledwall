import collections
import threading
from typing import List

import sacn
from colorutils import Color

from helpers import rgba_to_rgb


class LedGroup:
    height: int
    width: int

    buffer: [[tuple[int, int, int, int]]]
    mapping = {}
    sender = None

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width

        self.buffer_lock = threading.Lock()

        self.buffer = self.create_buffer()
        self.init_mapping()

        self.sender = sacn.sACNsender()  # provide an IP-Address to bind to if you are using Windows and want to use multicast
        self.sender.fps = 40
        self.sender.activate_output(1)
        self.sender.activate_output(2)
        self.sender.activate_output(3)
        self.sender.activate_output(4)
        self.sender[1].destination = "192.168.1.50"  # or provide unicast information.
        self.sender[2].destination = "192.168.1.52"  # or provide unicast information.
        self.sender[3].destination = "192.168.1.50"  # or provide unicast information.
        self.sender[4].destination = "192.168.1.50"  # or provide unicast information.
        self.sender.start()  # start the sending thread

    def stop(self):
        self.sender.stop()

    def create_buffer(self):
        buffer = []
        for x in range(self.width):
            line = []
            for y in range(self.height):
                line.append((0, 0, 0, 0))
            buffer.append(line)
        return buffer

    # def init_mapping(self):
    #     for x in range(31, -1, -1):
    #         for y in range(16):
    #             i = (32 - x) * 8 + (int(y / 8) * 256) + y % 8
    #             self.mapping[i] = (x, y)
    #     self.mapping = collections.OrderedDict(sorted(self.mapping.items()))

    def init_mapping(self):
        i = 0
        for x in range(self.width):
            for y in range(self.height):
                self.mapping[i] = (x, y)
                i = i + 1

    def set_buffer(self, buffer: [[Color]]):
        self.buffer = buffer

    # def blit(self, surface: Surface):
    #     for x in range(surface.get_width()):
    #         for y in range (surface.get_height()):
    #             surface_color = surface.get_at((x, y))
    #             self.buffer[x][y] = Color(rgba_to_rgb((
    #                 surface_color.r,
    #                 surface_color.g,
    #                 surface_color.b,
    #                 surface_color.a,
    #             )))

    def draw(self):
        count = 0
        packets = [[], [], [], []]
        for pixel in self.mapping.items():
            packetIdx = int(count / 170)
            rgba = self.buffer[pixel[1][0]][pixel[1][1]]
            rgb = rgba_to_rgb(rgba)
            packets[packetIdx].append(rgb[0])
            packets[packetIdx].append(rgb[1])
            packets[packetIdx].append(rgb[2])
            count += 1

        packets[1] = packets[0]

        count = 1
        for packet in packets:
            self.sender[count].dmx_data = tuple(packet)
            count += 1
        self.sender.flush()