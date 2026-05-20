import numpy as np
from geometry import Edge, Point, PointCloud, Triangle

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
# - track which points have been added, (to avoid dupes, hull points)


class TriangleNode(Triangle):
    def __init__(self, p: Point, q: Point, r: Point):
        super().__init__(p, q, r)
        self.children = []

    def get_containing_child(self, x: Point):
        for child in self.children:
            if child.contains(x):
                return child
        return None

    def subdivide(self, x: Point):
        if not self.contains(x):
            raise ValueError(
                "To subdivide triangle with x, x must be inside the triangle"
            )
        looped_points = self.points + [self.points[0]]
        for y, z in zip(looped_points, looped_points[1:]):
            self.children.append(TriangleNode(x, y, z))


class HistoryDAG:
    def __init__(self, cloud: PointCloud):
        self.cloud = cloud
        self.root = TriangleNode(None, None, None)
        self.edge_to_tris = {}
        # self.root.children = self._get_root_triangles()
        self._setup_root_triangles()

    def _setup_root_triangles(self):
        hull = self.cloud.convex_hull
        ref_pt = hull[0]
        pairs = zip(hull[1:], hull[2:])

        for i, (p, q) in enumerate(pairs):
            new_triangle = TriangleNode(ref_pt, p, q)
            if i > 0:
                self.edge_to_tris[Edge(ref_pt, p)] = [
                    new_triangle,
                    self.root.children[-1],
                ]
            self.root.children.append(new_triangle)

        assert len(self.root.children) == len(hull[2:])
        for triangle, p in zip(self.root.children, hull[2:]):
            assert not triangle.children
            self.enforce_delaunay(p, [triangle])
            print("size of edge dict:", len(self.edge_to_tris))
            print("total leaves:", len(self.get_leaves()))

    def enforce_delaunay(self, p: Point, cands: list[TriangleNode]):
        stack = list(cands)
        while stack:
            node = stack.pop()
            if node.children:
                print("non leaf triangle")
                continue
            opp_edge = node.get_opp_edge(p)
            if opp_edge not in self.edge_to_tris:
                print("enforce_delaunay: early exit on conv hull edge")
                continue
            t, r = self.edge_to_tris[opp_edge]
            if circle_test(t, r, [opp_edge.points[0], opp_edge.points[1]]):
                new_nodes = self.flip(
                    t, r, [opp_edge.points[0], opp_edge.points[1]]
                )
                stack += new_nodes
                # print("STACK", stack)
                print("flipped")
            else:
                print("enforce_delaunay: circle test passed")

    def flip(self, t: TriangleNode, r: TriangleNode, e: list[Point]):
        tx = t.get_opp_point(*e)
        rx = r.get_opp_point(*e)
        new_node0 = TriangleNode(tx, rx, e[0])
        new_node1 = TriangleNode(tx, rx, e[1])
        new_nodes = [new_node0, new_node1]
        t.children = new_nodes
        r.children = new_nodes

        edge = Edge(e[0], e[1])
        old_triangles = self.edge_to_tris[edge]
        self.edge_to_tris[Edge(tx, rx)] = new_nodes

        for node in new_nodes:
            for p in node.points:
                local_edge = node.get_opp_edge(p)
                if local_edge != edge and local_edge in self.edge_to_tris:
                    tris = self.edge_to_tris[local_edge]
                    to_keep = [tri for tri in tris if tri not in old_triangles]
                    self.edge_to_tris[local_edge] = [node, to_keep[0]]
        del self.edge_to_tris[edge]

        print(f"flip - input triangles: {t.points}{r.points}")
        print(f"flip - output triangles: {[t.points for t in new_nodes]}")
        return new_nodes

    def get_leaves(self):
        seen = set()
        res = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if not node.children:
                res.append(node)
            else:
                stack += node.children
        return res

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
            e = child.get_opp_edge(p)
            if e in self.edge_to_tris:
                v = self.edge_to_tris[e]
                outer_tri = v[1] if v[0] == leaf else v[0]
                self.edge_to_tris[e] = [outer_tri, child]

        # update inner edges adjacencies
        for q in leaf.points:
            e = Edge(p, q)
            tris = [
                tn for tn in leaf.children if p in tn.points and q in tn.points
            ]
            self.edge_to_tris[e] = tris

        self.enforce_delaunay(p, leaf.children)


def circle_test(t: TriangleNode, r: TriangleNode, e: list[Point]):
    def pull_coords(p: Point):
        return [p.x, p.y, p.x**2 + p.y**2, 1]

    triangle_coords = [pull_coords(p) for p in t.points]
    last_point = r.get_opp_point(*e)
    matrix = np.array(triangle_coords + [pull_coords(last_point)])

    return np.linalg.det(matrix) > 0
