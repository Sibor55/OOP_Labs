import pytest
import math
from Point2d import Point2d
from Vector2d import Vector2d


class TestVector2d:
    # Тесты создания вектора
    @pytest.mark.parametrize("x, y", [(0, 0), (1, 1), (-1, -1), (3.5, 4.2)])
    def test_creation(self, x, y):
        v = Vector2d(x, y)
        assert v.x == x
        assert v.y == y

    # Тесты создания из точек
    @pytest.mark.parametrize(
        "p1, p2, expected_x, expected_y",
        [
            (Point2d(0, 0), Point2d(1, 1), 1, 1),
            (Point2d(1, 2), Point2d(3, 4), 2, 2),
            (Point2d(10, 20), Point2d(5, 5), -5, -15),
        ],
    )
    def test_from_points(self, p1, p2, expected_x, expected_y):
        v = Vector2d.from_points(p1, p2)
        assert math.isclose(v.x, expected_x)
        assert math.isclose(v.y, expected_y)

    # Тесты операций
    @pytest.mark.parametrize(
        "v1, v2, expected_add, expected_sub",
        [
            (Vector2d(1, 2), Vector2d(3, 4), Vector2d(4, 6), Vector2d(-2, -2)),
            (Vector2d(-1, -2), Vector2d(3, 4), Vector2d(2, 2), Vector2d(-4, -6)),
        ],
    )
    def test_add_sub(self, v1, v2, expected_add, expected_sub):
        assert v1 + v2 == expected_add
        assert v1 - v2 == expected_sub

    # Тесты скалярных операций
    @pytest.mark.parametrize(
        "v, scalar, expected_mul, expected_div",
        [
            (Vector2d(1, 2), 2, Vector2d(2, 4), Vector2d(0.5, 1)),
            (Vector2d(3, 4), -1, Vector2d(-3, -4), Vector2d(-3, -4)),
        ],
    )
    def test_scalar_ops(self, v, scalar, expected_mul, expected_div):
        assert v * scalar == expected_mul
        assert scalar * v == expected_mul
        assert v / scalar == expected_div

    # Тесты скалярного произведения
    @pytest.mark.parametrize(
        "v1, v2, expected_dot",
        [
            (Vector2d(1, 0), Vector2d(0, 1), 0),
            (Vector2d(1, 2), Vector2d(3, 4), 11),
            (Vector2d(-1, -2), Vector2d(3, 4), -11),
        ],
    )
    def test_dot_product(self, v1, v2, expected_dot):
        assert math.isclose(v1.dot(v2), expected_dot)
        assert math.isclose(Vector2d.dot_product(v1, v2), expected_dot)

    # Тесты векторного произведения
    @pytest.mark.parametrize(
        "v1, v2, expected_cross",
        [
            (Vector2d(1, 0), Vector2d(0, 1), 1),
            (Vector2d(1, 2), Vector2d(3, 4), -2),
            (Vector2d(-1, -2), Vector2d(3, 4), 2),
        ],
    )
    def test_cross_product(self, v1, v2, expected_cross):
        assert math.isclose(v1.cross(v2), expected_cross)
        assert math.isclose(Vector2d.cross_product(v1, v2), expected_cross)

    # Тесты модуля вектора
    @pytest.mark.parametrize(
        "v, expected_magnitude",
        [(Vector2d(3, 4), 5), (Vector2d(6, 8), 10), (Vector2d(0, 0), 0)],
    )
    def test_magnitude(self, v, expected_magnitude):
        assert math.isclose(abs(v), expected_magnitude)

    # Тесты индексации
    @pytest.mark.parametrize(
        "v, idx, expected_val", [(Vector2d(1, 2), 0, 1), (Vector2d(1, 2), 1, 2)]
    )
    def test_indexing(self, v, idx, expected_val):
        assert v[idx] == expected_val

    # Тесты на недопустимые индексы
    @pytest.mark.parametrize("idx", [-1, 2, 100])
    def test_invalid_indexing(self, idx):
        v = Vector2d(1, 2)
        with pytest.raises(IndexError):
            _ = v[idx]
