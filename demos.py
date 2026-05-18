import random
import matplotlib.pyplot as plt
from delaunay import Point, PointCloud, Triangle
from history_dag import HistoryDAG


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
            hull = point_cloud.convex_hull + [point_cloud.convex_hull[0]]
            ax[i, j].plot(
                [p.x for p in hull],
                [p.y for p in hull],
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


def fan_demo():
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
            dag = HistoryDAG(point_cloud)
            ax[i, j].plot(
                [
                    p.x
                    for t in dag.root.children
                    for p in t.triangle.points + [t.triangle.points[0]]
                ],
                [
                    p.y
                    for t in dag.root.children
                    for p in t.triangle.points + [t.triangle.points[0]]
                ],
            )
            ax[i, j].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )

    plt.tight_layout()
    plt.show()


def DAG_subdivide_demo():
    fig, ax = plt.subplots(4, 4)
    for i in range(4):
        for j in range(4):
            num_points = 4
            ch_triangle = False
            while not ch_triangle:
                points = []
                for _ in range(num_points):
                    new_x = random.randint(-100, 100)
                    new_y = random.randint(-100, 100)
                    points.append(Point(new_x, new_y))
                point_cloud = PointCloud(points)
                ch_triangle = len(point_cloud.convex_hull) == 3
            dag = HistoryDAG(point_cloud)
            for p in point_cloud.points:
                if p not in point_cloud.convex_hull:
                    dag.insert(p)
                    break
            for t_node in dag.root.children[0].children:
                t = t_node.triangle
                ax[i, j].plot(
                    [p.x for p in t.points + [t.points[0]]],
                    [p.y for p in t.points + [t.points[0]]],
                )
            ax[i, j].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )
    plt.tight_layout()
    plt.show()


def two_subdivide_demo():
    fig, ax = plt.subplots(4, 3)
    for i in range(4):
        points = [Point(100, -240), Point(-400, 700), Point(700, 800)]

        # for _ in range(3):
        #    new_x = random.randint(-400, 400)
        #    new_y = random.randint(-400, 400)
        #    points.append(Point(new_x, new_y))
        big_triangle = Triangle(*points)
        for _ in range(2):
            while True:
                new_x = random.randint(-200, 300)
                new_y = random.randint(100, 500)
                if big_triangle.contains(Point(new_x, new_y)):
                    points.append(Point(new_x, new_y))
                    break
        point_cloud = PointCloud(points)
        dag = HistoryDAG(point_cloud)
        used = []
        for j in range(3):
            for t_node in dag.get_leaves():
                t = t_node.triangle
                ax[i, j].plot(
                    [p.x for p in t.points + [t.points[0]]],
                    [p.y for p in t.points + [t.points[0]]],
                )
            if j == 0:
                ax[i, j].scatter(
                    [p.x for p in point_cloud.points],
                    [p.y for p in point_cloud.points],
                )
            for p in point_cloud.points:
                if p not in point_cloud.convex_hull and p not in used:
                    dag.insert(p)
                    used.append(p)
                    break

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # triangle_membership_demo()
    # convex_hull_demo()
    # fan_demo()
    # DAG_subdivide_demo()
    two_subdivide_demo()

    # _pts = [[1, 1], [2, 4], [3, 3]]
    # pts = [Point(x, y) for x, y in _pts]
    # cloud = PointCloud(pts)
    # triangle = Triangle(*pts)
    # # print(triangle.points)
    # print(triangle.inside(Point(2, 3)))
    # print(triangle.inside(Point(2, 5)))
    # # print(cloud.points)
