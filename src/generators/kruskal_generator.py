import random

from src.generators.generator import Generator
from src.generators.utils import add_loops
from src.maze import Maze, Point


class UnionFind:
    """Структура данных для объединения непересекающихся множеств."""

    def __init__(self, points: list[Point]) -> None:
        self.parent = {p: p for p in points}

    def find(self, a: Point) -> Point:
        """Находит корневой элемент для точки.

        Args:
        ----
            a: Точка для поиска корня

        Returns:
        -------
            Корневая точка

        """
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a: Point, b: Point) -> bool:
        """Объединяет множества, содержащие точки a и b.

        Args:
        ----
            a: Первая точка
            b: Вторая точка

        Returns:
        -------
            True если множества были объединены, False если уже были в одном множестве

        """
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[rb] = ra
        return True


class KruskalGenerator(Generator):
    """Генератор лабиринта с использованием алгоритма Краскала."""

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

        points = [Point(x, y) for x in range(width) for y in range(height)]
        uf = UnionFind(points)

        edges: list[tuple[Point, Point]] = []
        for y in range(height):
            for x in range(width):
                p = Point(x, y)
                if x + 1 < width:
                    edges.append((p, Point(x + 1, y)))
                if y + 1 < height:
                    edges.append((p, Point(x, y + 1)))

        rng.shuffle(edges)
        for a, b in edges:
            if uf.union(a, b):
                maze.connect(a, b)

        add_loops(maze, ratio=0.15, seed=seed, prefer_dead_ends=True)
        return maze
