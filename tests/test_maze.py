import pytest

from src.maze import Maze, Point, Terrain

NEIGHBOR_COUNT = 2
COST_COIN = 0.2
EXPECTED_WIDTH = 2
EXPECTED_HEIGHT = 1


def test_maze_with_invalid_size() -> None:
    """Проверяет создание лабиринта с невалидными размерами."""
    with pytest.raises(
        ValueError, match="Размеры лабиринта должны быть положительными."
    ):
        Maze(0, 5)

    with pytest.raises(
        ValueError, match="Размеры лабиринта должны быть положительными."
    ):
        Maze(-1, 3)


def test_neighbors_for_valid_points() -> None:
    """Проверяет получение соседей для соединенных точек."""
    maze = Maze(3, 3)

    maze.connect(Point(0, 0), Point(1, 0))
    maze.connect(Point(1, 0), Point(1, 1))

    neighbors = list(maze.neighbors(Point(0, 0)))
    assert len(neighbors) == 1
    assert neighbors[0] == Point(1, 0)

    neighbors = list(maze.neighbors(Point(1, 0)))
    assert len(neighbors) == NEIGHBOR_COUNT
    assert Point(0, 0) in neighbors
    assert Point(1, 1) in neighbors


def test_maze_from_invalid_ascii() -> None:
    """Проверяет создание лабиринта из невалидного ASCII представления."""
    with pytest.raises(
        ValueError, match="Строки ASCII-лабиринта должны иметь одинаковую длину."
    ):
        Maze.from_ascii(["###", "##"])

    with pytest.raises(
        ValueError, match="ASCII-лабиринт должен иметь нечетные размеры"
    ):
        Maze.from_ascii(["####", "####", "####"])


def test_connect_invalid_cases() -> None:
    """Проверяет обработку невалидных соединений точек."""
    maze = Maze(2, 2)

    with pytest.raises(
        ValueError, match="Нельзя соединять клетки вне границ лабиринта."
    ):
        maze.connect(Point(-1, 0), Point(0, 0))

    with pytest.raises(
        ValueError,
        match="Клетки должны быть ортогональными соседями \\(без диагоналей\\).",
    ):
        maze.connect(Point(0, 0), Point(1, 1))

    with pytest.raises(
        ValueError,
        match="Клетки должны быть ортогональными соседями \\(без диагоналей\\).",
    ):
        maze.connect(Point(0, 0), Point(0, 0))


def test_to_ascii_renders_path_and_markers() -> None:
    """Проверяет отрисовку пути и маркеров в ASCII представлении."""
    maze = Maze(2, 2)
    maze.connect(Point(0, 0), Point(1, 0))
    maze.connect(Point(1, 0), Point(1, 1))

    path = [Point(0, 0), Point(1, 0), Point(1, 1)]
    ascii_rows = maze.to_ascii(start=Point(0, 0), end=Point(1, 1), path=path)

    assert ascii_rows[1][1] == "O"
    assert ascii_rows[3][3] == "X"
    assert ascii_rows[1][2] == "."
    assert ascii_rows[2][3] == "."


def test_apply_random_terrain_without_floor_when_weights_exceed_one() -> None:
    """Проверяет распределение terrain при весах, превышающих 1.0."""
    maze = Maze(3, 3)
    maze.apply_random_terrain({Terrain.SAND: 2.0, Terrain.MUD: 1.5}, seed=3)

    terrains = {
        maze.get_terrain(Point(x, y))
        for x in range(maze.width)
        for y in range(maze.height)
    }

    assert Terrain.FLOOR not in terrains
    assert Terrain.SAND in terrains
    assert Terrain.MUD in terrains


def test_apply_random_terrain_includes_floor_when_weights_under_one() -> None:
    """Проверяет распределение terrain при весах меньше 1.0."""
    maze = Maze(3, 3)
    maze.apply_random_terrain({Terrain.SAND: 0.25}, seed=1)

    terrains = {
        maze.get_terrain(Point(x, y))
        for x in range(maze.width)
        for y in range(maze.height)
    }

    assert Terrain.FLOOR in terrains
    assert Terrain.SAND in terrains


def test_from_ascii_restores_connections_and_terrain() -> None:
    """Проверяет восстановление соединений и terrain из ASCII представления."""
    source = Maze(2, 1)
    source.set_terrain(Point(0, 0), Terrain.COIN)
    source.connect(Point(0, 0), Point(1, 0))

    ascii_rows = source.to_ascii()
    restored = Maze.from_ascii(ascii_rows, use_unicode=True)

    assert restored.use_unicode is True
    assert restored.width == EXPECTED_WIDTH
    assert restored.height == EXPECTED_HEIGHT
    assert restored.get_terrain(Point(0, 0)) == Terrain.COIN
    assert restored.get_terrain(Point(1, 0)) == Terrain.FLOOR
    assert list(restored.neighbors(Point(0, 0))) == [Point(1, 0)]


def test_step_cost_uses_destination_terrain() -> None:
    """Проверяет расчет стоимости шага с учетом terrain точки назначения."""
    maze = Maze(2, 1)
    maze.set_terrain(Point(0, 0), Terrain.MUD)
    maze.set_terrain(Point(1, 0), Terrain.COIN)

    assert maze.step_cost(Point(0, 0), Point(1, 0)) == COST_COIN
