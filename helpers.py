import math

import colorutils
from colorutils import Color


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def chunk_based_on_number(lst, chunk_numbers):
    n = math.ceil(len(lst) / chunk_numbers)

    for x in range(0, len(lst), n):
        each_chunk = lst[x: n + x]

        if len(each_chunk) < n:
            each_chunk = each_chunk + [None for y in range(n - len(each_chunk))]
        yield each_chunk


def rgba_to_rgb(rgba):
    return (
        int(rgba[3] / 255 * rgba[0]),
        int(rgba[3] / 255 * rgba[1]),
        int(rgba[3] / 255 * rgba[2]),
    )


def rgb_to_hsv(rgb: tuple[int, int, int, int]) -> tuple[int, int, int]:
    hsv = colorutils.rgb_to_hsv((rgb[0] / 255, rgb[1] / 255, rgb[2] / 255))
    return int(hsv[0] * 360), int(hsv[1] * 100), int(hsv[2] * 100)

def hsv_to_rgb(hsv: tuple[int, int, int]) -> tuple[int, int, int, int]:
    rgb = colorutils.hsv_to_rgb((hsv[0], hsv[1] / 100, hsv[2] / 100))
    return int(rgb[0]), int(rgb[1]), int(rgb[2]), 255

