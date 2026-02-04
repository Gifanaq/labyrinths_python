from src.maze import Point


def reconstruct_path(came_from: dict[Point, Point], cur: Point) -> list[Point]:
    """Восстанавливает путь из словаря предков.

    Args:
    ----
        came_from: Словарь, связывающий каждую точку с её предком
        cur: Конечная точка пути

    Returns:
    -------
        Восстановленный путь от начальной точки до cur

    """
    path: list[Point] = [cur]

    while cur in came_from:
        cur = came_from[cur]
        path.append(cur)

    path.reverse()
    return path


def manhattan(a: Point, b: Point) -> int:
    """Вычисляет манхэттенское расстояние между двумя точками.

    Args:
    ----
        a: Первая точка
        b: Вторая точка

    Returns:
    -------
        Манхэттенское расстояние

    """
    return abs(a.x - b.x) + abs(a.y - b.y)
