import math
import typing


class Shot:
    def __init__(self, x, y, color, angle, speed, penetrate=False):
        self.color = color
        self.angle = angle
        self.speed = speed
        self.x = x
        self.y = y
        self.penetrate = penetrate

    def update(self):
        self.x, self.y = self.get_next_coord()

    def get_next_coord(self) -> typing.Tuple[int, int]:
        return (self.x + math.cos(self.angle) * self.speed,
                self.y + math.sin(self.angle) * self.speed)

    def is_intersection(self, ellipse):
        x, y = self.get_next_coord()
        return ((x ** 2 / ellipse.width ** 2
                 + y ** 2 / ellipse.height ** 2)
                > 1 + 1e-6 >
                (self.x ** 2 / ellipse.width ** 2
                 + self.y ** 2 / ellipse.height ** 2)
                or (x ** 2 / ellipse.width ** 2
                    + y ** 2 / ellipse.height ** 2)
                < 1 + 1e-6 <
                (self.x ** 2 / ellipse.width ** 2
                 + self.y ** 2 / ellipse.height ** 2))

    def copy(self):
        return Shot(self.x, self.y, self.color, self.angle, self.speed)
