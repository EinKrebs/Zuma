import math
import random
import unittest
from PyQt5.QtGui import QColor
from Ellipse import Ellipse
from Shot import Shot
from Ball import Ball


class Game:
    def __init__(self,
                 ellipse: Ellipse,
                 balls: list,
                 radius: float,
                 speed: float,
                 shot_speed: float,
                 turret: tuple):
        self.colors = [QColor(0, 0, 0), QColor(0, 255, 0)]
        self.turret_angle = math.pi / 2
        self.turret_ball = random.randint(0, len(self.colors) - 1)
        self.ellipse = ellipse
        self.next_balls = balls
        self.balls = []
        self.shot_balls = []
        self.radius = radius
        self.speed = speed
        self.shot_speed = shot_speed
        self.turret = turret
        self.left = False
        self.right = False
        self.turret_speed = 0.02
        self.ping = 0

    def go_next_state(self):
        if self.left:
            self.turn_turret(-self.turret_speed)
        elif self.right:
            self.turn_turret(self.turret_speed)
        self.move_balls()
        self.move_shot_balls()
        self.new_ball()
        self.ping -= 1 if self.ping > 0 else 0

    def move_balls(self):
        i = 0
        while i < len(self.balls):
            ball = self.balls[i]
            next_point = self.ellipse.next_point(ball.point, self.speed)
            if next_point is None:
                self.balls.pop(i)
            else:
                ball.point = next_point
                i += 1

    def move_shot_balls(self):
        i = 0
        while i < len(self.shot_balls):
            ball = self.shot_balls[i]
            if ball.is_intersection(self.ellipse):
                self.shot_balls.pop(i)
            else:
                ball.update()
                i += 1

    def new_ball(self):
        if (len(self.balls) == 0 or self.ellipse.is_space(
                self.balls[-1].point,
                self.radius)) and len(self.next_balls) > 0:
            ellipse = self.ellipse
            self.balls.append(Ball(ellipse.next_point(
                ellipse.get_coordinates(ellipse.start),
                self.radius),
                self.colors[self.next_balls[-1]]))
            self.next_balls.pop()

    def shoot(self):
        if self.ping > 0:
            return
        self.shot_balls.append(
            Shot(self.turret[0], self.turret[1],
                 self.colors[self.turret_ball],
                 self.turret_angle,
                 self.shot_speed)
        )
        self.ping = 20
        self.turret_ball = random.randint(0, len(self.colors) - 1)

    def turn_turret(self, angle):
        self.turret_angle += angle
        if self.turret_angle < 0:
            self.turret_angle = 0
        if self.turret_angle > math.pi:
            self.turret_angle = math.pi


class GameTests(unittest.TestCase):
    def test_init(self):
        try:
            game = Game(Ellipse(2, 5, 0, math.pi), [1, 0, 2], 1, 1, 3, (0, 0))
        except TypeError:
            self.fail()

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
