import unittest
import random
import math

from domain.ellipse import Ellipse
import math_extensions as math_ext
from math_extensions import get_distance


class EllipseTests(unittest.TestCase):
    @staticmethod
    def get_random_ellipse():
        random.seed = 100
        start = random.random() % math.pi
        finish = start + random.random() % (math.pi - start)
        width = random.randint(1, 100)
        height = random.randint(1, 100)
        ellipse = Ellipse(width, height, start, finish)
        return start, finish, width, height, ellipse

    def test_from_string(self):
        random.seed = 100
        for repeat in range(10000):
            width = random.randint(1, 400)
            height = random.randint(1, 400)
            start = random.randint(0, 179)
            finish = random.randint(start, 180)
            ellipse = Ellipse.from_string(f'{width} {height} '
                                          f'{start} {finish}')
            self.assertEqual(ellipse.width, width)
            self.assertEqual(ellipse.height, height)
            self.assertAlmostEqual(ellipse.start / math.pi * 180,
                                   start)
            self.assertAlmostEqual(ellipse.finish / math.pi * 180,
                                   finish)

    def test_get_coords(self):
        for repeat in range(100000):
            random.seed = 100
            start, finish, width, height, ellipse = self.get_random_ellipse()
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            self.assertIn(point, ellipse)
            self.assertAlmostEqual(math.atan2(point[1], point[0]), angle)

    def test_get_biased_coordinates_simple(self):
        ellipse = Ellipse(2, 4, 0, math.pi)
        angle = math.pi / 4
        height = 2
        point = ellipse.get_coordinates(angle, (0, height))
        self.assertIn(point, ellipse)

    def test_get_biased_coordinates(self):
        random.seed = 100
        for repeat in range(100000):
            start, finish, width, height, ellipse = self.get_random_ellipse()
            angle = random.random() % math.pi
            height = random.random() % ellipse.height
            point = ellipse.get_coordinates(angle, (0, height))
            self.assertIn(point, ellipse)
            self.assertAlmostEqual(
                math_ext.get_angle((point[0], point[1] - height)), angle)

    # noinspection DuplicatedCode
    def test_next_point(self):
        random.seed = 100
        for repeat in range(100000):
            start, finish, width, height, ellipse = self.get_random_ellipse()
            radius = random.randint(1, 5)
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            next_point = ellipse.next_point(point, radius)
            if next_point is None:
                self.assertLess(get_distance(
                    point,
                    ellipse.get_coordinates(finish)), radius - 1e-6)
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

    # noinspection DuplicatedCode
    def test_previous_point(self):
        random.seed = 100
        for repeat in range(100000):
            start, finish, width, height, ellipse = self.get_random_ellipse()
            radius = random.randint(1, 5)
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            previous_point = ellipse.previous_point(point, radius)
            if previous_point is None:
                self.assertLess(get_distance(point, ellipse.start_point),
                                radius - 1e-6)
                return
            dist = get_distance(previous_point, point)
            self.assertTrue(previous_point in ellipse,
                            previous_point[0] * previous_point[0] / (
                                    ellipse.width * ellipse.width) +
                            previous_point[1] * previous_point[1] / (
                                    ellipse.height * ellipse.height))
            self.assertLess(abs(dist - radius), 1e-6,
                            msg=f"{previous_point[0]}, {previous_point[1]},"
                                f" {dist}, {radius}")
