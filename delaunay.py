from __future__ import annotations
import matplotlib.pyplot as plt
import random
from math import sqrt
from dataclasses import dataclass

"""
assumptions:
- general (no 3 pts on line, )
"""


@dataclass
class Point:
    x: int
    y: int

    @staticmethod
    def dot(p: Point, q: Point):
        return p.x * q.x + p.y * q.y

    @staticmethod
    def sub(p: Point, q: Point):
        return Point(p.x - q.x, p.y - q.y)

    @staticmethod
    def orthogonal(p: Point, q: Point):
        direction = Point.sub(q, p)
        return Point(-direction.y, direction.x)

    @staticmethod
    def is_left(p: Point, q: Point, x: Point):
        base_orthogonal = Point.orthogonal(p, q)
        new_direction = Point.sub(x, q)
        return Point.dot(base_orthogonal, new_direction) > 0


class PointCloud:
    def __init__(self, points: list[Point]):
        self.points = self.sort(points)
        self.convex_hull = self.get_convex_hull()

    def sort(self, points):
        def cos_comp(ref_p: Point, p: Point):
            if p == ref_p:
                return (float("-inf"),) * 2
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = min(points, key=lambda p: (p.y, p.x))
        return sorted(points, key=lambda p: cos_comp(local_ref, p))

    def get_convex_hull(self):
        stack = []
        for point in self.points + [self.points[0]]:
            while len(stack) > 1 and not Point.is_left(
                stack[-2], stack[-1], point
            ):
                stack.pop()
            stack.append(point)
        # return stack[:-1]
        return stack


class Triangle(PointCloud):
    def __init__(self, p: Point, q: Point, r: Point):
        super().__init__([p, q, r])

    def inside(self, x: Point):
        last_point_added = self.points + [self.points[0]]
        for point, next_point in zip(last_point_added, last_point_added[1:]):
            if not Point.is_left(point, next_point, x):
                return False
        return True


def triangle_membership_demo():
    fig, ax = plt.subplots(4, 4)
    for i in range(4):
        for j in range(4):
            num_points = 400
            points = []
            for _ in range(num_points):
                new_x = random.randint(-100, 100)
                new_y = random.randint(-100, 100)
                points.append(Point(new_x, new_y))
            triangle_points = points[:3] + [points[0]]
            points = points[3:]

            t = Triangle(*triangle_points[:-1])
            ax[i, j].plot(
                [p.x for p in triangle_points], [p.y for p in triangle_points]
            )
            ax[i, j].scatter(
                [p.x for p in points if t.inside(p)],
                [p.y for p in points if t.inside(p)],
                c="r",
            )
            ax[i, j].scatter(
                [p.x for p in points if not t.inside(p)],
                [p.y for p in points if not t.inside(p)],
                c="b",
            )

    plt.tight_layout()
    plt.show()


def convex_hull_demo():
    fig, ax = plt.subplots(4, 4)
    for i in range(4):
        for j in range(4):
            num_points = random.randint(5, 60)
            points = []
            for _ in range(num_points):
                new_x = random.randint(-100, 100)
                new_y = random.randint(-100, 100)
                points.append(Point(new_x, new_y))
            point_cloud = PointCloud(points)
            # ordered = order_points(points)
            # scanned = scan(ordered)
            ax[i, j].plot(
                [p.x for p in point_cloud.convex_hull],
                [p.y for p in point_cloud.convex_hull],
            )
            ax[i, j].plot(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )
            ax[i, j].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # triangle_membership_demo()
    convex_hull_demo()

    # _pts = [[1, 1], [2, 4], [3, 3]]
    # pts = [Point(x, y) for x, y in _pts]
    # cloud = PointCloud(pts)
    # triangle = Triangle(*pts)
    # # print(triangle.points)
    # print(triangle.inside(Point(2, 3)))
    # print(triangle.inside(Point(2, 5)))
    # # print(cloud.points)
