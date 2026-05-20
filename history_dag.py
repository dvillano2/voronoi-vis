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
        self.edge_to_tris = {}
        # self.root.children = self._get_root_triangles()
        self._setup_root_triangles()

    def _setup_root_triangles(self):
        hull = self.cloud.convex_hull
        ref_pt = hull[0]
        pairs = zip(hull[1:], hull[2:])

        print("\n")
        for i, (p, q) in enumerate(pairs):
            print(i)
            new_triangle = TriangleNode(Triangle(ref_pt, p, q))
            if i > 0:
                self.edge_to_tris[Edge(ref_pt, p)] = [
                    new_triangle,
                    self.root.children[-1],
                ]
            self.root.children.append(new_triangle)

        # pairs = zip(hull[1:], hull[2:])
        # for i, (p, q) in enumerate(pairs):
        #    if i > 0:
        #        tris = self.edge_to_tris[Edge(ref_pt, p)]
        #        print(tris)
        #        to_flip = [tri for tri in tris if q in tri.triangle.points]
        #        if not to_flip:
        #            raise ValueError(
        #                "bad fan flipping, missing outermost point"
        #            )
        #        print("HERE")

        assert len(self.root.children) == len(hull[2:])
        for triangle, p in zip(self.root.children, hull[2:]):
            assert not triangle.children
            self.enforce_delaunay(p, [triangle])
            print("size of edge dict:", len(self.edge_to_tris))
            print("total leaves:", len(self.get_leaves()))

        # debug print - are edges correct? alg is never getting an opp edge in the map

    def enforce_delaunay(self, p: Point, cands: list[TriangleNode]):
        # print(cands)
        stack = [tn for tn in cands]
        while stack:
            node = stack.pop()
            if node.children:
                print("non leaf triangle")
                continue
            opp_edge = node.triangle.get_opp_edge(p)
            if opp_edge not in self.edge_to_tris:
                print("enforce_delaunay: early exit on conv hull edge")
                continue
            t, r = self.edge_to_tris[opp_edge]
            if circle_test(t, r, [opp_edge.points[0], opp_edge.points[1]]):
                new_nodes = self.flip(t, r, [opp_edge.points[0], opp_edge.points[1]])
                stack += new_nodes
                # print("STACK", stack)
                print("flipped")
            else:
                print("enforce_delaunay: circle test passed")

    def flip(self, t: TriangleNode, r: TriangleNode, e: list[Point]):
        tx = t.triangle.get_opp_point(*e)
        rx = r.triangle.get_opp_point(*e)
        new_node0 = TriangleNode(Triangle(tx, rx, e[0]))
        new_node1 = TriangleNode(Triangle(tx, rx, e[1]))
        new_nodes = [new_node0, new_node1]
        t.children = new_nodes
        r.children = new_nodes

        edge = Edge(e[0], e[1])
        old_triangles = self.edge_to_tris[edge]
        self.edge_to_tris[Edge(tx, rx)] = new_nodes

        for node in new_nodes:
            for p in node.triangle.points:
                local_edge = node.triangle.get_opp_edge(p)
                if local_edge != edge and local_edge in self.edge_to_tris:
                    tris = self.edge_to_tris[local_edge]
                    to_keep = [tri for tri in tris if tri not in old_triangles]
                    self.edge_to_tris[local_edge] = [node, to_keep[0]]
        del self.edge_to_tris[edge]

        print(f"flip - input triangles: {t.triangle.points}{r.triangle.points}")
        print(f"flip - output triangles: {[t.triangle.points for t in new_nodes]}")
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
            e = child.triangle.get_opp_edge(p)
            if e in self.edge_to_tris:
                v = self.edge_to_tris[e]
                outer_tri = v[1] if v[0] == leaf else v[0]
                self.edge_to_tris[e] = [outer_tri, child]

        # update inner edges adjacencies
        for q in leaf.triangle.points:
            e = Edge(p, q)
            tris = [
                tn
                for tn in leaf.children
                if p in tn.triangle.points and q in tn.triangle.points
            ]
            self.edge_to_tris[e] = tris

        self.enforce_delaunay(p, leaf.children)


def circle_test(t: TriangleNode, r: TriangleNode, e: list[Point]):
    def pull_coords(p: Point):
        return [p.x, p.y, p.x**2 + p.y**2, 1]

    triangle_coords = [pull_coords(p) for p in t.triangle.points]
    last_point = r.triangle.get_opp_point(*e)
    matrix = np.array(triangle_coords + [pull_coords(last_point)])

    return np.linalg.det(matrix) > 0
