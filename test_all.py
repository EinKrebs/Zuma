import random
import unittest
import math

from Ellipse import Ellipse
from Level import Level
from Ball import Ball
from Sequence import Sequence
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
        random.seed = 100
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


class LevelTest(unittest.TestCase):
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
        game.turret_ball = 0
        game.shoot()
        game.go_next_state()
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
        game.turret_ball = 0
        game.shoot()
        game.go_next_state()
        self.assertAlmostEqual(expected_new[0], game.balls[1].point[0], 4)
        self.assertAlmostEqual(expected_new[1], game.balls[1].point[1], 4)
        self.assertAlmostEqual(expected_old[0], game.balls[0].point[0], 4)
        self.assertAlmostEqual(expected_old[1], game.balls[0].point[1], 4)


class SequenceTests(unittest.TestCase):
    def test_add_ball(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        ball = Ball(
            ellipse.get_coordinates(1),
            (0, 0, 0)
        )
        radius = 5
        sequence = Sequence(ball, ellipse, radius)
        sequence.add_ball((0, 255, 0))
        expected = [ball,
                    Ball(
                        ellipse.previous_point(ball.point, 2 * radius),
                        (0, 255, 0))]
        self.assertEqual(len(sequence.balls), 2)
        for i in range(2):
            self.assertEqual(sequence.balls[i].color, expected[i].color)
            self.assertEqual(sequence.balls[i].point, expected[i].point)
        self.assertEqual(
            sequence.left,
            ellipse.previous_point(sequence.balls[1].point, 2 * radius))

    def test_move_balls_next_state(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        radius = 5
        sequence = Sequence(
            Ball(
                ellipse.next_point(ellipse.start_point,
                                   50),
                (0, 0, 0)),
            ellipse,
            radius
        )
        sequence.balls.append(
            Ball(
                ellipse.next_point(ellipse.start_point,
                                   3 * radius),
                (0, 0, 0)
            )
        )
        expected = [
            sequence.balls[0].point,
            ellipse.next_point(sequence.balls[1].point, radius)]
        sequence.move(radius)
        self.assertListEqual(
            [ball.point for ball in sequence.balls],
            expected
        )

    def test_insert_ball(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        radius = 5
        sequence = Sequence(
            Ball(
                ellipse.next_point(ellipse.start_point,
                                   50),
                (0, 0, 0)),
            ellipse,
            radius
        )
        sequence.add_ball((0, 0, 0))
        sequence.add_ball((0, 0, 0))
        point = ellipse.next_point(sequence.balls[1].point, radius * 0.6)
        expected_points = ([ellipse.next_point(
                                sequence.balls[0].point,
                                2 * radius)] +
                           [ball.point for ball in sequence.balls])
        expected_colors = [(0, 0, 0), (0, 255, 0), (0, 0, 0), (0, 0, 0)]
        sequence.insert_ball(point, (0, 255, 0))
        for i in range(len(sequence.balls)):
            for j in range(2):
                self.assertAlmostEqual(sequence.balls[i].point[j],
                                       expected_points[i][j], delta=1e-2)
        self.assertListEqual([ball.color for ball in sequence.balls],
                             expected_colors)

    def test_collapsing_simple(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        radius = 5
        ball = Ball(ellipse.next_point(ellipse.start_point, 100), (0, 0, 0))
        sequence = Sequence(ball, ellipse, radius)
        sequence.add_ball((0, 0, 0))
        sequence.add_ball((0, 0, 0))
        sequence.add_ball((0, 255, 0))
        sequence.collapse()
        self.assertEqual(len(sequence.balls), 4)
        sequence.balls[0].collapsing = True
        sequence.collapse()
        self.assertEqual(len(sequence.balls), 1)

    def test_multicollapsing(self):
        ellipse = Ellipse(1000, 1000, 0, math.pi)
        radius = 5
        ball = Ball(ellipse.next_point(ellipse.start_point, 100), (0, 0, 0))
        sequence = Sequence(ball, ellipse, radius)
        sequence.add_ball((0, 0, 0))
        sequence.add_ball((0, 255, 0))
        sequence.add_ball((0, 255, 0))
        sequence.add_ball((0, 255, 0))
        sequence.add_ball((0, 0, 0))
        sequence.add_ball((0, 255, 0))
        sequence.balls[3].collapsing = True
        score = 0

        score += sequence.collapse()[2]
        self.assertEqual(len(sequence.balls), 4)
        score += sequence.collapse()[2]
        self.assertEqual(len(sequence.balls), 1)
        self.assertEqual(score, 6)


if __name__ == '__main__':
    unittest.main()
