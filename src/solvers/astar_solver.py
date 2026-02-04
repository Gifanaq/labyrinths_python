import heapq

from src.maze import Maze, Point
from src.solvers.solver import Solver
from src.solvers.utils import manhattan, reconstruct_path


class AStarSolver(Solver):
    """Решатель лабиринта с использованием алгоритма A*."""

    def solve(self, maze: Maze, start: Point, end: Point) -> list[Point]:
        """Решает задачу поиска пути в лабиринте с использованием алгоритма A*.

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

        g: dict[Point, float] = {start: 0.0}

        min_step = min([1.0, 0.2, 0.6, 2.0, 3.0])
        f: dict[Point, float] = {start: manhattan(start, end) * min_step}

        pq: list[tuple[float, float, Point]] = [(f[start], 0, start)]
        came_from: dict[Point, Point] = {}
        visited: set[Point] = set()

        while pq:
            _, _, u = heapq.heappop(pq)

            if u in visited:
                continue
            visited.add(u)

            if u == end:
                return reconstruct_path(came_from, u)

            for v in maze.neighbors(u):
                if v in visited:
                    continue

                tentative = g[u] + maze.step_cost(u, v)
                if tentative < g.get(v, float("inf")):
                    came_from[v] = u
                    g[v] = tentative
                    f[v] = tentative + manhattan(v, end) * min_step
                    heapq.heappush(pq, (f[v], tentative, v))

        return []
