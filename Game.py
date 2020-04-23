import math
import random
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
        self.colors = [(0, 0, 0), (0, 255, 0)]
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
        self.ping = max(self.ping - 1, 0)

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
        if (not self.balls or self.ellipse.is_space(
                self.balls[-1].point,
                self.radius)) and self.next_balls:
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
