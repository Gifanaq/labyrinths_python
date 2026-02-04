from itertools import pairwise

from src.maze import TERRAIN_COST, Maze, Point, Terrain
from src.solvers.astar_solver import AStarSolver
from src.solvers.djikstra_solver import DijkstraSolver

EPSILON = 1e-9
EXPECTED_STEPS = 4
EXPECTED_COST = 4.0


def path_cost(maze: Maze, path: list[Point]) -> float:
    """Вычисляет общую стоимость пути в лабиринте.

    Args:
    ----
        maze: Лабиринт с определенными стоимостями terrain
        path: Список точек, представляющих путь

    Returns:
    -------
        Общая стоимость пути или бесконечность если путь пустой

    """
    if not path:
        return float("inf")
    total = 0.0
    for a, b in pairwise(path):
        total += maze.step_cost(a, b)
    return total


def build_maze_for_choice() -> Maze:
    """Создает тестовый лабиринт с разными типами terrain для проверки выбора пути.

    Returns
    -------
        Лабиринт с альтернативными путями разной стоимости

    """
    maze = Maze(3, 2, use_unicode=False)

    maze.connect(Point(0, 0), Point(1, 0))
    maze.connect(Point(1, 0), Point(2, 0))

    maze.connect(Point(0, 0), Point(0, 1))
    maze.connect(Point(0, 1), Point(1, 1))
    maze.connect(Point(1, 1), Point(2, 1))
    maze.connect(Point(2, 1), Point(2, 0))

    maze.set_terrain(Point(1, 0), Terrain.MUD)
    maze.set_terrain(Point(2, 0), Terrain.FLOOR)

    maze.set_terrain(Point(0, 1), Terrain.ROAD)
    maze.set_terrain(Point(1, 1), Terrain.COIN)
    maze.set_terrain(Point(2, 1), Terrain.ROAD)

    maze.set_terrain(Point(0, 0), Terrain.FLOOR)

    return maze


def test_astar_prefers_cheaper_route_even_if_longer() -> None:
    """Проверяет, что A* выбирает более дешевый путь даже если он длиннее."""
    maze = build_maze_for_choice()
    start, end = Point(0, 0), Point(2, 0)

    solver = AStarSolver()
    path = solver.solve(maze, start, end)

    assert path, "Путь должен находиться"
    cost = path_cost(maze, path)

    assert Point(1, 1) in path, "Маршрут должен проходить через монетку (COIN)."
    assert Point(1, 0) not in path, "Маршрут не должен идти через болото (MUD)."

    expensive = TERRAIN_COST[Terrain.MUD] + TERRAIN_COST[Terrain.FLOOR]
    assert expensive == 3.0 + 1.0

    cheap = (
        TERRAIN_COST[Terrain.ROAD]
        + TERRAIN_COST[Terrain.COIN]
        + TERRAIN_COST[Terrain.ROAD]
        + TERRAIN_COST[Terrain.FLOOR]
    )
    assert abs(cheap - 2.4) < EPSILON

    assert (
        cost < expensive
    ), f"Должно быть дешевле короткой дороги по грязи: {cost=}, {expensive=}"


def test_dijkstra_agrees_with_astar_on_cost() -> None:
    """Проверяет, что Дейкстра и A* находят пути одинаковой стоимости."""
    maze = build_maze_for_choice()
    start, end = Point(0, 0), Point(2, 0)

    astar = AStarSolver().solve(maze, start, end)
    dijk = DijkstraSolver().solve(maze, start, end)

    cost_a = path_cost(maze, astar)
    cost_d = path_cost(maze, dijk)

    assert (
        abs(cost_a - cost_d) < EPSILON
    ), f"A* и Дейкстра должны совпадать по стоимости: {cost_a} vs {cost_d}"

    assert Point(1, 1) in astar
    assert Point(1, 1) in dijk
    assert Point(1, 0) not in astar
    assert Point(1, 0) not in dijk


def test_longer_but_cheaper_explicit_numbers() -> None:
    """Проверяет явные числовые значения для длинного но дешевого пути."""
    maze = build_maze_for_choice()
    start, end = Point(0, 0), Point(2, 0)

    dijk_path = DijkstraSolver().solve(maze, start, end)

    steps = len(dijk_path) - 1
    cost = path_cost(maze, dijk_path)

    assert steps == EXPECTED_STEPS, f"Ожидаем длинный путь (4 шага), получили {steps}"
    assert (
        cost < EXPECTED_COST
    ), "Ожидаем, что длинный путь дешевле короткого сверху (4.0)"
