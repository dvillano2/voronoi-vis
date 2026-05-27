import numpy as np
from geometry import Edge, Point, Triangle, looped_pairs

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
        self.children: list[TriangleNode] = []

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
        for y, z in looped_pairs(self.points):
            self.children.append(TriangleNode(x, y, z))


class HistoryDAG:
    def __init__(self):
        self.root = TriangleNode(
            Point(0, 1, False), Point(-1, -1, False), Point(1, -1, False)
        )
        print(f"root edges are {self.root.edges}")
        self.edge_to_tris: dict[Edge, list[TriangleNode]] = {
            e: [self.root, self.root] for e in self.root.edges
        }

        # self.root.children = self._get_root_triangles()
        # self._setup_root_triangles()

    # def _setup_root_triangles(self):
    #    hull = self.cloud.convex_hull
    #    ref_pt = hull[0]
    #    pairs = zip(hull[1:], hull[2:])

    #    for i, (p, q) in enumerate(pairs):
    #        new_triangle = TriangleNode(ref_pt, p, q)
    #        if i > 0:
    #            self.edge_to_tris[Edge(ref_pt, p)] = [
    #                new_triangle,
    #                self.root.children[-1],
    #            ]
    #        self.root.children.append(new_triangle)

    #    assert len(self.root.children) == len(hull[2:])
    #    for triangle, p in zip(self.root.children, hull[2:]):
    #        assert not triangle.children
    #        self.enforce_delaunay(p, [triangle])
    #        print("size of edge dict:", len(self.edge_to_tris))
    #        print("total leaves:", len(self.get_leaves()))

    def enforce_delaunay(self, p: Point, cands: list[TriangleNode]):
        stack = list(cands)
        while stack:
            node = stack.pop()
            if node.children:
                # print("non leaf triangle")
                continue
            opp_edge = node.get_opp_edge(p)
            if opp_edge not in self.edge_to_tris:
                # print("enforce_delaunay: early exit on conv hull edge")
                continue
            t, r = self.edge_to_tris[opp_edge]
            if circle_test(t, r, opp_edge):
                new_nodes = self.flip(t, r, opp_edge)
                stack += new_nodes
                # print("STACK", stack)
                # print("flipped")
            else:
                pass
                # print("enforce_delaunay: circle test passed")

    def flip(self, t: TriangleNode, r: TriangleNode, e: Edge):
        tx = t.get_opp_point(e)
        rx = r.get_opp_point(e)
        new_nodes = [TriangleNode(tx, rx, x) for x in e.points]
        t.children = new_nodes
        r.children = new_nodes

        old_triangles = self.edge_to_tris[e]
        self.edge_to_tris[Edge(tx, rx)] = new_nodes

        for node in new_nodes:
            for p in node.points:
                local_edge = node.get_opp_edge(p)
                if local_edge != e and local_edge in self.edge_to_tris:
                    tris = self.edge_to_tris[local_edge]
                    to_keep = [tri for tri in tris if tri not in old_triangles]
                    self.edge_to_tris[local_edge] = [node, to_keep[0]]
        del self.edge_to_tris[e]

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
        print(f"inserting point {p.x}, {p.y}")
        leaf = self.get_leaf(p)
        leaf.subdivide(p)

        # update outer edge adjacencies
        for child in leaf.children:
            e = child.get_opp_edge(p)
            # if e in self.edge_to_tris:
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
        print(f"THERE ARE {len(self.edge_to_tris)} EDGES IN THE DICT")


def circle_test(t: TriangleNode, r: TriangleNode, e: Edge):
    if e not in t.edges + r.edges:
        raise ValueError("edges must belong to both triangles")
    present_point = t.get_opp_point(e)
    last_point = r.get_opp_point(e)

    # plan for deterimining flips:
    # rule: never flip or flip to totally infinite edge
    # rule: never flip finite edge to infinite edge
    # infinite edge flipped to infinite edge is valid if they cross
    # infinite edge flipped to finite edge if valid if they cross
    # above is gauranteed for finite edge to finite edge....
    # in that case need to defer to circle test
    # order: first infinte edge to infinte edge.. greedy on new
    # point... give that point as many infinite edges as possible
    # then infinite to finite, then finite to finite

    # should not flip edge at infinity
    if not e.p.is_finite and not e.q.is_finite:
        return False
    # should not flip to edge at infinity
    if not present_point.is_finite and not last_point.is_finite:
        return False

    # DUMMY FOR TESTS
    if not e.p.is_finite or not e.q.is_finite:
        return False
    # should not flip to edge at infinity
    if not present_point.is_finite or not last_point.is_finite:
        return False
    # don't flip finite edge to infinte edge
    if (e.p.is_finite and e.q.is_finite) and (
        not present_point.is_finite or not last_point.is_finite
    ):
        return False

    ### SUGGESTED RULE FOR FLIPPING RAY TO RAY:
    ### IF NIEGHOBOR HAS MORE INFINITE POINTS, FLIP
    ### ELSE DONT

    # if infinite edge to be flipped crossed with
    # finite edge that replaces it, do it,
    # otherwise don't
    # if not e.p.is_finite or not e.q.is_finite:
    # refactor

    # points lie on the same side of the line
    # so
    # if Point.is_left(e.p, e.q, present_point) == Point.is_left(
    #     e.p, e.q, last_point
    # ):
    #     return False

    # tripled_t = t.triple()
    # tripled_r = r.triple()
    # a, b = present_point.x, present_point.y
    # z, w = last_point.x, last_point.y
    # interpolated_point_1 = Point(a + z, 2 * b + 2 * w)
    # interpolated_point_2 = Point(2 * a + 2 * z, b + w)
    # condition_1 = tripled_t.contains(
    #     interpolated_point_1
    # ) or tripled_r.contains(interpolated_point_2)
    # condition_2 = tripled_t.contains(
    #     interpolated_point_2
    # ) or tripled_r.contains(interpolated_point_2)
    # if condition_1 or condition_2:
    #     return False
    # return True

    # if everything is finite, go back to circle test
    def pull_coords(p: Point):
        return [p.x, p.y, p.x**2 + p.y**2, 1]

    triangle_coords = [pull_coords(p) for p in t.points]
    matrix = np.array(triangle_coords + [pull_coords(last_point)])

    return np.linalg.det(matrix) > 0
