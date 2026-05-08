import matplotlib.pyplot as plt
from math import sqrt

def find_ref_point(points):
    return min(points, key=lambda p: (p[1], p[0]))


def order_function(ref_point, point):
    if point == ref_point:
        return (float("-inf"),) * 2
    x, y = point
    a, b = ref_point
    distance = sqrt((x - a) ** 2 + (y - b) ** 2)
    return (-(x - a) / distance, distance)


def order_points(points):
    local_ref = find_ref_point(points)
    return sorted(points, key=lambda point: order_function(local_ref, point))


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
    # return stack[:-1]
    return stack

def plot_voronoi(points):
    ref_point = find_ref_point(points)
    ordered = order_points(points)
    scanned = scan(ordered)
    fig, ax = plt.subplots()
    ax.plot([p[0] for p in scanned], [p[1] for p in scanned])
    plt.show()

# def test(points, expected):
#     ref_point = find_ref_point(points)
#     ordered = order_points(points)
#     scanned = scan(ordered)

#     print(f'points: {points}')
#     print(f'ref_point: {ref_point}')
#     print(f'ordered: {ordered}')
#     print(f'scanned: {scanned}')
#     print(f'expected: {expected}')
#     print("PASSED" if expected == scanned else "FAILED")
#     print("\n")


# case 1
points = [[4, 3], [-2, -1], [9, 7], [2, 7]]
expected = [[-2, -1], [4, 3], [9, 7], [2, 7]]
# test(points, expected)

# case 2
points = [[4, 5], [0, 0], [9, 7], [2, 7]]
expected = [[0, 0], [9, 7], [2, 7]]
# test(points, expected)


# PLOTTING
plot_voronoi(points)
