import math
import unittest
import random


def get_distance(point1, point2):
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def bin_search(start, finish, param, value):  # function growth
    left = start
    right = finish
    for i in range(100):
        mid = (left + right) / 2
        mid_value = param(mid)
        if mid_value < value:
            left = mid
        else:
            right = mid
    return left


def tern_search(start, finish, param):  # function looks like -x^2
    left = start
    right = finish
    for i in range(100):
        mid_left = (9 * left + 8 * right) / 17
        mid_right = (8 * left + 9 * right) / 17
        if param(mid_left) <= param(mid_right):
            left = mid_left
        else:
            right = mid_right
    return left


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

    @staticmethod
    def sign(number):
        if abs(number) < 1e-6:
            return 0
        if number > 0:
            return 1
        return -1

    @staticmethod
    def get_angle(point):
        return math.atan2(point[1], point[0])

    def get_coordinates(self, angle):
        if angle == 0:
            return self.width, 0
        if angle == math.pi / 2:
            return 0, self.height
        if angle == math.pi:
            return -self.width, 0
        x = self.sign(math.cos(angle)) * self.width * self.height / math.sqrt(
            self.height ** 2 + (self.width * math.tan(angle)) ** 2)
        return x, math.tan(angle) * x

    def next_point(self, point, distance):
        start = self.get_angle(point)
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


# TODO: remove test from file


class EclipseTest(unittest.TestCase):
    @staticmethod
    def get_random_ellipse():
        start = random.random() % math.pi
        finish = start + random.random() % (math.pi - start)
        width = random.randint(1, 100)
        height = random.randint(1, 100)
        ellipse = Ellipse(width, height, start, finish)
        return start, finish, width, height, ellipse

    def test_get_coords(self):
        for repeat in range(100000):
            start, finish, width, height, ellipse = self.get_random_ellipse()
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            self.assertTrue(point in ellipse)
            self.assertAlmostEqual(math.atan2(point[1], point[0]), angle)

    def test_next_point(self):
        for repeat in range(100000):
            start, finish, width, height, ellipse = self.get_random_ellipse()
            radius = random.randint(1, 5)
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            next_point = ellipse.next_point(point, radius)
            if next_point is None:
                self.assertLess(get_distance(point, ellipse.get_coordinates(
                    finish)), radius - 1e-6)
                return
            dist = get_distance(next_point, point)
            self.assertTrue(next_point in ellipse,
                            next_point[0] * next_point[0] / (
                                    ellipse.width * ellipse.width) +
                            next_point[1] * next_point[1] / (
                                    ellipse.height * ellipse.height))
            self.assertLess(abs(dist - radius), 1e-6,
                            msg=f"{next_point[0]}, {next_point[1]},"
                                f" {dist}, {radius}")
