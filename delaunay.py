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

def point_add(p: Point, q: Point):
    return Point(p.x + q.x, p.y + q.y)


def point_sub(p: Point, q: Point):
    return Point(p.x - q.x, p.y - q.y)


def point_dot(p: Point, q: Point):
    return p.x * q.x + p.y * q.y


class PointCloud:
    def __init__(self, points: list[Point]):
        # self.points = points
        self.points = self.sort(points)

    def sort(self, points):
        def cos_comp(ref_p: Point, p: Point):
            if p == ref_p:
                return (float("-inf"),) * 2
            distance = sqrt((p.x - ref_p.x) ** 2 + (p.y - ref_p.y) ** 2)
            return (-(p.x - ref_p.x) / distance, distance)

        local_ref = min(points, key=lambda p: (p.y, p.x))
        return sorted(points, key=lambda p: cos_comp(local_ref, p))


class Triangle(PointCloud):
    def __init__(self, p: Point, q: Point, r: Point):
        super().__init__([p, q, r])

    def inside(self, x: Point):
        last_point_added = self.points + [self.points[0]]
        for point, next_point in zip(last_point_added, last_point_added[1:]):
            direction = point_sub(next_point, point)
            orthogonal = Point(-direction.y, direction.x)
            if not point_dot(x, orthogonal) > point_dot(point, orthogonal):
                return False
        return True


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
            ax[i, j].plot([p.x for p in triangle_points], [p.y for p in triangle_points])
            ax[i, j].scatter([p.x for p in points if t.inside(p)], [p.y for p in points if t.inside(p)], c='r')
            ax[i, j].scatter([p.x for p in points if not t.inside(p)], [p.y for p in points if not t.inside(p)], c='b')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    triangle_membership_demo()
    # _pts = [[1, 1], [2, 4], [3, 3]]
    # pts = [Point(x, y) for x, y in _pts]
    # cloud = PointCloud(pts)
    # triangle = Triangle(*pts)
    # # print(triangle.points)
    # print(triangle.inside(Point(2, 3)))
    # print(triangle.inside(Point(2, 5)))
    # # print(cloud.points)
    
