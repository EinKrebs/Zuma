import random
import unittest
import math

from Ellipse import Ellipse
from Level import Level
from Ball import Ball
from MathExtentions import get_distance
import MathExtentions as mathExt


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
                mathExt.get_angle((point[0], point[1] - height)), angle)

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


class GameTests(unittest.TestCase):
    def test_move_balls_next_state(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        game = Level(
            ellipse,
            [],
            5,
            5,
            150,
            (0, 0)
        )
        game.balls.append(
            Ball(
                ellipse.next_point(ellipse.start_point,
                                   100),
                (game.colors[0])
            )
        )
        game.balls.append(
            Ball(
                ellipse.next_point(ellipse.start_point,
                                   5),
                (game.colors[0])
            )
        )
        expected = [
            game.balls[0].point,
            ellipse.next_point(game.balls[1].point, 5)
        ]
        game.go_next_state()
        self.assertListEqual(
            [ball.point for ball in game.balls],
            expected
        )

    def test_shot_first(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        game = Level(
            ellipse,
            [0],
            5,
            50,
            150,
            (0, 0)
        )
        game.go_next_state()
        game.go_next_state()
        game.speed = 0
        shot_angle = mathExt.get_biased_angle(
            game.balls[0].point,
            game.turret
        ) + 0.1
        expected_new = ellipse.next_point(game.balls[0].point, 10)
        expected_old = game.balls[0].point
        game.turret_angle = shot_angle
        game.turret_ball = 1
        game.shoot()
        game.go_next_state()
        self.assertTupleEqual(game.balls[0].color, game.colors[1])
        self.assertTupleEqual(game.balls[1].color, game.colors[0])
        self.assertAlmostEqual(expected_new[0], game.balls[0].point[0], 4)
        self.assertAlmostEqual(expected_new[1], game.balls[0].point[1], 4)
        self.assertAlmostEqual(expected_old[0], game.balls[1].point[0], 4)
        self.assertAlmostEqual(expected_old[1], game.balls[1].point[1], 4)

    def test_shot_last(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        game = Level(
            ellipse,
            [0],
            5,
            50,
            150,
            (0, 0)
        )
        game.go_next_state()
        game.go_next_state()
        game.go_next_state()
        game.speed = 0
        shot_angle = mathExt.get_biased_angle(
            game.balls[0].point,
            game.turret
        ) - 0.1
        expected_new = ellipse.get_coordinates(
            shot_angle,
            game.turret
        )
        expected_old = ellipse.next_point(expected_new, 10)
        game.turret_angle = shot_angle
        game.turret_ball = 1
        game.shoot()
        game.go_next_state()
        self.assertTupleEqual(game.balls[0].color, game.colors[0])
        self.assertTupleEqual(game.balls[1].color, game.colors[1])
        self.assertAlmostEqual(expected_new[0], game.balls[1].point[0], 4)
        self.assertAlmostEqual(expected_new[1], game.balls[1].point[1], 4)
        self.assertAlmostEqual(expected_old[0], game.balls[0].point[0], 4)
        self.assertAlmostEqual(expected_old[1], game.balls[0].point[1], 4)

    def test_collapsing_simple(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        radius = 5
        game = Level(ellipse, [], radius, 0, 0, (0, 0))
        game.balls.append(Ball(ellipse.get_coordinates(0.3, game.turret),
                               game.colors[0]))
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[0])
        )
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[0])
        )
        ball = Ball(ellipse.next_point(game.balls[0].point, 2 * radius),
                    game.colors[1])
        game.balls.insert(
            0,
            ball
        )
        game.balls[1].collapsing = True
        game.go_next_state()
        self.assertListEqual(game.balls, [ball])

    def test_multicollapsing(self):
        ellipse = Ellipse(1000, 1000, 0, math.pi)
        radius = 5
        game = Level(ellipse, [], radius, 0, 0, (0, 0))
        game.balls.append(Ball(ellipse.get_coordinates(0.3, game.turret),
                               game.colors[1]))
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[0])
        )
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[0])
        )
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[0])
        )
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[1])
        )
        game.balls.insert(
            0,
            Ball(ellipse.next_point(game.balls[0].point, 2 * radius), game.colors[1])
        )
        game.balls[4].collapsing = True
        game.go_next_state()
        game.go_next_state()
        self.assertListEqual(game.balls, [])


if __name__ == '__main__':
    game_tests = GameTests()
    ellipse_tests = EllipseTests()
    ellipse_tests.test_get_coords()
    ellipse_tests.test_next_point()
