import random
import matplotlib.pyplot as plt
from delaunay import Point, PointCloud
from history_dag import HistoryDAG


def torus():
    layers = 10
    num_points = 8000
    outer_edge = 10000000
    outer_circle = 3 * outer_edge / 4
    inner_circle = outer_edge / 4
    points = [[] for _ in range(layers)]

    def prop_parabola(x):
        return layers**2 + (x - layers / 2) ** 2

    limit_sum = sum(prop_parabola(x) for x in range(layers))
    limits = [num_points * prop_parabola(x) // limit_sum for x in range(layers)]

    while sum([len(bin) for bin in points]) < 7130:
        new_x = random.randint(-outer_edge, outer_edge)
        new_y = random.randint(-outer_edge, outer_edge)
        rad_squared = new_x**2 + new_y**2
        if rad_squared <= inner_circle**2 or rad_squared >= outer_circle**2:
            continue
        for i in range(layers):
            inner_thresh = inner_circle**2 * (
                1 - i / (layers - 1)
            ) + outer_circle**2 * (i / (layers - 1))
            outer_thresh = inner_circle**2 * (
                1 - (i + 1) / (layers - 1)
            ) + outer_circle**2 * ((i + 1) / (layers - 1))
            if inner_thresh < rad_squared < outer_thresh and len(points[i]) < limits[i]:
                points[i].append(Point(new_x, new_y))
        print(f"currently have {sum([len(bin) for bin in points])} points added")
    new_points = []
    for subbin in points:
        new_points.extend(subbin)

    point_cloud = PointCloud(new_points)
    dag = HistoryDAG(point_cloud)
    to_insert = set(point_cloud.points) - set(point_cloud.convex_hull)
    while to_insert:
        new_point = to_insert.pop()
        dag.insert(new_point)
    for t_node in dag.get_leaves():
        t = t_node.triangle
        plt.gca().set_aspect("equal")
        plt.plot(
            [p.x for p in t.points + [t.points[0]]],
            [p.y for p in t.points + [t.points[0]]],
        )

    plt.show()


if __name__ == "__main__":
    torus()
