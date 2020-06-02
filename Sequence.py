import math
import MathExtentions as mathExt
from Ellipse import Ellipse
from Ball import Ball


class Sequence:
    def __init__(self, ball: Ball, ellipse: Ellipse, radius: int):
        self.balls = [ball]
        self.ellipse = ellipse
        self.radius = radius
        self.left = self.get_left()
        self.right = self.get_right()
        self.more_to_collapse = -1

    def __len__(self):
        return len(self.balls)

    def get_right(self):
        return self.ellipse.next_point(
            self.balls[0].point,
            2 * self.radius,
            finish=math.pi + 1
        )

    def get_left(self):
        return self.ellipse.previous_point(
            self.balls[-1].point,
            2 * self.radius,
            start=-1
        )

    def move(self, distance, index=None):
        if len(self.balls) == 0:
            return 0
        count = 0
        if index is None:
            index = len(self.balls) - 1
        while index >= 0:
            try:
                ball = self.balls[index]
            except IndexError:
                print('fuck!')
            new_point = self.ellipse.next_point(ball.point, distance)
            if new_point is None:
                self.balls.pop(index)
                count += 1
            else:
                ball.point = new_point
                if index > 0:
                    distance = max(
                        2 * self.radius - mathExt.get_distance(
                            self.balls[index].point,
                            self.balls[index - 1].point),
                        0)
            index -= 1

        if len(self.balls) > 0:
            self.right = self.get_right()
            self.left = self.get_left()
        return count

    def add_ball(self, color):
        if len(self.balls) == 0:
            point = self.ellipse.next_point(self.ellipse.start_point,
                                            self.radius)
        else:
            if mathExt.get_angle(self.left) < self.ellipse.start:
                raise ValueError
            point = self.left
        self.balls.append(Ball(point, color))
        self.left = self.get_left()

    def insert_ball(self, point, color):  # point lies between left & right
        count = 0
        position = self.find_position(point[0])
        ball = None

        if position < len(self.balls):
            distance = 2 * self.radius - mathExt.get_distance(
                point,
                self.balls[position].point
            )
            if distance > -1e-6:
                point = self.ellipse.next_point(point, distance)
                if not point:
                    count += 1
                    return count
                ball = Ball(point, color)
        if position > 0:
            distance = 2 * self.radius - mathExt.get_distance(
                point,
                self.balls[position - 1].point
            )
            if distance > -1e-6:
                count = self.move(distance, position - 1)
                position -= count
                ball = Ball(point, color)

        ball.collapsing = True

        if position == len(self.balls):
            self.add_ball(color)
        else:
            self.balls.insert(position, ball)
        return count

    def find_position(self, x):
        ball_place = mathExt.int_bin_search(
            0,
            len(self.balls),
            lambda index: self.balls[index].point[0],
            x)
        return ball_place

    def move_balls_collapse(self, index):
        point = self.balls[index].point
        for i in range(index - 1, -1, -1):
            self.balls[i].point = self.ellipse.next_point(
                point,
                2 * self.radius)
            point = self.balls[i].point
        self.more_to_collapse = -1
        self.right = self.get_right()

    def collapse(self):
        if len(self.balls) == 0:
            return 0, (0, 0, 0), 0
        if self.more_to_collapse != -1:
            self.move_balls_collapse(self.more_to_collapse)
        start = 0
        length = 1
        cond = self.balls[0].collapsing
        color = self.balls[0].color
        for i in range(1, len(self.balls)):
            if self.balls[i].color != color:
                if length >= 3 and cond:
                    score = self.remove_collapsing(length, start)
                    return length, color, score
                else:
                    start = i
                    length = 1
                    color = self.balls[i].color
                    cond = self.balls[i].collapsing
            else:
                cond = cond or self.balls[i].collapsing
                length += 1
        if length >= 3 and cond:
            score = self.remove_collapsing(length, start)
            return length, color, score
        return 0, (0, 0, 0), 0

    def remove_collapsing(self, length, start):
        score = 3 ** (length - 2)
        if (
                start > 0
                and start + length < len(self.balls)
                and self.balls[start - 1].color
                == self.balls[start + length].color
        ):
            self.balls[start + length].collapsing = True
            self.balls[start - 1].collapsing = True
            self.more_to_collapse = start - 1
        for j in range(length):
            self.balls.pop(start)
        return score
