from delaunay import Point, PointCloud, Triangle

# plan:
# - test subdivide
# - initial fan hull
# - add k initial triangles of fan as root nodes
# - Dag query test
# - impl flip + test single call
# - full alg

# fan hull
# - 

class TriangleNode:
    def __init__(self, triangle: Triangle):
        self.triangle = triangle
        self.children = []

    def walk_to_child(self, x: Point):
        if not self.children:
            return self
        for child in self.children:
            if child.inside(x):
                return child
        return None

    def subdivide(self, x: Point):
        if not self.triangle.inside(x):
            raise ValueError(
                "To subdivide triangle with x, x must be inside the triangle"
            )
        looped_points = self.triangle.points + [self.triangle.points[0]]
        for y, z in zip(looped_points, looped_points[1:]):
            self.children.append(Triangle(x, y, z))


class HistoryDAG:
    def __init__(self, cloud: PointCloud):
        self.cloud = cloud
        self.root = TriangleNode(None)
        self.root.children = self._get_root_triangles()

    def _get_root_triangles(self):
        hull = self.cloud.convex_hull
        ref_pt = hull[0]
        pairs = zip(hull[1:], hull[2:]) 
        return [Triangle(ref_pt, p, q) for p, q in pairs]
