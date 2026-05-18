from delaunay import Edge, Point, PointCloud, Triangle
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
        # update outer edge adjacencies
        for child in leaf.children:
            e = child.triangle.get_opp_edge(p)
            if e in self.edge_to_tris:
                outer_tri = v[1] if v[0] == leaf else v[1]
                self.edge_to_tris[e] = [outer_tri, child]
        # update inner edges adjacencies
        for q in leaf.triangle.points:
            e = Edge(p, q)
            tris = [tn for tn in leaf.children if p in tn.triangle.points and q in tn.triangle.points]
            self.edge_to_tris[e] = tris

        self.enforce_delaunay(p, leaf.children)

        return leaf.children

    def enforce_delaunay(self, p: Point, cands: list[TriangleNode]):
        stack = [tn for tn in cands]
        while stack:
            node = stack.pop()
            opp_edge = node.triangle.get_opp_edge(p)
            t, r = self.edge_to_tris[opp_edge]
            if not circle_test(t, r, [opp_edge.points[0], opp_edge.points[1]]):
               new_nodes = flip(t, r, [opp_edge.points[0], opp_edge.points[1]])
               stack += new_nodes

    def flip(self, t: TriangleNode, r: TriangleNode, e: list[Point]):
        tx = t.triangle.get_opp_point(*e)
        rx = r.triangle.get_opp_point(*e)
        new_node0 = TriangleNode(Triangle(tx, rx, e[0]))
        new_node1 = TriangleNode(Triangle(tx, rx, e[1]))
        new_nodes = [new_node0, new_node1]
        t.children = new_nodes
        r.children = new_nodes

        edge = Edge(e[0], e[1])
        del self.edge_to_tris[edge]
        self.edge_to_tris[Edge(tx, rx)] = new_nodes
        return new_nodes

    def circle_test(t: TriangleNode, r: TriangleNode, e: list[Point]):
        def pull_coords(p: Point):
            return [p.x, p.y, p.x**2 + p.y**2, 1]

        triangle_coords = [pull_coords(p) for p in t.triangle.points]
        last_point = r.triangle.get_opp_point(*e)
        matrix = np.array(triangle_coords + pull_coords(last_point))
        return np.linalg.det(matrix) > 0
