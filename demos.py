import random
import matplotlib.pyplot as plt
from delaunay import Point, PointCloud, Triangle


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
