import math
from MathExtentions import get_distance, get_angle, sign,\
    bin_search, tern_search


class Ellipse:
    def __init__(self, width, height, start, finish):
        self.width = width
        self.height = height
        self.start = start
        self.finish = finish

    def __contains__(self, item):
        return item[1] >= -1e-6 and abs(
            (item[0] * item[0] / (self.width * self.width) + item[1] * item[
                1] / (self.height * self.height)) - 1) < 1e-6

    def get_coordinates(self, angle):
        if angle == 0:
            return self.width, 0
        if angle == math.pi / 2:
            return 0, self.height
        if angle == math.pi:
            return -self.width, 0
        x = sign(math.cos(angle)) * self.width * self.height / math.sqrt(
            self.height ** 2 + (self.width * math.tan(angle)) ** 2)
        return x, math.tan(angle) * x

    def next_point(self, point, distance):
        start = get_angle(point)
        finish = self.finish
        middle = tern_search(start, finish,
                             lambda x: get_distance(
                                 self.get_coordinates(x), point))
        angle1 = bin_search(start, middle, lambda x: get_distance(
            self.get_coordinates(x), point), distance)
        angle2 = bin_search(middle, finish, lambda x: -get_distance(
            self.get_coordinates(x), point), distance)
        if abs(get_distance(self.get_coordinates(angle1),
                            point) - distance) < 1e-6:
            return self.get_coordinates(angle1)
        if abs(get_distance(self.get_coordinates(angle2),
                            point) - distance) < 1e-6:
            return self.get_coordinates(angle2)
        return None

    def is_space(self, last, radius):
        return get_distance(last,
                            self.get_coordinates(self.start)) > 3 * radius
