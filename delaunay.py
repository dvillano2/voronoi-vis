"""
assumptions:
- general (no 3 pts on line, )




"""
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

def point_add(p: Point, q: Point):
    return Point(p.x + q.x, p.y + q.y)

def point_sub(p: Point, q: Point):
    return Point(p.x - q.x, p.y - q.y)

def point_dot(p: Point, q: Point):
    return p.x * q.x + p.y * q.y

class Segment:
    def __init__(self, p: Point, q: Point):
        pts = sorted([p, q], key=lambda pp: (pp.y, pp.x))
        self.base = pts[0]
        self.far = pts[1]
        self.direction = point_sub(self.far, self.base)
        self.orthogonal = Point(-self.direction.y, self.direction.x)

    def is_left(self, p: Point):
        return point_dot(p, self.orthogonal) > point_dot(self.base, self.orthogonal)

class Triangle:
    def __init__(self):
        pass


def is_delaunay(p: Point, t: Triangle):
    pass



if __name__ == "__main__":
    _pts = [[1, 2], [5, 3]]
    pts = [Point(x, y) for x,y in _pts]
    seg = Segment(pts[0], pts[1])
    seg = Segment(pts[1], pts[0])
    print(seg.is_left(Point(0, 10)))
    print(seg.is_left(Point(3, 3)))

