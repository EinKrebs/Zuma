import math


def sign(number):
    if abs(number) < 1e-6:
        return 0
    if number > 0:
        return 1
    return -1


def get_angle(point):
    return math.atan2(point[1], point[0])


def get_biased_angle(first, second):
    return math.atan2(first[1] - second[1], first[0] - second[0])


def get_distance(point1, point2):
    return math.sqrt(
        (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def bin_search(start, finish, param, value):  # function growth
    left = start
    right = finish
    for i in range(100):
        mid = (left + right) / 2
        mid_value = param(mid)
        if mid_value < value:
            left = mid
        else:
            right = mid
    return left


def int_bin_search(start, finish, param, value):  # function growth
    left = start
    right = finish
    while right - left > 1:
        mid = (left + right) // 2
        mid_value = param(mid)
        if mid_value < value:
            left = mid
        else:
            right = mid
    return left if param(left) >= value else right


def tern_search(start, finish, param):  # function looks like -x^2
    left = start
    right = finish
    for i in range(100):
        mid_left = (9 * left + 8 * right) / 17
        mid_right = (8 * left + 9 * right) / 17
        if param(mid_left) <= param(mid_right):
            left = mid_left
        else:
            right = mid_right
    return left


def solve_square_poly(a, b, c):
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return None, None
    return ((-b - math.sqrt(discriminant)) / (2 * a),
            (-b + math.sqrt(discriminant)) / (2 * a))


def translate_point(point, width, height):
    return [width // 2 - point[0], height - point[1]]


def normalise_angle(angle):
    if angle < -math.pi / 2:
        angle += 2 * math.pi
    if angle > 3 * math.pi / 2:
        angle -= 2 * math.pi
    return angle
