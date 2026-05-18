from delaunay import Point, PointCloud, Triangle
import numpy as np

# done:
# - initial fan hull
# - test subdivide

# plan:
# - Dag query test
# - impl flip + test single call
# - full alg

# backlog:
# - make triangleNode subclass triangle for ergonomics
# - no point cloud. use inf triangle.
# - condsider moving containment next node fundtion to DAG if only used once
# - tree leaves function
# - track whick points have been added, (to avoid dupes, hull points)


class TriangleNode:
    def __init__(self, triangle: Triangle):
        self.triangle = triangle
        self.children = []

    def get_containing_child(self, x: Point):
        for child in self.children:
            if child.triangle.contains(x):
                return child
        return None

    def subdivide(self, x: Point):
        if not self.triangle.contains(x):
            raise ValueError(
                "To subdivide triangle with x, x must be inside the triangle"
            )
        looped_points = self.triangle.points + [self.triangle.points[0]]
        for y, z in zip(looped_points, looped_points[1:]):
            tri = Triangle(x, y, z)
            self.children.append(TriangleNode(tri))

class Edge:
    def __init__(self, p: Point, q: Point):
        self.points = tuple(sorted([p, q]))


class HistoryDAG:
    def __init__(self, cloud: PointCloud):
        self.cloud = cloud
        self.root = TriangleNode(None)
        self.edge_to_tris= {} 
        self.root.children = self._get_root_triangles()

    def _get_root_triangles(self):
        hull = self.cloud.convex_hull
        ref_pt = hull[0]
        pairs = zip(hull[1:], hull[2:])
        children = []
        for p, q in pairs:
            new_triangle = TriangleNode(Triangle(ref_pt, p, q))
            if children:
                self.edge_to_tris[Edge(ref_pt, p)] = [new_triangle, children[-1]]
            children.append(new_triangle)
        return children

    def get_leaf(self, x: Point):
        node = self.root
        while next_node := node.get_containing_child(x):
            node = next_node
        return node

    def insert(self, p: Point):
        leaf = self.get_leaf(p)
        leaf.subdivide(p)
        neighbors = triangle_neighbors[leaf]
        for neighbor, e in neighbors:
            p0, p1 = e
            for high_deg_neighbor, _ in triangle_neighbors[neighbor]:

            if 
            

        return leaf.children

    def flip(self, t: TriangleNode, r: TriangleNode, e: list[Point]):
        tx = t.triangle.get_opp_point(*e)
        rx = r.triangle.get_opp_point(*e)
        new_node0 = TriangleNode(Triangle(tx, rx, e[0]))
        new_node1 = TriangleNode(Triangle(tx, rx, e[1]))
        new_nodes = [new_node0, new_node1]
        t.children = new_nodes
        r.children = new_nodes
        return

    def circle_test(t: TriangleNode, r: TriangleNode, e: list[Point]):
        def pull_coords(p: Point):
            return [p.x, p.y, p.x**2 + p.y**2, 1]

        triangle_coords = [pull_coords(p) for p in t.triangle.points]
        last_point = r.triangle.get_opp_point(*e)
        matrix = np.array(triangle_coords + pull_coords(last_point))
        return np.linalg.det(matrix) > 0

    def local_flips(self, p: Point, triangles: list[TriangleNodes]):


