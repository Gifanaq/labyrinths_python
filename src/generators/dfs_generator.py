import random

from src.generators.generator import Generator
from src.generators.utils import add_loops
from src.maze import Maze, Point


class DFSGenerator(Generator):
    """Генератор лабиринта с использованием алгоритма поиска в глубину."""

    def generate(
        self,
        width: int,
        height: int,
        *,
        use_unicode: bool | None = False,
        seed: int | None = None,
    ) -> Maze:
        """Генерирует лабиринт заданного размера.

        Args:
        ----
            width: Ширина лабиринта
            height: Высота лабиринта
            use_unicode: Использовать Unicode символы
            seed: Seed для RNG

        Returns:
        -------
            Сгенерированный лабиринт

        """
        rng = random.Random(seed)
        maze = Maze(width=width, height=height, use_unicode=use_unicode)
        visited = [[False] * height for _ in range(width)]
        stack: list[Point] = [Point(0, 0)]
        visited[0][0] = True

        def unvisited_neighbors(p: Point) -> list[Point]:
            res = []

            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = Point(p.x + dx, p.y + dy)
                if maze.in_bounds(q) and not visited[q.x][q.y]:
                    res.append(q)

            return res

        while stack:
            cur = stack[-1]
            nbrs = unvisited_neighbors(cur)
            if not nbrs:
                stack.pop()
                continue
            nxt = rng.choice(nbrs)
            maze.connect(cur, nxt)
            visited[nxt.x][nxt.y] = True
            stack.append(nxt)

        add_loops(maze, ratio=0.15, seed=seed, prefer_dead_ends=True)
        return maze
