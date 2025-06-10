from typing import Self

WIDTH, HEIGHT = 1024, 750


class Point2d:
    __slots__ = ("_x", "_y")  # Оптимизация памяти через slots

    def __init__(self, x: float, y: float) -> None:
        self.x = x  # Используем сеттеры для валидации
        self.y = y

    @property
    def x(self) -> float:
        """Координата X точки. Гарантированно в диапазоне [0, WIDTH]."""
        return self._x

    @x.setter
    def x(self, x: float) -> None:
        """Сеттер с валидацией координаты X."""
        if not (0 <= x <= WIDTH):
            raise ValueError(f"X coordinate must be in [0, {WIDTH}]")
        self._x = x

    @property
    def y(self) -> float:
        """Координата Y точки. Гарантированно в диапазоне [0, HEIGHT]."""
        return self._y

    @y.setter
    def y(self, y: float) -> None:
        """Сеттер с валидацией координаты Y."""
        if not (0 <= y <= HEIGHT):
            raise ValueError(f"Y coordinate must be in [0, {HEIGHT}]")
        self._y = y

    def __eq__(self, other: Self) -> bool:
        """Проверка эквивалентности точек через сравнение координат."""
        return self.x == other.x and self.y == other.y

    def __str__(self) -> str:
        """Пользовательское строковое представление точки."""
        return f"Point2d({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Официальное строковое представление для отладки."""
        return str(self)
