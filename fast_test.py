from geometry import Point, Triangle
import random


def random_test_1():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(0, 1, False)
    r = Point(1, -1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 0
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (x + y > p.x + p.y and x > p.x)
    print("if not assertions above, 100000 contains tests have passed")


def random_test_2():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(0, 1, False)
    r = Point(-1, -1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 0
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (-x + y > -p.x + p.y and x < p.x)
    print("if not assertions above, 100000 contains tests have passed")


def random_test_3():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(-1, -1, False)
    r = Point(1, -1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 0
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (
            -x + y < -p.x + p.y and x + y < p.x + p.y
        )
    print("if not assertions above, 100000 contains tests have passed")


def random_test_4():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    p, q = sorted([p, q])
    r = Point(0, 1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 1
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (
            x > p.x and x < q.x and Point.is_left(p, q, new_point)
        )
    print("if not assertions above, 100000 contains tests have passed")


def random_test_5():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    p, q = sorted([p, q], key=lambda r: -r.x + r.y)
    r = Point(-1, -1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 1
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (
            -x + y > -p.x + p.y
            and -x + y < -q.x + q.y
            and Point.is_left(p, q, new_point)
        )
    print("if not assertions above, 100000 contains tests have passed")


def random_test_6():
    p = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    q = Point(
        random.randint(-1000000, 1000000), random.randint(-1000000, 1000000)
    )
    p, q = sorted([p, q], key=lambda r: -r.x + -r.y)
    r = Point(1, -1, False)
    t = Triangle(p, q, r)
    assert len(t.edges) == 1
    print(f"ordered points are {t.points}")
    for _ in range(100000):
        x = random.randint(-10000, 100000)
        y = random.randint(-10000, 100000)
        new_point = Point(x, y)
        assert t.contains(new_point) == (
            -x + -y > -p.x + -p.y
            and -x + -y < -q.x + -q.y
            and Point.is_left(p, q, new_point)
        )
    print("if not assertions above, 100000 contains tests have passed")


if __name__ == "__main__":
    print("FIRST TEST")
    for _ in range(100):
        random_test_1()
    print("SECOND TEST")
    for _ in range(100):
        random_test_2()
    print("THIRD TEST")
    for _ in range(100):
        random_test_3()
    print("FOURTH TEST")
    for _ in range(100):
        random_test_4()
    print("FIFTH TEST")
    for _ in range(100):
        random_test_5()
    print("SIXTH TEST")
    for _ in range(100):
        random_test_6()
