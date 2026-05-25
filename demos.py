import random
import matplotlib.pyplot as plt
from geometry import Point, PointCloud, Triangle
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
            triangle_points = points[:3]
            points = points[3:]

            t = Triangle(*triangle_points)
            ax[i, j].plot(
                [p.x for e in t.edges for p in e.points],
                [p.y for e in t.edges for p in e.points],
                c="k",
            )
            ax[i, j].scatter(
                [p.x for p in points if t.contains(p)],
                [p.y for p in points if t.contains(p)],
                c="r",
            )
            ax[i, j].scatter(
                [p.x for p in points if not t.contains(p)],
                [p.y for p in points if not t.contains(p)],
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
                    for e in t.edges
                    for p in e.points
                ],
                [
                    p.y
                    for t in dag.root.children
                    for e in t.edges
                    for p in e.points
                ],
            )
            ax[i, j].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )

    plt.tight_layout()
    plt.show()


# side-by-side of fan and corrected fan
def corrected_fan_demo():
    fig, ax = plt.subplots(4, 2)
    for i in range(4):
        num_points = random.randint(5, 60)
        points = []
        for _ in range(num_points):
            new_x = random.randint(-100, 100)
            new_y = random.randint(-100, 100)
            points.append(Point(new_x, new_y))

        point_cloud = PointCloud(points)
        dag = HistoryDAG(point_cloud)
        leaves = dag.get_leaves()
        for leaf in leaves:
            print(leaf.points)
        for j, nodes in enumerate([dag.root.children, leaves]):
            ax[i, j].set_aspect("equal")
            for node in nodes:
                ax[i, j].plot(
                    [p.x for e in node.edges for p in e.points],
                    [p.y for e in node.edges for p in e.points],
                )
            ax[i, j].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
                s=5,
            )

    plt.tight_layout()
    plt.show()


def DAG_subdivide_demo():
    fig, ax = plt.subplots(4, 4, sharex=True, sharey=True)
    for i in range(4):
        dag = HistoryDAG()
        points = []
        for _ in range(2):
            new_x = random.randint(-100, 100)
            new_y = random.randint(-100, 100)
            p = Point(new_x, new_y)
            points.append(p)
            dag.insert(p)
        for j in range(4):
            # print(f"Working on plot {i}, {j}")
            new_x = random.randint(-100, 100)
            new_y = random.randint(-100, 100)
            p = Point(new_x, new_y)
            points.append(p)
            dag.insert(p)
            for t_node in dag.get_leaves():
                t_node.plot(ax[i, j])
            ax[i, j].scatter(
                [p.x for p in points],
                [p.y for p in points],
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
                ax[i, j].plot(
                    [p.x for e in t_node.edges for p in e.points],
                    [p.y for e in t_node.edges for p in e.points],
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


def det_two_subdivide_demo():
    fig, ax = plt.subplots(4, 3)
    for i in range(4):
        points = [
            Point(x=100, y=-240),
            Point(700, 800),
            Point(-400, 700),
            Point(x=285, y=223),
            Point(x=224, y=365),
        ]

        point_cloud = PointCloud(points)
        dag = HistoryDAG(point_cloud)
        used = []
        for j in range(3):
            print("\n")
            for t_node in dag.get_leaves():
                print(t_node.points)
                ax[i, j].plot(
                    [p.x for e in t_node.edges for p in e.points],
                    [p.y for e in t_node.edges for p in e.points],
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


def fan_and_insert_demo():
    fig, ax = plt.subplots(4, 2)
    for i in range(4):
        num_points = random.randint(400, 600)
        points = []
        for _ in range(num_points):
            new_x = random.randint(-10000, 10000)
            new_y = random.randint(-10000, 10000)
            points.append(Point(new_x, new_y))
        point_cloud = PointCloud(points)
        dag = HistoryDAG(point_cloud)
        to_insert = set(point_cloud.points) - set(point_cloud.convex_hull)
        for t_node in dag.get_leaves():
            ax[i, 0].set_aspect("equal")
            ax[i, 0].plot(
                [p.x for p in t_node.points + [t_node.points[0]]],
                [p.y for p in t_node.points + [t_node.points[0]]],
            )
            ax[i, 0].scatter(
                [p.x for p in point_cloud.points],
                [p.y for p in point_cloud.points],
            )
        while to_insert:
            new_point = to_insert.pop()
            dag.insert(new_point)
        for t_node in dag.get_leaves():
            t = t_node
            ax[i, 1].set_aspect("equal")
            ax[i, 1].plot(
                [p.x for p in t.points + [t.points[0]]],
                [p.y for p in t.points + [t.points[0]]],
            )

    plt.tight_layout()
    plt.show()


def one_big():
    num_points = 8000
    outer_edge = 10000000
    outer_circle = 3 * outer_edge / 4
    inner_circle = outer_edge / 4
    points = []
    while len(points) < num_points:
        new_x = random.randint(-outer_edge, outer_edge)
        new_y = random.randint(-outer_edge, outer_edge)
        rad_squared = new_x**2 + new_y**2
        if inner_circle**2 < rad_squared < outer_circle**2:
            points.append(Point(new_x, new_y))
    point_cloud = PointCloud(points)
    dag = HistoryDAG(point_cloud)
    to_insert = set(point_cloud.points) - set(point_cloud.convex_hull)
    while to_insert:
        new_point = to_insert.pop()
        dag.insert(new_point)
    for t_node in dag.get_leaves():
        plt.gca().set_aspect("equal")
        plt.plot(
            [p.x for p in t_node.points + [t_node.points[0]]],
            [p.y for p in t_node.points + [t_node.points[0]]],
        )

    plt.show()


if __name__ == "__main__":
    # triangle_membership_demo()
    # convex_hull_demo()
    # fan_demo()
    # corrected_fan_demo()
    DAG_subdivide_demo()
    # two_subdivide_demo()
    # det_two_subdivide_demo()
    # fan_and_insert_demo()
    # one_big()
