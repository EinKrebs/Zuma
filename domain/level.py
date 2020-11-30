import math
import random
import time
import typing

from domain.ellipse import Ellipse
from domain.shot import Shot
from domain.ball import Ball
from domain.sequence import Sequence
import math_extensions as mathExt


class Level:
    def __init__(self,
                 ellipse: Ellipse,
                 sequences: typing.List[Sequence],
                 times: typing.List[float],
                 radius=20,
                 speed=1,
                 shot_speed=150,
                 turret=(0, 90)):
        self.colors = [(0, 0, 0), (0, 255, 0), (255, 0, 0), (0, 0, 255)]
        self.current_colors = []
        self.ellipse = ellipse

        self.next_sequences = sequences[::-1]
        self.current_sequence_next = None
        self.sequences = []
        self.current_time_offset = None
        self.times = times[::-1]
        self.radius = radius
        self.speed = speed
        self.shot_speed = shot_speed
        self.turret = turret
        self.current_sequence_started = False

        self.shots = []
        self.turret_angle = math.pi / 2
        self.color_count = []
        self.turret_ball = -1
        self.turret_speed = 0.02
        self.left = False
        self.right = False
        self.ping = 0

        self.start_time = time.time()
        self.complete_time = None

        self.score = 0
        self.hp = 3
        self.finished = False

        self.timer = None
        self.std_speed = speed
        self.super_shot_count = 0

        self.more_to_collapse = -1

        self.add_balls = True

        self.pause_time = None

    @staticmethod
    def from_file(file: str):
        with open(file) as f:
            array = f.readlines()
        ellipse = Ellipse.from_string(array[0])
        times = []
        sequences = []
        for i in range(1, len(array)):
            line = list(map(int, array[i].split()))
            times.append(line[0])
            sequences.append(line[1:])
        return Level(ellipse, sequences, times)

    def pause(self):
        if self.pause_time is not None:
            return
        self.pause_time = time.time()

    def resume(self):
        if self.pause_time is None:
            raise ValueError("game is not paused")
        elapsed = time.time() - self.pause_time
        self.start_time += elapsed
        if self.timer is not None:
            self.timer += elapsed
        self.pause_time = None

    def start(self):
        self.start_time = time.time()

    def go_next_state(self):
        if self.finished or self.hp <= 0:
            return
        if (len(self.sequences) == 0
                and len(self.next_sequences) == 0
                and (self.current_sequence_next is None
                     or len(self.current_sequence_next) == 0)):
            self.finished = True
            self.complete_time = time.time() - self.start_time

        self.update_turret()
        self.update_sequences()
        self.move_balls_next_state(self.speed)
        self.move_shots()
        self.score += self.collapse()
        self.new_ball()
        if self.turret_ball == -1:
            self.turret_ball = random.randint(
                0,
                max(len(self.current_colors) - 1, 0)
            )
        while self.turret_ball >= len(self.current_colors):
            self.turret_ball -= 1
        self.ping = max(self.ping - 1, 0)

    def update_turret(self):
        if self.left:
            self.turn_turret(-self.turret_speed)
        elif self.right:
            self.turn_turret(self.turret_speed)

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
                self.remove_color(shot.color)
            if condition:
                self.shots.pop(i)
            else:
                shot.update()
                i += 1

    def process_hit(self, shot):
        cond = False
        intersection = self.ellipse.get_coordinates(shot.angle, self.turret)
        intersection_angle = mathExt.get_angle(intersection)
        for sequence in self.sequences:
            if (mathExt.get_angle(sequence.left) <= intersection_angle
                    <= mathExt.get_angle(sequence.right)):
                if shot.penetrate:
                    sequence.get_penetrated(intersection)
                else:
                    sequence.insert_ball(intersection, shot.color)
                cond = True
        return cond

    def collapse(self):
        score = 0
        for sequence in self.sequences:
            length, color, seq_score = sequence.collapse(self.speed)
            score += seq_score
            if length != 0:
                self.process_event(length)
                self.remove_color(color, count=length)
        return score

    def change_speed(self):
        if self.timer is None:
            return
        if time.time() - self.timer > 5:
            self.speed = self.std_speed

    def process_event(self, length):
        if random.randint(1, 50) <= length:
            if random.randint(1, 20) == 1:
                self.add_super_shots()
            else:
                if self.timer is not None:
                    return
                self.timer = time.time()
                event_type = random.randint(1, 40)
                if event_type == 1:
                    self.speed = self.std_speed * 0.25
                elif 2 <= event_type <= 5:
                    self.speed = self.std_speed * 0.5
                elif 6 <= event_type <= 20:
                    self.speed = self.std_speed * 0.75
                elif 21 <= event_type <= 35:
                    self.speed = self.std_speed * 1.25
                elif 36 <= event_type <= 39:
                    self.speed = self.std_speed * 1.5
                else:
                    self.speed = self.std_speed * 2

    def add_super_shots(self):
        a = random.randint(1, 100)
        if a == 100:
            self.super_shot_count += 3
        elif a % 10 == 0:
            self.super_shot_count += 2
        else:
            self.super_shot_count += 1

    def update_sequences(self):
        if ((self.current_sequence_next is None
                or len(self.current_sequence_next) == 0)
                and len(self.next_sequences) > 0):
            self.current_sequence_started = False
            self.current_sequence_next = self.next_sequences[-1][::-1]
            self.next_sequences.pop()
            self.current_time_offset = self.times[-1]
            self.times.pop()
        i = len(self.sequences) - 1
        while i >= 0:
            sequence = self.sequences[i]
            if (len(sequence) == 0
                    and (i < len(self.sequences) - 1
                         or len(self.current_sequence_next) == 0)):
                self.sequences.pop(i)
            i -= 1

    def move_balls_next_state(self, distance):
        for sequence in self.sequences:
            self.hp -= sequence.move(distance)

    def new_ball(self):
        if (not self.current_sequence_next
                or len(self.current_sequence_next) == 0):
            return
        if self.current_time_offset < self.get_current_time():
            if not self.current_sequence_started:
                ball = Ball(
                    self.ellipse.next_point(
                        self.ellipse.start_point,
                        self.radius
                    ),
                    self.colors[self.current_sequence_next[-1]]
                )
                sequence = Sequence(
                    ball,
                    self.ellipse,
                    self.radius
                )
                self.sequences.append(sequence)
                self.current_sequence_next.pop()
                self.current_sequence_started = True

                self.add_color(ball.color)
                return
            if (mathExt.get_angle(self.sequences[-1].left) >
                mathExt.get_angle(self.ellipse.next_point(
                    self.ellipse.start_point,
                    self.radius))
                    or len(self.sequences[-1].balls) == 0):
                color = self.colors[self.current_sequence_next[-1]]
                self.add_color(color)
                self.sequences[-1].add_ball(color)
                self.current_sequence_next.pop()
                return

    def get_current_time(self):
        return time.time() - self.start_time

    def shoot(self, penetrate: bool):
        if self.ping > 0:
            return
        if penetrate:
            if self.super_shot_count > 0:
                self.super_shot_count -= 1
            else:
                penetrate = False
        self.shots.append(
            Shot(self.turret[0], self.turret[1],
                 self.current_colors[self.turret_ball],
                 self.turret_angle,
                 self.shot_speed,
                 penetrate)
        )
        self.color_count[self.turret_ball] += 1
        self.ping = 20
        self.turret_ball = random.randint(0, len(self.current_colors) - 1)

    def turn_turret(self, angle):
        self.turret_angle += angle
        if self.turret_angle < 0:
            self.turret_angle = 0
        if self.turret_angle > math.pi:
            self.turret_angle = math.pi

    def add_color(self, color):
        if self.get_color_number(color) == -1:
            self.current_colors.append(color)
            self.color_count.append(0)
        self.color_count[self.get_color_number(color)] += 1

    def remove_color(self, color, count=1):
        index = self.get_color_number(color)
        if index == -1:
            raise ValueError
        for i in range(count):
            self.color_count[index] -= 1
        if self.color_count[index] == 0:
            self.color_count.pop(index)
            self.current_colors.pop(index)

    def get_color_number(self, needed_color):
        for counter, value in enumerate(self.current_colors):
            if value == needed_color:
                return counter
        return -1

    @property
    def balls(self):
        balls = []
        for sequence in self.sequences:
            balls += sequence.balls
        return balls
