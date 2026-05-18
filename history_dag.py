from delaunay import Point, PointCloud, Triangle
from typing import Optional

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


class TriangleNode:
    def __init__(self, triangle: Optional[Triangle]):
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


class HistoryDAG:
    def __init__(self, cloud: PointCloud):
        self.cloud = cloud
        self.root = TriangleNode(None)
        self.root.children = self._get_root_triangles()

    def _get_root_triangles(self):
        hull = self.cloud.convex_hull
        ref_pt = hull[0]
        pairs = zip(hull[1:], hull[2:])
        return [TriangleNode(Triangle(ref_pt, p, q)) for p, q in pairs]

    def get_leaf(self, x: Point):
        node = self.root
        while next_node := node.get_containing_child(x):
            node = next_node
        return node

    def insert(self, p: Point):
        leaf = self.get_leaf(p)
        leaf.subdivide(p)
