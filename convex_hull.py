"""
points = [[4, 3], [-2, -1], [9, 7], [2, 7]]




"""

from math import sqrt


def find_ref_point(points):
    return min(points, key=lambda p: (p[1], p[0]))


def order_fuction(ref_point, point):
    if point == ref_point:
        return (float("-inf"),) * 2
    x, y = point
    a, b = ref_point
    distance = sqrt((x - a) ** 2 + (y - b) ** 2)
    return (-x / distance, distance)


def order_points(points):
    local_ref = find_ref_point(points)
    return sorted(points, key=lambda point: order_fuction(local_ref, point))


def left_turn(point0, point1, point2):
    a, b = point0
    c, d = point1
    x, y = point2
    orthonal_ref = (b - d, c - a)
    new_line = (x - c, y - d)
    dot_product = sum(
        o_coord * new_coord
        for o_coord, new_coord in zip(orthonal_ref, new_line)
    )
    return dot_product >= 0


def scan(ordered_points):
    stack = []
    for point in ordered_points + [ordered_points[0]]:
        while len(stack) > 1 and not left_turn(stack[-2], stack[-1], point):
            stack.pop()
        stack.append(point)
    return stack[:-1]


points = [[4, 3], [0, 0], [9, 7], [2, 7]]
print(points)
ref_point = find_ref_point(points)
print(ref_point)
ordered = order_points(points)
print(ordered)
scaned = scan(ordered)
print(scaned)
