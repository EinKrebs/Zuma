import math
import math_extensions as mathExt
from domain.ellipse import Ellipse
from domain.ball import Ball


class Sequence:
    def __init__(self, ball: Ball, ellipse: Ellipse, radius: int):
        self.balls = [ball]
        self.ellipse = ellipse
        self.radius = radius
        self._left = None
        self._right = None
        self.more_to_collapse = -1

    @property
    def left(self):
        if self._left is None:
            self._left = self.get_left()
        return self._left

    @property
    def right(self):
        if self._right is None:
            self._right = self.get_right()
        return self._right

    def __len__(self):
        return len(self.balls)

    def get_right(self):
        if len(self.balls) == 0:
            return self.ellipse.start_point
        return self.ellipse.next_point(
            self.balls[0].point,
            2 * self.radius,
            finish=math.pi + 1
        )

    def get_left(self):
        if len(self.balls) == 0:
            return self.ellipse.start_point
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
                return
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
            self._right = None
            self._left = None
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
        self._left = None

    def get_penetrated(self, point):
        position = self.find_position(point[0])
        self.balls[max(0, position - 1)].exploding = True
        self.balls[min(position, len(self.balls) - 1)].exploding = True

    def insert_ball(self, point, color):  # point lies between left & right
        if not(self.right[0] < point[0] < self.left[0]
               and len(self.balls) > 0):
            return 0
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
        self._right = None

    def collapse(self, speed):
        if len(self.balls) == 0:
            return 0, (0, 0, 0), 0
        if self.more_to_collapse != -1:
            self.move_balls_collapse(self.more_to_collapse)
        start = 0
        length = 1
        cond = self.balls[0].collapsing
        exploding = self.balls[0].exploding
        color = self.balls[0].color
        for i in range(1, len(self.balls)):
            if self.balls[i].color != color:
                if (length >= 3 and cond) or exploding:
                    score = self.remove_collapsing(length, start, speed)
                    return length, color, score
                else:
                    start = i
                    length = 1
                    color = self.balls[i].color
                    cond = self.balls[i].collapsing
                    exploding = self.balls[i].exploding
            else:
                cond = cond or self.balls[i].collapsing
                exploding = exploding or self.balls[i].exploding
                length += 1
        if (length >= 3 and cond) or exploding:
            score = self.remove_collapsing(length, start, speed)
            return length, color, score
        for ball in self.balls:
            ball.collapsing = False
        return 0, (0, 0, 0), 0

    def remove_collapsing(self, length, start, speed):
        score = 3 ** (length - 2) * math.sqrt(speed)
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
