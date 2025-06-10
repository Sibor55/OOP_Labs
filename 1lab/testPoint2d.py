import pytest
from Point2d import Point2d, WIDTH, HEIGHT


class TestPoint2d:
    # Тесты корректного создания точки
    @pytest.mark.parametrize(
        "x, y", [(0, 0), (WIDTH, HEIGHT), (100, 200), (WIDTH // 2, HEIGHT // 2)]
    )
    def test_valid_creation(self, x, y):
        p = Point2d(x, y)
        assert p.x == x
        assert p.y == y

    # Тесты на недопустимые координаты
    @pytest.mark.parametrize(
        "x, y, expected_error",
        [
            (-1, 100, f"X coordinate must be in [0, {WIDTH}]"),
            (WIDTH + 1, 100, f"X coordinate must be in [0, {WIDTH}]"),
            (100, -1, f"Y coordinate must be in [0, {HEIGHT}]"),
            (100, HEIGHT + 1, f"Y coordinate must be in [0, {HEIGHT}]"),
        ],
    )
    def test_invalid_creation(self, x, y, expected_error):
        with pytest.raises(ValueError) as excinfo:
            Point2d(x, y)
        assert expected_error in str(excinfo.value)

    # Тесты сравнения точек
    @pytest.mark.parametrize(
        "p1, p2, expected",
        [
            (Point2d(10, 20), Point2d(10, 20), True),
            (Point2d(10, 20), Point2d(10, 21), False),
            (Point2d(10, 20), Point2d(11, 20), False),
            (Point2d(10, 20), Point2d(11, 21), False),
        ],
    )
    def test_equality(self, p1, p2, expected):
        assert (p1 == p2) == expected

    # Тесты строкового представления
    @pytest.mark.parametrize(
        "x, y, expected_repr",
        [
            (0, 0, "Point2d(0, 0)"),
            (100, 200, "Point2d(100, 200)"),
            (WIDTH, HEIGHT, f"Point2d({WIDTH}, {HEIGHT})"),
        ],
    )
    def test_repr(self, x, y, expected_repr):
        p = Point2d(x, y)
        assert repr(p) == expected_repr
        assert str(p) == expected_repr
