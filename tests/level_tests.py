import math
import time
import unittest

import math_extensions as math_ext
from domain.ellipse import Ellipse
from domain.level import Level


class LevelTests(unittest.TestCase):
    def test_from_file(self):
        level = Level.from_file('test_levels/test_level1.txt')
        self.assertListEqual(level.times, [10, 0])
        self.assertListEqual(level.next_sequences,
                             [[0, 0, 0, 1, 0],
                              [1, 0, 0, 0, 0]])
        self.assertIsNone(level.current_sequence_next)

    # noinspection DuplicatedCode
    def test_shot_first(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        level = Level(
            ellipse,
            [[0]],
            [0],
            None,
            5,
            50,
            150,
            (0, 0)
        )
        time.sleep(1)
        level.go_next_state()
        level.go_next_state()
        level.speed = 0
        shot_angle = math_ext.get_biased_angle(
            level.sequences[0].balls[0].point,
            level.turret
        ) + 0.1
        expected_new = ellipse.next_point(level.balls[0].point, 10)
        expected_old = level.balls[0].point
        level.turret_angle = shot_angle
        level.turret_ball = 0
        level.shoot(False)
        level.go_next_state()
        self.assertAlmostEqual(expected_new[0], level.balls[0].point[0], 4)
        self.assertAlmostEqual(expected_new[1], level.balls[0].point[1], 4)
        self.assertAlmostEqual(expected_old[0], level.balls[1].point[0], 4)
        self.assertAlmostEqual(expected_old[1], level.balls[1].point[1], 4)

    # noinspection DuplicatedCode
    def test_shot_last(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        level = Level(
            ellipse,
            [[0]],
            [0],
            None,
            5,
            50,
            150,
            (0, 0)
        )
        time.sleep(1)
        level.go_next_state()
        level.go_next_state()
        level.go_next_state()
        level.speed = 0
        shot_angle = math_ext.get_biased_angle(
            level.balls[0].point,
            level.turret
        ) - 0.1
        expected_new = ellipse.get_coordinates(
            shot_angle,
            level.turret
        )
        expected_old = ellipse.next_point(expected_new, 10)
        level.turret_angle = shot_angle
        level.turret_ball = 0
        level.shoot(False)
        level.go_next_state()
        self.assertAlmostEqual(expected_new[0], level.balls[1].point[0], 2)
        self.assertAlmostEqual(expected_new[1], level.balls[1].point[1], 2)
        self.assertAlmostEqual(expected_old[0], level.balls[0].point[0], 2)
        self.assertAlmostEqual(expected_old[1], level.balls[0].point[1], 2)

    def test_fail(self):
        ellipse = Ellipse(100, 50, 0, math.pi)
        level = Level(ellipse, [[0, 0, 0]], [0], radius=10, speed=100)
        time.sleep(1)
        for i in range(1000):
            level.go_next_state()
        self.assertEqual(level.hp, 0)

    def test_turret(self):
        ellipse = Ellipse(100, 50, 0, math.pi)
        level = Level(ellipse, [[0]], [0], radius=10, speed=0)
        level.left = True
        self.assertAlmostEqual(level.turret_angle, math.pi / 2)
        for i in range(50):
            level.go_next_state()
        self.assertAlmostEqual(level.turret_angle, math.pi / 2 - 1)
        level.left = False
        level.right = True
        for i in range(100):
            level.go_next_state()
        self.assertAlmostEqual(level.turret_angle, math.pi / 2 + 1)

    def test_collapse(self):
        ellipse = Ellipse(200, 100, 0, math.pi)
        level = Level(ellipse, [[0, 0]], [0],
                      radius=10, speed=10, shot_speed=250)
        time.sleep(1)
        for i in range(4):
            level.go_next_state()
        self.assertEqual(len(level.balls), 2)
        self.assertEqual(len(level.color_count), 1)
        self.assertEqual(level.color_count[0], 2)
        level.turret_angle = math_ext.get_biased_angle(
            level.balls[1].point,
            level.turret) + 0.1
        level.speed = 0
        level.shoot(False)
        level.go_next_state()
        level.go_next_state()
        level.go_next_state()
        self.assertEqual(len(level.balls), 0)
        self.assertTrue(level.finished)
        self.assertEqual(len(level.color_count), 0)
