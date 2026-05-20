from __future__ import annotations
from math import sqrt
from dataclasses import dataclass

"""
assumptions:
- general (no 3 pts on line, )
"""


@dataclass(frozen=True)
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

    def __lt__(self, other: Point):
        if self.x < other.x:
            return True
        if self.x > other.x:
            return False
        return self.y < other.y


# note: i define eq and hash below, but @dataclass(frozen=True) is same.
# and you can define a __post_init__
class Edge:
    def __init__(self, p: Point, q: Point):
        self.points = tuple(sorted((p, q)))

    # for debug only
    def __repr__(self):
        return f"Edge({self.points[0]}, {self.points[1]})"

    def __eq__(self, other):
        return isinstance(other, Edge) and self.points == other.points

    def __hash__(self):
        return hash(self.points)


class PointCloud:
    def __init__(self, points: list[Point]):
        # points sorted by cos relative to bottommost point
        self.points = self.sort(points)
        # points on convex hull, cyclic from bottommost point.
        self.convex_hull = self.get_convex_hull()

    def sort(self, points):
        def cos_comp(ref_p: Point, p: Point):
            if p == None:
                return float("-inf")
            if p == ref_p:
                return (float("-inf"),) * 2
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = (
            min(points, key=lambda p: (p.y, p.x))
            if None not in points
            else float("-inf")
        )
        return sorted(points, key=lambda p: cos_comp(local_ref, p))

    def get_convex_hull(self):
        if None in self.points:
            return self.points
        stack = []
        for point in self.points + [self.points[0]]:
            while len(stack) > 1 and not Point.is_left(
                stack[-2], stack[-1], point
            ):
                stack.pop()
            stack.append(point)
        return stack[:-1]
        # return stack

    def get_hull_edges(self):
        return [
            Edge(p, q)
            for p, q in zip(
                self.convex_hull, self.convex_hull[1:] + [self.convex_hull[0]]
            )
        ]


class Triangle(PointCloud):
    def __init__(self, p: Point, q: Point, r: Point):
        super().__init__([p, q, r])

    def contains(self, x: Point):
        if None in self.points:
            return True
        last_point_added = self.points + [self.points[0]]
        for point, next_point in zip(last_point_added, last_point_added[1:]):
            if not Point.is_left(point, next_point, x):
                return False
        return True

    def get_opp_point(self, x: Point, y: Point):
        if x not in self.points or y not in self.points:
            raise ValueError("points must be vertices of triangle")
        return [z for z in self.points if z not in [x, y]][0]

    def get_opp_edge(self, p: Point):
        if p not in self.points:
            raise ValueError("point must be vertex of triangle")
        return Edge(*[z for z in self.points if z != p])


if __name__ == "__main__":
    pass
    # triangle_membership_demo()
    # convex_hull_demo()

    # _pts = [[1, 1], [2, 4], [3, 3]]
    # pts = [Point(x, y) for x, y in _pts]
    # cloud = PointCloud(pts)
    # triangle = Triangle(*pts)
    # # print(triangle.points)
    # print(triangle.contains(Point(2, 3)))
    # print(triangle.contains(Point(2, 5)))
    # # print(cloud.points)
