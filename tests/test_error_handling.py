from pathlib import Path

import pytest

from src.io_utils import read_lines
from src.maze import Maze, Point
from src.solvers.djikstra_solver import DijkstraSolver


def test_read_lines_missing_file(tmp_path: Path) -> None:
    """Проверяет обработку ошибки при чтении несуществующего файла."""
    missing = tmp_path / "absent.txt"

    with pytest.raises(FileNotFoundError):
        read_lines(str(missing))


def test_maze_from_ascii_rejects_invalid_input() -> None:
    """Проверяет валидацию входных данных при создании лабиринта из ASCII."""
    with pytest.raises(ValueError, match="Лабиринт пуст."):
        Maze.from_ascii([])

    with pytest.raises(
        ValueError, match="Строки ASCII-лабиринта должны иметь одинаковую длину"
    ):
        Maze.from_ascii(["###", "##"])


def test_point_parse_validation() -> None:
    """Проверяет валидацию парсинга координат точки."""
    with pytest.raises(
        ValueError,
        match="Координаты должны быть в формате x,y где x и y - целые числа.",
    ):
        Point.parse("1;2")

    with pytest.raises(ValueError, match="Координаты должны быть больше нуля."):
        Point.parse("-1,2")


def test_solver_invalid_start_end() -> None:
    """Проверяет обработку невалидных начальной и конечной точек в решателе."""
    maze = Maze(3, 3)
    solver = DijkstraSolver()

    with pytest.raises(ValueError, match="Старт/Финиш вне границ лабиринта."):
        solver.solve(maze, Point(4, 4), Point(2, 2))

    with pytest.raises(ValueError, match="Старт/Финиш вне границ лабиринта."):
        solver.solve(maze, Point(0, 0), Point(4, 4))
