from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import pairwise
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class CellType(str, Enum):
    """Типы клеток для ASCII отрисовки."""

    WALL = "#"
    EMPTY = " "
    PATH = "."
    START = "O"
    END = "X"


class CellUnicode(Enum):
    """Unicode символы для отрисовки лабиринта."""

    WALL = "\u2588"  # (█)
    EMPTY = "\u0020"  # (пробел)
    PATH = "\u00B7"  # (·)
    START = "\u25CB"  # (◯)
    END = "\u2713"  # (✔)


class Terrain(Enum):
    """Типы поверхностей клеток с разной стоимостью прохождения."""

    FLOOR = " "
    SAND = ":"
    MUD = "~"
    ROAD = "="
    COIN = "$"


TERRAIN_COST: dict[Terrain, float] = {
    Terrain.FLOOR: 1.0,
    Terrain.SAND: 2.0,
    Terrain.MUD: 3.0,
    Terrain.ROAD: 0.6,
    Terrain.COIN: 0.2,
}


@dataclass(frozen=True, order=True)
class Point:
    """Точка в двумерном пространстве."""

    x: int
    y: int

    @staticmethod
    def parse(s: str) -> Point:
        """Парсит строку в формате 'x,y' в объект Point.

        Args:
        ----
            s: Строка в формате 'x,y'

        Returns:
        -------
            Объект Point

        Raises:
        ------
            ValueError: Если формат некорректный или координаты отрицательные

        """
        try:
            x_str, y_str = s.split(",", 1)
            x, y = int(x_str), int(y_str)
        except ValueError as err:
            error_message = (
                "Координаты должны быть в формате x,y где x и y - целые числа."
            )
            raise ValueError(error_message) from err
        if x < 0 or y < 0:
            error_message = "Координаты должны быть больше нуля."
            raise ValueError(error_message)
        return Point(x, y)


class Maze:
    """Представление лабиринта с клетками и соединениями."""

    def __init__(self, width: int, height: int, *, use_unicode: bool = False) -> None:
        if width <= 0 or height <= 0:
            msg = "Размеры лабиринта должны быть положительными."
            raise ValueError(msg)
        self.width = width
        self.height = height
        self.use_unicode = use_unicode
        self._adj: list[list[set[Point]]] = [
            [set() for _ in range(height)] for _ in range(width)
        ]
        self._terrain: list[list[Terrain]] = [
            [Terrain.FLOOR for _ in range(height)] for _ in range(width)
        ]

    def set_terrain(self, p: Point, t: Terrain) -> None:
        """Устанавливает тип поверхности для указанной клетки."""
        if not self.in_bounds(p):
            error_message = "Точка вне границ."
            raise ValueError(error_message)
        self._terrain[p.x][p.y] = t

    def get_terrain(self, p: Point) -> Terrain:
        """Возвращает тип поверхности клетки."""
        return self._terrain[p.x][p.y]

    def step_cost(self, _from: Point, to: Point) -> float:
        """Возвращает стоимость перемещения между двумя клетками."""
        return TERRAIN_COST[self.get_terrain(to)]

    def in_bounds(self, p: Point) -> bool:
        """Проверяет, находится ли точка в границах лабиринта."""
        return 0 <= p.x < self.width and 0 <= p.y < self.height

    def connect(self, p1: Point, p2: Point) -> None:
        """Соединяет две соседние клетки лабиринта."""
        if not (self.in_bounds(p1) and self.in_bounds(p2)):
            error_message = "Нельзя соединять клетки вне границ лабиринта."
            raise ValueError(error_message)
        dx, dy = abs(p1.x - p2.x), abs(p1.y - p2.y)
        if (dx + dy) != 1:
            error_message = (
                "Клетки должны быть ортогональными соседями (без диагоналей)."
            )
            raise ValueError(error_message)
        if p1 == p2:
            error_message = "Нельзя связать клетку саму с собой (петля)."
            raise ValueError(error_message)
        self._adj[p1.x][p1.y].add(p2)
        self._adj[p2.x][p2.y].add(p1)

    def neighbors(self, p: Point) -> Iterable[Point]:
        """Возвращает соседние клетки, соединенные с данной."""
        return self._adj[p.x][p.y]

    def _create_terrain_distribution(
        self, probs: dict[Terrain, float]
    ) -> list[tuple[Terrain, float]]:
        import math

        cleaned: list[tuple[Terrain, float]] = []
        for terrain, weight in (probs or {}).items():
            if terrain is None or terrain == Terrain.FLOOR:
                continue
            try:
                weight_val = float(weight)
            except (ValueError, TypeError):
                weight_val = 0.0
            if not math.isfinite(weight_val) or weight_val <= 0.0:
                continue
            cleaned.append((terrain, weight_val))

        total_weight = sum(w for _, w in cleaned)

        if total_weight <= 0.0:
            return []

        dist: list[tuple[Terrain, float]] = []
        if total_weight > 1.0:
            for t, w in cleaned:
                dist.append((t, w / total_weight))
            floor_prob = 0.0
        else:
            for t, w in cleaned:
                dist.append((t, w))
            floor_prob = 1.0 - total_weight

        if floor_prob > 0.0:
            dist.append((Terrain.FLOOR, floor_prob))

        return dist

    def _create_cumulative_distribution(
        self, dist: list[tuple[Terrain, float]]
    ) -> list[tuple[float, Terrain]]:
        cumulative: list[tuple[float, Terrain]] = []
        acc = 0.0
        for t, p in dist:
            acc += p
            cumulative.append((acc, t))
        if cumulative:
            cumulative[-1] = (1.0, cumulative[-1][1])
        return cumulative

    def apply_random_terrain(
        self, probs: dict[Terrain, float], seed: int | None = None
    ) -> None:
        """Расставляет поверхности по клеткам согласно заданным вероятностям.

        Логика:
        - Используются только переданные веса для типов Terrain, КРОМЕ FLOOR.
        - Если сумма весов S <= 1.0, то FLOOR получает (1 - S).
        - Если сумма весов S > 1.0, то все переданные веса нормализуются так,
          чтобы сумма стала 1.0, FLOOR = 0.
        - Если ни одного положительного веса не передано (S == 0), ничего не делаем.
        """
        import random

        dist = self._create_terrain_distribution(probs)
        if not dist:
            return

        cumulative = self._create_cumulative_distribution(dist)
        rng = random.Random(seed)

        def sample() -> Terrain:
            r = rng.random()
            for c, t in cumulative:
                if r <= c:
                    return t
            return Terrain.FLOOR

        for y in range(self.height):
            for x in range(self.width):
                self._terrain[x][y] = sample()

    def to_ascii(
        self,
        start: Point | None = None,
        end: Point | None = None,
        path: Sequence[Point] | None = None,
    ) -> list[str]:
        """Преобразует лабиринт в ASCII представление."""
        if self.use_unicode:
            return self.to_grid(start, end, path, CellUnicode)
        return self.to_grid(start, end, path, CellType)

    def to_grid(
        self,
        start: Point | None = None,
        end: Point | None = None,
        path: Sequence[Point] | None = None,
        cell_enum: Enum = CellType,
    ) -> list[str]:
        """Преобразует лабиринт в текстовое представление.

        Args:
        ----
        start: Начальная точка (отображается как O или ◯)
        end: Конечная точка (отображается как X или ✔)
        path: Путь для отображения (точки отображаются как . или ·)
        cell_enum: Набор символов для отрисовки (CellType или CellUnicode)

        Returns:
        -------
        Список строк, представляющих лабиринт

        """
        wall = cell_enum.WALL.value
        empty = cell_enum.EMPTY.value
        path_char = cell_enum.PATH.value
        start_char = cell_enum.START.value
        end_char = cell_enum.END.value

        width, height = 2 * self.width + 1, 2 * self.height + 1
        canvas = [[wall for _ in range(width)] for _ in range(height)]

        for y in range(self.height):
            for x in range(self.width):
                cx, cy = 2 * x + 1, 2 * y + 1
                terrain_char = self._terrain[x][y].value
                canvas[cy][cx] = terrain_char

                for nb in self._adj[x][y]:
                    nx, ny = 2 * nb.x + 1, 2 * nb.y + 1
                    wx, wy = (cx + nx) // 2, (cy + ny) // 2
                    canvas[wy][wx] = empty

        self._place_path_elements(
            canvas, start, end, path, start_char, end_char, path_char
        )

        return ["".join(row) for row in canvas]

    def _place_path_elements(
        self,
        canvas: list[list[str]],
        start: Point | None,
        end: Point | None,
        path: Sequence[Point] | None,
        start_char: str,
        end_char: str,
        path_char: str,
    ) -> None:

        def place(p: Point, char: str) -> None:
            if self.in_bounds(p):
                canvas[2 * p.y + 1][2 * p.x + 1] = char

        if path:
            for p in path:
                place(p, path_char)

            for a, b in pairwise(path):
                my = (2 * a.y + 1 + 2 * b.y + 1) // 2
                mx = (2 * a.x + 1 + 2 * b.x + 1) // 2
                canvas[my][mx] = path_char

        if start:
            place(start, start_char)

        if end:
            place(end, end_char)

    @staticmethod
    def _validate_ascii_lines(lines: list[str]) -> tuple[int, int]:
        if not lines:
            error_message = "Лабиринт пуст."
            raise ValueError(error_message)

        width = len(lines[0])

        if any(len(r) != width for r in lines):
            error_message = "Строки ASCII-лабиринта должны иметь одинаковую длину."
            raise ValueError(error_message)
        if width % 2 == 0 or len(lines) % 2 == 0:
            error_message = "ASCII-лабиринт должен иметь нечетные размеры."
            raise ValueError(error_message)

        return (width - 1) // 2, (len(lines) - 1) // 2

    @staticmethod
    def _parse_terrain_from_char(ch: str) -> Terrain:
        for t in Terrain:
            if t.value == ch:
                return t
        return Terrain.FLOOR

    @staticmethod
    def _process_ascii_cell(
        maze: Maze, lines: list[str], x: int, y: int, passable_cell_chars: set[str]
    ) -> None:

        cx, cy = 2 * x + 1, 2 * y + 1
        ch = lines[cy][cx]

        if ch not in passable_cell_chars:
            return

        terrain = Maze._parse_terrain_from_char(ch)
        maze.set_terrain(Point(x, y), terrain)

        p = Point(x, y)

        if (
            x + 1 < maze.width
            and ch in passable_cell_chars
            and lines[cy][cx + 1] in passable_cell_chars
            and lines[cy][cx + 2] in passable_cell_chars
        ):
            maze.connect(p, Point(x + 1, y))

        if (
            y + 1 < maze.height
            and ch in passable_cell_chars
            and lines[cy + 1][cx] in passable_cell_chars
            and lines[cy + 2][cx] in passable_cell_chars
        ):
            maze.connect(p, Point(x, y + 1))

    @staticmethod
    def from_ascii(lines: list[str], *, use_unicode: bool = False) -> Maze:
        """Создает лабиринт из ASCII представления."""
        width, height = Maze._validate_ascii_lines(lines)
        maze = Maze(width=width, height=height, use_unicode=use_unicode)

        passable_cell_chars = {" ", "O", "X", ".", ":", "~", "=", "$"}

        for y in range(height):
            for x in range(width):
                Maze._process_ascii_cell(maze, lines, x, y, passable_cell_chars)

        return maze
