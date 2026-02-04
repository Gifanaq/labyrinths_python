import heapq

from src.maze import Maze, Point
from src.solvers.solver import Solver
from src.solvers.utils import reconstruct_path


class DijkstraSolver(Solver):
    """Решатель лабиринта с использованием алгоритма Дейкстры."""

    def solve(self, maze: Maze, start: Point, end: Point) -> list[Point]:
        """Решает задачу поиска пути в лабиринте с использованием алгоритма Дейкстры.

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

        dist: dict[Point, float] = {start: 0.0}
        pq: list[tuple[float, Point]] = [(0.0, start)]
        came_from: dict[Point, Point] = {}
        visited: set[Point] = set()

        while pq:
            d, u = heapq.heappop(pq)

            if u in visited:
                continue
            visited.add(u)

            if u == end:
                return reconstruct_path(came_from, u)

            for v in maze.neighbors(u):
                if v in visited:
                    continue
                nd = d + maze.step_cost(u, v)
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    came_from[v] = u
                    heapq.heappush(pq, (nd, v))

        return []
