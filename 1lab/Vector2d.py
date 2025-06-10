from typing import Self, Iterator
import math
from Point2d import Point2d


class Vector2d:
    __slots__ = ("_x", "_y")  # Оптимизация памяти через slots

    def __init__(self, x: float, y: float) -> None:
        self.x = x  # Прямое присвоение через свойства
        self.y = y

    @classmethod
    def from_points(cls, start: Point2d, end: Point2d) -> Self:
        """Перегрузка к-ра: вектор из двух точек."""
        return cls(end.x - start.x, end.y - start.y)

    @property
    def x(self) -> float:
        """Компонента X вектора."""
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        """Сеттер для компоненты X."""
        self._x = value

    @property
    def y(self) -> float:
        """Компонента Y вектора."""
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        """Сеттер для компоненты Y."""
        self._y = value

    def __getitem__(self, index: int) -> float:
        """Доступ к компонентам по индексу [0,1]."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Index out of range. Use 0 for X or 1 for Y")

    def __setitem__(self, index: int, value: float) -> None:
        """Изменение компонент по индексу [0,1]."""
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError("Index out of range. Use 0 for X or 1 for Y")

    def __iter__(self) -> Iterator[float]:
        """Итерация по компонентам вектора (x, y)."""
        yield self.x
        yield self.y

    def __len__(self) -> int:
        """Количество компонент вектора (фиксированное значение)."""
        return 2

    def __eq__(self, other: Self) -> bool:
        """Проверка эквивалентности векторов через сравнение компонент."""
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)

    def __str__(self) -> str:
        """Пользовательское строковое представление вектора."""
        return f"Vector2d({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Официальное строковое представление для отладки."""
        return str(self)

    def __abs__(self) -> float:
        """Модуль вектора (евклидова норма)."""
        return math.sqrt(self.x**2 + self.y**2)

    def __add__(self, other: Self) -> Self:
        """Поэлементное сложение векторов."""
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        """Поэлементное вычитание векторов."""
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Self:
        """Умножение вектора на скаляр (слева)."""
        return self.__class__(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Self:
        """Умножение вектора на скаляр (справа)."""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Self:
        """Деление вектора на скаляр с плавающей точкой."""
        if scalar == 0:
            raise ZeroDivisionError("Vector division by zero")
        return self.__class__(self.x / scalar, self.y / scalar)

    def dot(self, other: Self) -> float:
        """Скалярное произведение двух векторов (метод экземпляра)."""
        return self.x * other.x + self.y * other.y

    @classmethod
    def dot_product(cls, v1: Self, v2: Self) -> float:
        """Статический метод для скалярного произведения двух векторов."""
        return v1.x * v2.x + v1.y * v2.y

    def cross(self, other: Self) -> float:
        """Векторное произведение 2D (псевдоскалярное значение)."""
        return self.x * other.y - self.y * other.x

    @classmethod
    def cross_product(cls, v1: Self, v2: Self) -> float:
        """Статический метод для векторного произведения 2D."""
        return v1.x * v2.y - v1.y * v2.x

    def triple_product(self, v2: Self, v3: Self) -> float:
        """Смешанное произведение: v1 · (v2 × v3) для 2D векторов."""
        return self.dot(Vector2d(v2.x, v2.y)) * v3.cross(self)
