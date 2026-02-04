import heapq

from src.maze import Maze, Point
from src.solvers.solver import Solver
from src.solvers.utils import manhattan, reconstruct_path


class GreedySolver(Solver):
    """Решатель лабиринта с использованием жадного алгоритма."""

    def solve(self, maze: Maze, start: Point, end: Point) -> list[Point]:
        """Решает задачу поиска пути в лабиринте с использованием жадного алгоритма.

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

        pq: list[tuple[int, Point]] = [(manhattan(start, end), start)]
        came_from: dict[Point, Point] = {}
        seen: set[Point] = {start}

        while pq:
            _, u = heapq.heappop(pq)

            if u == end:
                return reconstruct_path(came_from, u)

            for v in maze.neighbors(u):
                if v in seen:
                    continue

                seen.add(v)
                came_from[v] = u
                heapq.heappush(pq, (manhattan(v, end), v))

        return []
