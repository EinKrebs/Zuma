import random
import unittest
import math
import time

from Shot import Shot
from Ellipse import Ellipse
from Level import Level
from Game import Game
from Ball import Ball
from Sequence import Sequence
from MathExtentions import get_distance
import MathExtentions as mathExt


class ShotTest(unittest.TestCase):
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
            self.assertAlmostEqual(mathExt.get_angle((x1 - x, y1 - y)), angle)
            self.assertAlmostEqual(
                mathExt.get_distance(
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
            mathExt.get_distance(
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


class LevelTest(unittest.TestCase):
    def test_from_file(self):
        level = Level.from_file('test_levels\\test_level1.txt')
        self.assertListEqual(level.times, [10, 0])
        self.assertListEqual(level.next_sequences,
                             [[0, 0, 0, 1, 0],
                              [1, 0, 0, 0, 0]])
        self.assertIsNone(level.current_sequence_next)

    def test_shot_first(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        level = Level(
            ellipse,
            [[0]],
            [0],
            5,
            50,
            150,
            (0, 0)
        )
        time.sleep(1)
        level.go_next_state()
        level.go_next_state()
        level.speed = 0
        shot_angle = mathExt.get_biased_angle(
            level.sequences[0].balls[0].point,
            level.turret
        ) + 0.1
        expected_new = ellipse.next_point(level.balls[0].point, 10)
        expected_old = level.balls[0].point
        level.turret_angle = shot_angle
        level.turret_ball = 0
        level.shoot()
        level.go_next_state()
        self.assertAlmostEqual(expected_new[0], level.balls[0].point[0], 4)
        self.assertAlmostEqual(expected_new[1], level.balls[0].point[1], 4)
        self.assertAlmostEqual(expected_old[0], level.balls[1].point[0], 4)
        self.assertAlmostEqual(expected_old[1], level.balls[1].point[1], 4)

    def test_shot_last(self):
        ellipse = Ellipse(100, 100, 0, math.pi)
        level = Level(
            ellipse,
            [[0]],
            [0],
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
        shot_angle = mathExt.get_biased_angle(
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
        level.shoot()
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
        level.turret_angle = mathExt.get_biased_angle(
            level.balls[1].point,
            level.turret) + 0.1
        level.speed = 0
        level.shoot()
        level.go_next_state()
        level.go_next_state()
        level.go_next_state()
        self.assertEqual(len(level.balls), 0)
        self.assertTrue(level.finished)
        self.assertEqual(level.score, 3)
        self.assertEqual(len(level.color_count), 0)
        
        
class GameTests(unittest.TestCase):
    @staticmethod
    def two_dim_lists_equal(first, second, param):
        cond = len(first) == len(second)
        if cond:
            for i in range(len(first)):
                cond1 = (len(param(first[i]))
                         == len(param(second[i])))
                if cond1:
                    for j in range(len(param(first[i]))):
                        cond1 = (cond1
                                 and param(first[i])[j]
                                 == param(second[i])[j])
                cond = cond and cond1
        return cond

    @staticmethod
    def level_equals(first: Level, second: Level):
        cond = GameTests.two_dim_lists_equal(first.sequences,
                                             second.sequences,
                                             lambda x: x.balls)
        cond = cond and GameTests.two_dim_lists_equal(
            first.next_sequences,
            second.next_sequences,
            lambda x: x
        )
        if not cond:
            return cond
        if ((first.current_sequence_next is None
                and second.current_sequence_next is not None)
                or (first.current_sequence_next is not None
                    and second.current_sequence_next is None)):
            return False
        if first.current_sequence_next is None:
            return True
        if (len(first.current_sequence_next)
                != len(second.current_sequence_next)):
            return False
        for i in range(len(first.current_sequence_next)):
            if (first.current_sequence_next[i]
                    != second.current_sequence_next[i]):
                return False
        return True
    
    def test_general(self):
        game = Game.from_directory('test_levels')
        level = Level.from_file('test_levels\\test_level1.txt')
        self.assertTrue(self.level_equals(level, game.current_level))
        game.update()
        level.go_next_state()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.current_level.finished = True
        game.update()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.current_level.hp = 0
        game.current_level.finished = False
        game.update()
        self.assertTrue(self.level_equals(level, game.current_level))
        game.next_level()
        level = Level.from_file('test_levels\\test_level2.txt')
        self.assertTrue(self.level_equals(level, game.current_level))
        game.next_level()
        self.assertEqual(game.over, 1)
        self.assertIsNone(game.current_level)


if __name__ == '__main__':
    unittest.main()
