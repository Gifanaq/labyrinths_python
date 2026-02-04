from collections import deque

from src.maze import Maze, Point
from src.solvers.solver import Solver
from src.solvers.utils import reconstruct_path


class BFSSolver(Solver):
    """Решатель лабиринта с использованием алгоритма поиска в ширину (BFS)."""

    def solve(self, maze: Maze, start: Point, end: Point) -> list[Point]:
        """Решает задачу поиска пути в лабиринте с использованием BFS.

        Args:
        ----
            maze: Лабиринт, в котором необходимо найти путь
            start: Начальная точка
            end: Конечная точка

        Returns:
        -------
            Список точек, представляющих путь от start до end

        Raises:
        ------
            ValueError: Если старт или финиш вне границ лабиринта

        """
        error_message = "Старт/Финиш вне границ лабиринта."
        if not (maze.in_bounds(start) and maze.in_bounds(end)):
            raise ValueError(error_message)

        q = deque([start])
        came_from: dict[Point, Point] = {}
        seen = {start}

        while q:
            u = q.popleft()

            if u == end:
                return reconstruct_path(came_from, u)

            for v in maze.neighbors(u):
                if v not in seen:
                    seen.add(v)
                    came_from[v] = u
                    q.append(v)

        return []
