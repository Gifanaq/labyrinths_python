import random

from src.maze import Maze, Point


def get_score(a: Point, b: Point, maze: Maze, *, prefer_dead_ends: bool = True) -> int:
    """Вычисляет оценку для потенциального соединения клеток.

    Args:
    ----
        a: Первая точка
        b: Вторая точка
        maze: Лабиринт
        prefer_dead_ends: Предпочитать тупиковые клетки

    Returns:
    -------
        Оценка соединения

    """
    score = 0
    if prefer_dead_ends:
        deg_a = len(list(maze.neighbors(a)))
        deg_b = len(list(maze.neighbors(b)))
        score = (1 if deg_a == 1 else 0) + (1 if deg_b == 1 else 0)
    return score


def add_loops(
    maze: Maze,
    ratio: float = 0.2,
    seed: int | None = None,
    *,
    prefer_dead_ends: bool = True,
) -> None:
    """Добавляет дополнительные соединения в лабиринт.

    Args:
    ----
        maze: Лабиринт для модификации
        ratio: Доля возможных соединений для добавления
        seed: Seed для RNG
        prefer_dead_ends: Предпочитать соединения с тупиковыми клетками

    """
    if ratio <= 0.0:
        return

    rng = random.Random(seed)
    w, h = maze.width, maze.height

    candidates: list[tuple[int, Point, Point]] = []
    for y in range(h):
        for x in range(w):
            a = Point(x, y)
            for dx, dy in ((1, 0), (0, 1)):
                b = Point(x + dx, y + dy)
                if not maze.in_bounds(b):
                    continue

                if b not in maze.neighbors(a):
                    score = get_score(a, b, maze, prefer_dead_ends=prefer_dead_ends)
                    candidates.append((score, a, b))

    if not candidates:
        return

    k = int(len(candidates) * min(1.0, max(0.0, ratio)))
    if k <= 0:
        return

    candidates.sort(key=lambda t: t[0], reverse=True)
    band = candidates[: max(k * 2, k)]
    rng.shuffle(band)
    pick = band[:k]

    for _, a, b in pick:
        maze.connect(a, b)
