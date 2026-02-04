import random

from src.generators.generator import Generator
from src.generators.utils import add_loops
from src.maze import Maze, Point


class PrimGenerator(Generator):
    """Генератор лабиринта с использованием алгоритма Прима."""

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

        start = Point(rng.randrange(width), rng.randrange(height))
        in_maze = [[False] * height for _ in range(width)]
        in_maze[start.x][start.y] = True

        frontier: list[tuple[Point, Point]] = []

        def add_frontier(p: Point) -> None:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = Point(p.x + dx, p.y + dy)
                if maze.in_bounds(q) and not in_maze[q.x][q.y]:
                    frontier.append((p, q))

        add_frontier(start)

        while frontier:
            i = rng.randrange(len(frontier))
            a, b = frontier.pop(i)
            if in_maze[a.x][a.y] and in_maze[b.x][b.y]:
                continue
            maze.connect(a, b)
            new_cell = b if not in_maze[b.x][b.y] else a
            in_maze[new_cell.x][new_cell.y] = True
            add_frontier(new_cell)

        for y in range(height):
            for x in range(width):
                p = Point(x, y)
                if not maze.neighbors(p):
                    candidates = [
                        Point(nx, ny)
                        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
                        if 0 <= nx < width
                        and 0 <= ny < height
                        and maze.neighbors(Point(nx, ny))
                    ]
                    if candidates:
                        maze.connect(p, rng.choice(candidates))

        add_loops(maze, ratio=0.15, seed=seed, prefer_dead_ends=True)
        return maze
