from delaunay import Point, PointCloud, Triangle

# done: 
# - initial fan hull

# plan:
# - test subdivide
# - Dag query test
# - impl flip + test single call
# - full alg

# fan hull
# - 

# backlog:
# - make triangleNode subclass triangle for ergonomics
# - no point cloud. use inf triangle.

class TriangleNode:
    def __init__(self, triangle: Triangle):
        self.triangle = triangle
        self.children = []

    def walk_to_child(self, x: Point):
        if not self.children:
            return self
        for child in self.children:
            if child.contains(x):
                return child
        return None

    def subdivide(self, x: Point):
        if not self.triangle.contains(x):
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
        return [TriangleNode(Triangle(ref_pt, p, q)) for p, q in pairs]

    def get_leaf(self, node: TriangleNode, p: Point):
        if node != None and not node.children:
            return node
        for child in node.children:
            if child.contains(p):
                return get_leaf(child, p)

    def insert(self, p: Point):
        node = self.root

        # while node != (succ := node.walk_to_child(p)):
        #     node = succ

        
        
