from math_extensions import get_distance


class Ball:
    def __init__(self, point, color):
        self.point = point
        self.color = color
        self.collapsing = False
        self.exploding = False

    def __eq__(self, other):
        return (self.color == other.color
                and get_distance(self.point, other.point) < 1e-4)

    def __str__(self):
        return str(self.point)
