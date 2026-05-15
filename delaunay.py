from math import sqrt
from convex_hull import ordered_points

"""
assumptions:
- general (no 3 pts on line, )




"""

from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


class PointCloud:
    def __init__(self, points: list[Point]):
        self.points = points
        self.points = self.sort()

    def sort(self):
        def cos_comp(ref_p, p):
            if p == ref_p:
                return (float("-inf"),) * 2
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = min(self.points, key=lambda p: (p.y, p.x))
        return sorted(self.points, key=lambda p: cos_comp(local_ref, p))


class Triangle(PointCloud):
    def __init__(self, p: Point, q: Point, r: Point):
        super().__init__([p, q, r])

    def inside(self, x: Point):
        for seg in self.segments:
            if not seg.is_left(x):
                return False
        return True


def point_add(p: Point, q: Point):
    return Point(p.x + q.x, p.y + q.y)


def point_sub(p: Point, q: Point):
    return Point(p.x - q.x, p.y - q.y)


def point_dot(p: Point, q: Point):
    return p.x * q.x + p.y * q.y


# class Segment:
#    def __init__(self, p: Point, q: Point):
#        pts = sorted([p, q], key=lambda pp: (pp.y, pp.x))
#        self.base = pts[0]
#        self.far = pts[1]
#        self.direction = point_sub(self.far, self.base)
#        self.orthogonal = Point(-self.direction.y, self.direction.x)
#
#    def is_left(self, p: Point):
#        return point_dot(p, self.orthogonal) > point_dot(
#            self.base, self.orthogonal
#        )


def is_delaunay(p: Point, t: Triangle):
    pass


if __name__ == "__main__":
    _pts = [[1, 2], [5, 3]]
    pts = [Point(x, y) for x, y in _pts]
    seg = Segment(pts[0], pts[1])
    seg = Segment(pts[1], pts[0])
    print(seg.is_left(Point(0, 10)))
    print(seg.is_left(Point(3, 3)))
