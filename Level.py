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
                 balls: list,
                 radius=20,
                 speed=1,
                 shot_speed=150,
                 turret=(0, 90)):
        self.colors = [(0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255)]
        self.ellipse = ellipse
        self.next_balls = balls
        self.radius = radius
        self.speed = speed
        self.shot_speed = shot_speed
        self.turret = turret

        self.balls = []
        self.shots = []
        self.turret_angle = math.pi / 2
        self.color_count = self.count_colors()
        self.remove_colors()
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

        self.add_balls = True

    @staticmethod
    def from_string_array(array: list):
        ellipse = Ellipse.from_string(array[0])
        balls = list(map(int, array[1].split()))
        return Level(ellipse, balls)

    def count_colors(self):
        count = [0] * len(self.colors)
        for color in self.next_balls:
            count[color] += 1
        return count

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
        self.remove_colors()
        if self.turret_ball >= len(self.colors):
            self.turret_ball -= 1
        if self.add_balls:
            self.new_ball()
        self.ping = max(self.ping - 1, 0)

    def move_shots(self):
        i = 0
        while i < len(self.shots):
            shot = self.shots[i]
            condition = False
            if shot.is_intersection(self.ellipse):
                condition = self.process_hit(self.shots[i])
            if (shot.x > self.ellipse.width + self.radius
                    or shot.y > self.ellipse.height + self.radius):
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
        self.color_count[self.turret_ball] += 1
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
                if not point:
                    return
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

    def get_color_number(self, needed_color):
        for counter, value in enumerate(self.colors):
            if value == needed_color:
                return counter

    def remove_colors(self):
        i = 0
        while i < len(self.colors):
            if self.color_count[i] == 0:
                self.color_count.pop(i)
                self.colors.pop(i)
            else:
                i += 1

    def find_position(self, x):
        ball_place = mathExt.int_bin_search(
            0,
            len(self.balls),
            lambda index: self.balls[index].point[0],
            x)
        return ball_place
