from delaunay import Point


# not used now but good from looking back
class Segment:
    def __init__(self, p: Point, q: Point):
        pts = sorted([p, q], key=lambda pp: (pp.y, pp.x))
        self.base = pts[0]
        self.far = pts[1]
        self.direction = Point.sub(self.far, self.base)
        self.orthogonal = Point(-self.direction.y, self.direction.x)

    def is_left(self, p: Point):
        return Point.dot(p, self.orthogonal) > Point.dot(
            self.base, self.orthogonal
        )
