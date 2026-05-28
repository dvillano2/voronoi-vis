import random
import matplotlib.pyplot as plt
from geometry import Point, PointCloud
from history_dag import HistoryDAG


def sample_ring(inner, outer, pulls):
    points = []
    inner_sq = inner**2
    outer_sq = outer**2
    while len(points) < pulls:
        new_x = random.randint(-outer, outer)
        new_y = random.randint(-inner, inner)
        if inner_sq < new_x**2 + new_y**2 < outer_sq:
            points.append(Point(new_x, new_y))
    return points


def torus_layers(inner, outer, tiers):
    step = (outer - inner) / tiers
    return [
        [int(inner + i * step), int(inner + (i + 1) * step)]
        for i in range(tiers)
    ]


def distribution_ratios(tiers):
    non_normalized = [
        tiers**2 + abs((x + 2 - (tiers / 2)) ** 2) for x in range(tiers)
    ]
    return [x / sum(non_normalized) for x in non_normalized]


def torus():
    tiers = 20
    num_points = 10000
    outer_edge = 10000000
    outer_circle = 3 * outer_edge / 4
    inner_circle = outer_edge / 4
    torus_tiers = torus_layers(inner_circle, outer_circle, tiers)
    ratios = distribution_ratios(tiers)
    tiered_totals = [int(num_points * x) for x in ratios]
    points = []
    for [inner, outer], pulls in zip(torus_tiers, tiered_totals):
        points.extend(sample_ring(inner, outer, pulls))

    dag = HistoryDAG()
    # point_cloud = PointCloud(points)
    # dag = HistoryDAG(point_cloud)
    # to_insert = set(point_cloud.points) - set(point_cloud.convex_hull)
    # while to_insert:
    #     new_point = to_insert.pop()
    #     dag.insert(new_point)
    plt.gca().set_aspect("equal")
    for point in points:
        dag.insert(point)
    for t_node in dag.get_leaves():
        if t_node.is_finite:
            plt.plot(
                [p.x for e in t_node.edges for p in e.points],
                [p.y for e in t_node.edges for p in e.points],
            )

    plt.show()


if __name__ == "__main__":
    torus()
