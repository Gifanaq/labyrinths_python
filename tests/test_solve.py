from collections import deque
from itertools import pairwise

import pytest

from src.maze import Maze, Point
from src.solvers.astar_solver import AStarSolver
from src.solvers.bfs_solver import BFSSolver
from src.solvers.djikstra_solver import DijkstraSolver
from src.solvers.greedy_solver import GreedySolver
from src.solvers.solver import Solver


@pytest.mark.parametrize(
    "solver",
    [DijkstraSolver(), AStarSolver(), BFSSolver(), GreedySolver()],
)
def test_solver_finds_path_in_known_maze(solver: Solver) -> None:
    """Проверяет, что все решатели находят путь в заранее известном лабиринте."""
    maze = Maze(3, 3)
    expected_path = [
        Point(0, 0),
        Point(1, 0),
        Point(1, 1),
        Point(2, 1),
        Point(2, 2),
    ]

    for start, end in pairwise(expected_path):
        maze.connect(start, end)

    result = solver.solve(maze, expected_path[0], expected_path[-1])

    assert result == expected_path


def _shortest_distance(maze: Maze, start: Point, end: Point) -> int:
    """Вычисляет кратчайшее расстояние между точками с помощью BFS.

    Args:
    ----
        maze: Лабиринт для поиска
        start: Начальная точка
        end: Конечная точка

    Returns:
    -------
        Кратчайшее расстояние в шагах

    """
    queue = deque([(start, 0)])
    seen = {start}

    while queue:
        current, dist = queue.popleft()

        if current == end:
            return dist

        for neighbor in maze.neighbors(current):
            if neighbor in seen:
                continue
            seen.add(neighbor)
            queue.append((neighbor, dist + 1))

    error_message = "Путь между указанными клетками не найден."
    raise AssertionError(error_message)


def test_solvers_return_optimal_paths_with_multiple_routes() -> None:
    """Проверяет, что решатели находят оптимальные пути."""
    maze = Maze(3, 3)
    edges = [
        (Point(0, 0), Point(1, 0)),
        (Point(1, 0), Point(2, 0)),
        (Point(2, 0), Point(2, 1)),
        (Point(1, 0), Point(1, 1)),
        (Point(1, 1), Point(2, 1)),
        (Point(0, 0), Point(0, 1)),
        (Point(0, 1), Point(0, 2)),
        (Point(0, 2), Point(1, 2)),
        (Point(1, 2), Point(2, 2)),
        (Point(1, 1), Point(1, 2)),
        (Point(2, 1), Point(2, 2)),
    ]

    for a, b in edges:
        maze.connect(a, b)

    start = Point(0, 0)
    end = Point(2, 2)

    optimal_length = _shortest_distance(maze, start, end)

    for solver in (DijkstraSolver(), AStarSolver()):
        path = solver.solve(maze, start, end)

        assert path, "Решатель вернул пустой путь."
        assert path[0] == start
        assert path[-1] == end
        assert len(path) - 1 == optimal_length
