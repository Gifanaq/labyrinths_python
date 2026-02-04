from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze


class Generator(ABC):
    """Абстрактный базовый класс для генераторов лабиринтов."""

    @abstractmethod
    def generate(
        self,
        width: int,
        height: int,
        *,
        use_unicode: bool = False,
        seed: int | None = None,
    ) -> Maze:
        """Генерирует лабиринт заданного размера.

        Args:
        ----
            width: Ширина лабиринта в клетках
            height: Высота лабиринта в клетках
            use_unicode: Использовать Unicode символы для отрисовки
            seed: Seed для генератора случайных чисел

        Returns:
        -------
            Сгенерированный лабиринт

        """
