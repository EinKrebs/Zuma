import math
import math_extensions as mathExt
from math_extensions import (get_distance, get_angle, bin_search,
                             tern_search, solve_square_poly)


class Ellipse:
    @staticmethod
    def from_string(s: str):
        args = list(map(int, s.split()))
        return Ellipse(args[0],
                       args[1],
                       args[2] / 180 * math.pi,
                       args[3] / 180 * math.pi)

    def __init__(self, width, height, start, finish):
        self.width = width
        self.height = height
        self.start = start
        self.finish = finish
        self.start_point = self.get_coordinates(self.start)
        self.finish_point = self.get_coordinates(self.finish)

    def __contains__(self, item):
        return item[1] >= -1e-6 and abs(
            (item[0] * item[0] / (self.width * self.width) + item[1] * item[
                1] / (self.height * self.height)) - 1) < 1e-6

    def get_coordinates(self, angle, point=(0, 0)):
        x1, x2 = solve_square_poly(
            self.height ** 2 + (self.width * math.tan(angle)) ** 2,
            2 * point[1] * math.tan(angle) * (self.width ** 2),
            self.width ** 2 * ((point[1]) ** 2 - self.height ** 2))
        if angle < math.pi / 2 + 1e-6:
            return x2, math.tan(angle) * x2 + point[1]
        else:
            return x1, math.tan(angle) * x1 + point[1]

    def next_point(self, point, distance, finish=None):
        if not finish:
            finish = self.finish
        start = get_angle(point)
        middle = tern_search(start, finish,
                             lambda x: get_distance(
                                 self.get_coordinates(x), point))
        angle1 = bin_search(start, middle, lambda x: get_distance(
            self.get_coordinates(x), point), distance)
        angle2 = bin_search(middle, finish, lambda x: -get_distance(
            self.get_coordinates(x), point), distance)
        dist1 = get_distance(self.get_coordinates(angle1), point)
        dist2 = get_distance(self.get_coordinates(angle2), point)
        if abs(dist1 - distance) < 1e-6:
            return self.get_coordinates(angle1)
        if abs(dist2 - distance) < 1e-6:
            return self.get_coordinates(angle2)
        return None

    def previous_point(self, point, distance, start=None):
        if not start:
            start = self.start
        angle = math.pi - get_angle(point)
        rev_point = self.get_coordinates(angle)
        rev_next_point = self.next_point(
            rev_point,
            distance,
            finish=math.pi - start)
        if not rev_next_point:
            return None
        previous_point = self.get_coordinates(
            mathExt.normalise_angle(math.pi - get_angle(rev_next_point)))
        return previous_point

    def is_space(self, last, radius):
        return get_distance(last,
                            self.get_coordinates(self.start)) > 3 * radius

    def get_distance(self, angle1, angle2):
        return get_distance(self.get_coordinates(angle1),
                            self.get_coordinates(angle2))

    def check_point_pre_started(self, point, distance):
        point_angle = get_angle(point)
        return (
                point_angle < self.start
                or get_distance(point, self.start_point) < distance
        )

    def check_point_finished(self, point, distance):
        point_angle = get_angle(point)
        return (
                self.finish < point_angle
                or get_distance(point, self.finish_point) < distance
        )
