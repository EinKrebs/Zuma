import unittest
import random
import math

import math_extensions as math_ext
from domain.shot import Shot
from domain.ellipse import Ellipse


class ShotTests(unittest.TestCase):
    def test_update(self):
        random.seed = 100
        for repeat in range(100000):
            x = random.random()
            y = random.random()
            speed = random.random() % 100
            angle = random.random() % (2 * math.pi)
            shot = Shot(x, y, None, angle, speed)
            shot.update()
            x1 = shot.x
            y1 = shot.y
            self.assertAlmostEqual(math_ext.get_angle((x1 - x, y1 - y)), angle)
            self.assertAlmostEqual(
                math_ext.get_distance(
                    (x1, y1),
                    (x, y)),
                speed
            )

    def test_is_intersection(self):
        random.seed = 100
        ellipse = Ellipse(100, 50, 0, math.pi)
        x = 0
        y = 0
        for i in range(100000):
            angle = math.pi / 100000 * i
            speed = random.random() % 200
            shot = Shot(x, y, None, angle, speed)
            self.assertEqual(speed > 100.01, shot.is_intersection(ellipse))