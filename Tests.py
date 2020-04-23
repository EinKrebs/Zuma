import random
import unittest
import math
from Ellipse import Ellipse
from Game import Game
from MathExtentions import get_distance


class EclipseTest(unittest.TestCase):
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
            start, finish, width, height, ellipse = self.get_random_ellipse()
            angle = random.random() % math.pi
            point = ellipse.get_coordinates(angle)
            self.assertIn(point, ellipse)
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


class GameTests(unittest.TestCase):
    # TODO: rewrite this
    def test_shot(self):
        game = Game(Ellipse(2, 5, 0, math.pi), [1, 0], 1, 1, 1, (0, 0))
        game.shoot()
        game.turn_turret(-math.pi / 4)
        game.shoot()
        first_shot = []
        second_shot = []
        while len(game.shot_balls) > 0:
            first_shot.append(game.shot_balls[0].copy())
            if len(game.shot_balls) > 1:
                second_shot.append(game.shot_balls[1].copy())
            game.go_next_state()
        self.assertAlmostEqual(first_shot[0].x, 0)
        self.assertAlmostEqual(first_shot[0].y, 0)
        self.assertAlmostEqual(first_shot[1].x, 0)
        self.assertAlmostEqual(first_shot[1].y, 1)
        self.assertAlmostEqual(first_shot[2].x, 0)
        self.assertAlmostEqual(first_shot[2].y, 2)
        self.assertAlmostEqual(first_shot[3].x, 0)
        self.assertAlmostEqual(first_shot[3].y, 3)
        self.assertAlmostEqual(first_shot[4].x, 0)
        self.assertAlmostEqual(first_shot[4].y, 4)
        self.assertAlmostEqual(second_shot[0].x, 0)
        self.assertAlmostEqual(second_shot[0].y, 0)
        self.assertAlmostEqual(second_shot[1].x, 1 / math.sqrt(2))
        self.assertAlmostEqual(second_shot[1].y, 1 / math.sqrt(2))

    def test_game(self):
        game = Game(Ellipse(960, 1080, 0, math.pi), [1, 0, 1, 1], 20, 10,
                    40, (0, 0))
        try:
            while len(game.next_balls) > 0 or len(game.balls) > 0:
                game.go_next_state()
        except (TypeError, IndexError):
            self.fail()
