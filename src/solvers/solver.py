from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze, Point


class Solver(ABC):
    """Абстрактный базовый класс для алгоритмов решения лабиринтов."""

    @abstractmethod
    def solve(self, maze: Maze, start: Point, end: Point) -> list[Point]:
        """Находит путь от начальной до конечной точки в лабиринте.

        Args:
        ----
            maze: Лабиринт для решения
            start: Начальная точка
            end: Конечная точка

        Returns:
        -------
            Список точек, представляющих путь, или пустой список если путь не найден

        """
