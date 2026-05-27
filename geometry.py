from __future__ import annotations
from math import sqrt
from dataclasses import dataclass, field
import random

"""
assumptions:
- general (no 3 pts on line, )
"""


def looped_pairs(points: list[Point]):
    if len(points) < 3:
        return zip(points, points[1:])
    loop = points + [points[0]]
    return zip(loop, loop[1:])


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
            return Point(p.y, -p.x)
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
        self.points = tuple(sorted((p, q)))
        self.p = self.points[0]
        self.q = self.points[1]
        self.is_finite = all(e.is_finite for e in self.points)
        self.totally_infinite = all(not e.is_finite for e in self.points)

    @staticmethod
    def cross(e: Edge, f: Edge):
        if e.totally_infinite or f.totally_infinite:
            raise ValueError("totally infinite edges do not cross anything")
        p = f.p
        q = f.q
        if not p.is_finite and q.is_finite:
            p, q = q, p
        direction = Point.sub(p, q)
        direction.is_finite = False
        tri = Triangle(e.p, e.q, direction)
        return tri.contains(p) != tri.contains(q)

    def plot(self, ax, color):
        if self.is_finite:
            ax.plot(
                [p.x for p in self.points],
                [p.y for p in self.points],
                c=color,
            )
        elif self.p.is_finite or self.q.is_finite:
            ax.relim()
            ax.autoscale_view()
            x_min, x_max = ax.get_xlim()
            y_min, y_max = ax.get_ylim()
            z = self.p if self.p.is_finite else self.q
            w = self.q if z == self.p else self.p
            jump = 1
            path_x = z.x + jump * w.x
            path_y = z.y + jump * w.y
            while x_min <= path_x <= x_max and y_min <= path_y <= y_max:
                jump += 1
                path_x = z.x + (jump + 1) * w.x
                path_y = z.y + (jump + 1) * w.y
            path_x -= w.x
            path_y -= w.y

            ax.plot(
                [z.x, path_x],
                [z.y, path_y],
                linestyle="dotted",
                color=color,
                linewidth=1,
            )

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


class Triangle:
    def __init__(self, p: Point, q: Point, r: Point):
        points = [p, q, r]
        finite_points = [x for x in points if x.is_finite]
        infinite_points = [x for x in points if not x.is_finite]
        sorting_reps: dict[Point, Point] = {x: x for x in points}
        for a in infinite_points:
            if finite_points:
                b = max(finite_points, key=lambda z: Point.dot(z, a))
                sorting_reps[a] = Point(a.x + b.x, a.y + b.y)
        self.points = self._sort(sorting_reps)
        self.edges = [Edge(x, y) for x, y in looped_pairs(self.points)]
        self.is_finite = all(p.is_finite for p in self.points)

    def plot(self, ax):
        colors = ["b", "g", "r", "c", "m"]
        color = random.choice(colors)
        for e in self.edges:
            e.plot(ax, color)

    def _sort(self, rep_pairs):
        def cos_comp(ref_p: Point, p: Point):
            if p == ref_p:
                return (float("-inf"),) * 2
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = min(rep_pairs.values(), key=lambda p: (p.y, p.x))
        return sorted(
            rep_pairs.keys(), key=lambda p: cos_comp(local_ref, rep_pairs[p])
        )

    def contains(self, x: Point):
        if not x.is_finite:
            return False
        for point, next_point in looped_pairs(self.points):
            if not point.is_finite and not next_point.is_finite:
                continue
            if not Point.is_left(point, next_point, x):
                return False
        return True

    def get_opp_point(self, e: Edge):
        if e not in self.edges:
            raise ValueError("edge must be finite side of triangle")
        for p in self.points:
            if p not in e.points:
                return p
        print("get opp point not found: no good")
        return None

    def get_opp_edge(self, p: Point):
        if p not in self.points:
            raise ValueError(
                f"point must be vertex of triangle \n trying to get edge opp {p} for triangle with points (self.points)"
            )
        for e in self.edges:
            if p not in e.points:
                return e
        print("get opp edge not found: no good")
        return None

    def triple(self):
        return Triangle(*[Point(3 * p.x, 3 * p.y) for p in self.points])


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
