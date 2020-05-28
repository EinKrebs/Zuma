from MathExtentions import get_distance


class Ball:
    def __init__(self, point, color):
        self.point = point
        self.color = color
        self.collapsing = False

    def __eq__(self, other):
        return (self.color == other.color
                and get_distance(self.point, other.point) < 1e-4)
