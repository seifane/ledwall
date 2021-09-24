import math
import random

from Core import Core
from Effects.Attributes.IntAttribute import IntAttribute
from Effects.Attributes.IntRangeAttribute import IntRangeAttribute
from Effects.BaseEffect import BaseEffect
from LedGroup import LedGroup
from colorutils import Color
from typing import Tuple, List

class Spot:
    position: Tuple[float, float]
    dir_vector: Tuple[float, float]
    target_max_distance: float
    max_distance: float
    color: Color


class HaloEffect(BaseEffect):
    def __init__(self, core: Core) -> None:
        super().__init__()
        self.core = core

        self.spots = []

        self.attributes = {
            'item_amount': IntAttribute(1, 50, 5),
            'speed_range': IntRangeAttribute(5, 200, (20, 50))
        }

    @staticmethod
    def get_name():
        return 'Halo effect'

    def get_attributes(self):
        return self.attributes

    def get_attribute_value(self, attribute_name: str):
        return self.attributes[attribute_name].value

    def set_attribute_value(self, attribute_name: str, value: any):
        self.attributes[attribute_name].value = value

    def create_new_spot(self):
        spot = Spot()
        speedRange = self.get_attribute_value('speed_range')
        speedX = random.uniform(speedRange[0] / 100, speedRange[1] / 100)
        speedY = random.uniform(speedRange[0] / 100, speedRange[1] / 100)
        if random.randint(0, 1) % 2 == 1:
            speedX *= -1
        if random.randint(0, 1) % 2 == 1:
            speedY *= -1
        spot.dir_vector = (speedX, speedY)

        posX = random.uniform(0, self.core.group.width)
        posY = random.uniform(0, self.core.group.height)
        spot.position = (posX, posY)

        spot.target_max_distance = random.uniform(1, 4)
        spot.max_distance = 0
        spot.color = Color((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        self.spots.append(spot)

    def draw(self, buffer: [[Color]]):
        for x in range(self.core.group.width):
            for y in range(self.core.group.height):
                intensity = 0
                for spot in self.spots:
                    distance = self.get_distance((x, y), spot.position)
                    if distance < spot.max_distance:
                        intensity += (1 - (distance / spot.max_distance)) * 255
                if intensity > 255:
                    intensity = 255
                buffer[x][y] = (255, 255, 255, int(intensity))

        for spot in self.spots:
            x = spot.dir_vector[0] + spot.position[0]
            y = spot.dir_vector[1] + spot.position[1]
            spot.position = (x, y)
            if spot.max_distance < spot.target_max_distance:
                spot.max_distance += 0.3
            if (spot.position[0] - spot.max_distance > self.core.group.width or
                    spot.position[1] - spot.max_distance > self.core.group.height or
                    spot.position[0] < -spot.max_distance or
                    spot.position[1] < -spot.max_distance):
                self.spots.remove(spot)

        needToAdd = self.get_attribute_value('item_amount') - len(self.spots)
        if needToAdd > 0:
            for i in range(needToAdd):
                self.create_new_spot()

        return buffer



    def get_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]):
        return math.sqrt(math.pow(pos1[0] - pos2[0], 2) + math.pow(pos1[1] - pos2[1], 2))