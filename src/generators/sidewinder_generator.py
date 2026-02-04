import random

from src.generators.generator import Generator
from src.generators.utils import add_loops
from src.maze import Maze, Point

CARVING_PROBABILITY = 0.5


class SidewinderGenerator(Generator):
    """Генератор лабиринта с использованием алгоритма Sidewinder."""

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

        for y in range(height):
            run: list[Point] = []
            for x in range(width):
                p = Point(x, y)
                run.append(p)
                carve_east = (x + 1 < width) and (
                    y == 0 or rng.random() < CARVING_PROBABILITY
                )

                if carve_east:
                    maze.connect(p, Point(x + 1, y))
                else:
                    member = rng.choice(run)
                    if y > 0:
                        maze.connect(member, Point(member.x, y - 1))
                    run = []

        add_loops(maze, ratio=0.15, seed=seed, prefer_dead_ends=True)
        return maze
