from __future__ import annotations
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
# - condsider moving containment next node function to DAG if only used once
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
        return [Triangle(x, y, z) for y, z in looped_pairs(self.points)]


class HistoryDAG:
    def __init__(self):
        root_triangle = Triangle(
            Point(0, 1, False), Point(-1, -1, False), Point(1, -1, False)
        )
        self.root = TriangleNode(*root_triangle.points)
        # print(f"root edges are {self.root.edges}")
        self.edge_to_tris: dict[Edge, list[TriangleNode]] = {
            e: [self.root, self.root] for e in self.root.edges
        }
        self.triangles_present: dict[Triangle, TriangleNode] = {
            root_triangle: self.root
        }

    def enforce_delaunay(self, p: Point, cands: list[TriangleNode]):
        """p is finite"""
        stack = list(cands)
        stack.sort(key=lambda x: 0 if x.is_finite else 1)
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
            if crossing_test(t, r, opp_edge) and circle_test(t, r, opp_edge):
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

        new_triangles = [Triangle(tx, rx, x) for x in e.points]
        new_nodes = []
        for new_triangle in new_triangles:
            if new_triangle not in self.triangles_present:
                self.triangles_present[new_triangle] = TriangleNode(
                    *new_triangle.points
                )
            node = self.triangles_present[new_triangle]
            new_nodes.append(node)

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

        # print(f"flip - input triangles: {t.points}{r.points}")
        # print(f"flip - output triangles: {[t.points for t in new_nodes]}")
        return new_nodes

    def get_leaves(self):
        seen = set()
        res = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node in seen:
                # print("SEEN")
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
        # print(f"INSERTING POINT {p.x}, {p.y}")
        leaf = self.get_leaf(p)
        assert not leaf.children
        # print(f"INTO TRIANGLE {leaf.points}")
        new_triangles = leaf.subdivide(p)
        for new_triangle in new_triangles:
            if new_triangle in self.triangles_present:
                leaf.children.append(self.triangles_present[new_triangle])
            else:
                new_node = TriangleNode(*new_triangle.points)
                self.triangles_present[new_triangle] = new_node
                leaf.children.append(new_node)

        # print(f"subdivided leaf is \n {leaf.points}")

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
        # print(f"THERE ARE {len(self.edge_to_tris)} EDGES IN THE DICT")


def crossing_test(t: TriangleNode, r: TriangleNode, e: Edge):
    if e.totally_infinite:
        return False
    present_point = t.get_opp_point(e)
    last_point = r.get_opp_point(e)
    return Edge.cross(e, Edge(present_point, last_point))


def circle_test(t: TriangleNode, r: TriangleNode, e: Edge):
    """
    no longer symmetric in t and r,
    should be passed to a refactor later,
    but for now just trying to get it working
    """
    if e not in t.edges + r.edges:
        raise ValueError("edges must belong to both triangles")
    present_point = t.get_opp_point(e)
    last_point = r.get_opp_point(e)

    # dont switch finite to infinte point
    if e.is_finite and not (present_point.is_finite and last_point.is_finite):
        return False
    # besides above, if its not all finite, cross test should
    # determine whether flip get fired
    if not all([e.is_finite, present_point.is_finite, last_point.is_finite]):
        return True

    # if everything is finite, go back to circle test
    def pull_coords(p: Point):
        return [p.x, p.y, p.x**2 + p.y**2, 1]

    triangle_coords = [pull_coords(p) for p in t.points]
    matrix = np.array(triangle_coords + [pull_coords(last_point)])

    return np.linalg.det(matrix) > 0
