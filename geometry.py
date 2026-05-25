from __future__ import annotations
from math import sqrt
from dataclasses import dataclass, field

"""
assumptions:
- general (no 3 pts on line, )
"""


@dataclass(frozen=True)
class Point:
    x: int
    y: int
    is_finite: bool = True

    @staticmethod
    def dot(p: Point, q: Point):
        return p.x * q.x + p.y * q.y

    @staticmethod
    def sub(p: Point, q: Point):
        if not p.is_finite:
            return Point(p.x, p.y)
        if not q.is_finite:
            return Point(-q.x, -q.y)
        return Point(p.x - q.x, p.y - q.y)

    @staticmethod
    def orthogonal(p: Point, q: Point):
        if not p.is_finite and not q.is_finite:
            return Point(0, 0)
        if not p.is_finite:
            return Point(-p.y, p.x)
        if not q.is_finite:
            return Point(-q.y, q.x)
        direction = Point.sub(q, p)
        return Point(-direction.y, direction.x)

    @staticmethod
    def is_left(p: Point, q: Point, x: Point):
        base_orthogonal = Point.orthogonal(p, q)
        finite_base = q if q.is_finite else p
        new_direction = Point.sub(x, finite_base)
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
        if not p.is_finite or not q.is_finite:
            raise ValueError("Edge must be between two finite points")
        self.points = tuple(sorted((p, q)))
        self.p = self.points[0]
        self.q = self.points[1]

    # for debug only
    def __repr__(self):
        return f"Edge({self.points[0]}, {self.points[1]})"

    def __eq__(self, other):
        return isinstance(other, Edge) and self.points == other.points

    def __hash__(self):
        # print(
        #     f"hashing the following edge {self.p.x, self.p.y, self.p.z}, {self.q.x, self.q.y, self.q.z}"
        # )
        return hash(self.points)


class PointCloud:
    def __init__(self, points: list[Point]):
        self.infinite_points = [p for p in points if not p.is_finite]
        self.finite_points = [p for p in points if p.is_finite]
        self.create_dummies()
        # points sorted by cos relative to bottommost point
        self.points = self.sort(points)
        # points on convex hull, cyclic from bottommost point.
        self.convex_hull = self.get_convex_hull()

    def create_dummies(self):
        for p in self.infinite_points:
            if self.finite_points:
                q = max(self.finite_points, key=lambda x: Point.dot(x, p))
                p.establish_dummy(q)

    def sort(self, points):
        def cos_comp(ref_p: Point, p: Point):
            if p == ref_p:
                return (float("-inf"),) * 2
            p = p.dummy if p.z == 1 else p
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = min(points, key=lambda p: (p.y, p.x))
        return sorted(points, key=lambda p: cos_comp(local_ref, p))

    def get_convex_hull(self):
        stack = []
        for point in self.points + [self.points[0]]:
            if point.z == 1:
                continue
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
        # note edges will not repect counterclockwise locally
        self.edges = [Edge(p, q), Edge(p, r), Edge(q, r)]

    def contains(self, x: Point):
        last_point_added = self.points + [self.points[0]]
        for point, next_point in zip(last_point_added, last_point_added[1:]):
            if point.z == 1 and next_point.z == 1:
                continue
            if not Point.is_left(point, next_point, x):
                return False
        return True

    def get_opp_point(self, e: Edge):
        raw_triangle_points = [p.get_raw_point() for p in self.points]
        if e.p not in raw_triangle_points or e.q not in raw_triangle_points:
            raise ValueError("points must be vertices of triangle")
        for p in self.points:
            if p.get_raw_point() not in e.points:
                return p
        print("get opp point not found: no good")
        return None

    def get_opp_edge(self, p: Point):
        print("opp edge called")
        print(f"triangle points are {self.points}")
        print(f"point isw {p}")
        if p not in self.points:
            raise ValueError("point must be vertex of triangle")
        raw_p = p.get_raw_point()
        for e in self.edges:
            if raw_p not in e.points:
                return e
        print("get opp edge not found: no good")
        return None


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
