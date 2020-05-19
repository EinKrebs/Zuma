import math
from MathExtentions import sqr


class Shot:
    def __init__(self, x, y, color, angle, speed):
        self.color = color
        self.angle = angle
        self.speed = speed
        self.x = x
        self.y = y

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def is_intersection(self, ellipse):
        x = self.x + math.cos(self.angle) * self.speed
        y = self.y + math.sin(self.angle) * self.speed
        return sqr(x) / sqr(ellipse.width) + sqr(y) / sqr(
            ellipse.height) > 1 + 1e-6 > sqr(self.x) / sqr(
            ellipse.width) + sqr(self.y) / sqr(ellipse.height)

    def copy(self):
        return Shot(self.x, self.y, self.color, self.angle, self.speed)
