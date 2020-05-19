import math
import random
import time
from Ellipse import Ellipse
from Shot import Shot
from Ball import Ball
import MathExtentions as mathExt


class Level:
    def __init__(self,
                 ellipse: Ellipse,
                 balls: list):
        self.colors = [(0, 0, 0), (0, 255, 0)]
        self.ellipse = ellipse
        self.next_balls = balls
        self.radius = 20
        self.speed = 1
        self.shot_speed = 150
        self.turret = (0, 90)

        self.balls = []
        self.shots = []
        self.turret_angle = math.pi / 2
        self.turret_ball = random.randint(0, len(self.colors) - 1)
        self.turret_speed = 0.02
        self.left = False
        self.right = False
        self.ping = 0

        self.start_time = time.time()
        self.complete_time = None

        self.score = 0
        self.hp = 3
        self.finished = False

        self.more_to_collapse = -1

    @staticmethod
    def from_string_array(array: list):
        ellipse = Ellipse(*map(int, array[0].split()))
        balls = list(map(int, array[1].split))
        return Level(ellipse, balls)

    def go_next_state(self):
        if self.finished or self.hp <= 0:
            return
        if len(self.balls) == 0 and len(self.next_balls) == 0:
            self.finished = True
            self.complete_time = time.time() - self.start_time
        if self.left:
            self.turn_turret(-self.turret_speed)
        elif self.right:
            self.turn_turret(self.turret_speed)
        self.move_balls_next_state(self.speed)
        self.move_shots()
        self.collapse()
        self.new_ball()
        self.ping = max(self.ping - 1, 0)

    def move_balls_next_state(self, dist):
        i = len(self.balls) - 1
        distance = dist
        while i >= 0:
            self.move_ball(i, distance)
            if i > 0:
                distance = 2 * self.radius - mathExt.get_distance(
                    self.balls[i].point,
                    self.balls[i - 1].point
                )
            i -= 1

    def move_balls_process_hit(self, index, dist):
        i = index - 1
        distance = dist
        while i >= 0 and distance > 1e-6:
            self.move_ball(i, distance)
            if i > 0:
                distance = 2 * self.radius - mathExt.get_distance(
                    self.balls[i].point,
                    self.balls[i - 1].point
                )
            i -= 1

    def move_balls_collapse(self, index):
        point = self.balls[index].point
        for i in range(index - 1, -1, -1):
            self.balls[i].point = \
                self.ellipse.next_point(point, 2 * self.radius)
            point = self.balls[i].point
        self.more_to_collapse = -1

    def move_ball(self, index, dist):
        ball = self.balls[index]
        next_point = self.ellipse.next_point(ball.point, dist)
        if next_point is None:
            # self.balls.pop(index)
            return False
        elif self.ellipse.check_point_finished(next_point, self.radius):
            self.hp -= 1
            self.balls.pop(index)
            return False
        else:
            ball.point = next_point
            return True

    def move_shots(self):
        i = 0
        while i < len(self.shots):
            shot = self.shots[i]
            condition = False
            if shot.is_intersection(self.ellipse):
                condition = self.process_hit(self.shots[i])
            if shot.x > self.ellipse.width + self.radius or shot.y > \
                    self.ellipse.height + self.radius:
                condition = True
            if condition:
                self.shots.pop(i)
            else:
                shot.update()
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
        self.shots.append(
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

    def process_hit(self, shot):
        cond = False
        intersection = self.ellipse.get_coordinates(shot.angle, self.turret)
        angle = mathExt.get_angle(
            self.ellipse.get_coordinates(shot.angle, self.turret))
        ball_place = self.find_position(intersection[0])
        ball = None

        if ball_place < len(self.balls):
            distance = 2 * self.radius - mathExt.get_distance(
                self.ellipse.get_coordinates(angle),
                self.balls[ball_place].point
            )
            if distance > -1e-6:
                point = self.ellipse.next_point(
                    self.ellipse.get_coordinates(angle),
                    distance
                )
                ball = Ball(point, shot.color)
                angle = mathExt.get_angle(point)
                cond = True
        if ball_place > 0:
            distance = 2 * self.radius - mathExt.get_distance(
                self.ellipse.get_coordinates(angle),
                self.balls[ball_place - 1].point
            )
            if distance > -1e-6:
                self.move_balls_process_hit(ball_place, distance)
                ball = Ball(self.ellipse.get_coordinates(angle),
                            shot.color)
                cond = True

        if not cond:
            return False
        if not ball:
            raise ValueError
        ball.collapsing = True

        if ball_place == len(self.balls):
            self.balls.append(ball)
        else:
            self.balls.insert(ball_place, ball)
        return True

    def find_position(self, x):
        ball_place = mathExt. \
            int_bin_search(0,
                           len(self.balls),
                           lambda index: self.balls[index].point[0],
                           x)
        return ball_place

    def collapse(self):
        if len(self.balls) == 0:
            return
        if self.more_to_collapse != -1:
            self.move_balls_collapse(self.more_to_collapse)
        start = 0
        length = 1
        cond = self.balls[0].collapsing
        color = self.balls[0].color
        for i in range(1, len(self.balls)):
            if self.balls[i].color != color:
                if length >= 3 and cond:
                    self.remove_collapsing(length, start)
                    return
                else:
                    start = i
                    length = 1
                    color = self.balls[i].color
                    cond = self.balls[i].collapsing
            else:
                cond = cond or self.balls[i].collapsing
                length += 1
        if length >= 3 and cond:
            self.remove_collapsing(length, start)

    def remove_collapsing(self, length, start):
        self.score += 3 ** (length - 2)
        if start > 0:
            self.balls[start - 1].collapsing = True
            self.more_to_collapse = start - 1
        if start + length - 1 < len(self.balls):
            self.balls[start + length - 1].collapsing = True
        for j in range(length):
            self.balls.pop(start)
