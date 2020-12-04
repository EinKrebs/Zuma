import math
import unittest

import math_extensions as math_ext
from domain.ball import Ball
from domain.ellipse import Ellipse
from domain.sequence import Sequence


class SequenceTests(unittest.TestCase):
    def test_get_left(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        radius = 5
        ball = Ball(ellipse.next_point(ellipse.start_point, radius),
                    (0, 0, 0))
        sequence = Sequence(ball, ellipse, radius)
        self.assertEqual(sequence.left, ellipse.previous_point(
            sequence.balls[0].point,
            2 * radius,
            start=-1.5
        ))
        self.assertAlmostEqual(
            math_ext.get_distance(
                sequence.balls[0].point,
                sequence.left),
            2 * radius,
            delta=1e-4
        )

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
        sequence.collapse(1)
        self.assertEqual(len(sequence.balls), 4)
        sequence.balls[0].collapsing = True
        sequence.collapse(1)
        self.assertEqual(len(sequence.balls), 1)

    # noinspection SpellCheckingInspection
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

        score += sequence.collapse(1)[2]
        self.assertEqual(len(sequence.balls), 4)
        score += sequence.collapse(1)[2]
        self.assertEqual(len(sequence.balls), 1)
        self.assertEqual(score, 6)