import pytest

from src.generators import GEN_ALGOS
from src.generators.generator import Generator
from src.maze import Point


@pytest.mark.parametrize("algo", list(GEN_ALGOS.keys()))
@pytest.mark.parametrize(("width", "height"), [(5, 5), (10, 10), (3, 3)])
def test_generate_maze(algo: Generator, width: int, height: int) -> None:
    """Проверяет генерацию лабиринтов разных размеров различными алгоритмами."""
    maze = GEN_ALGOS[algo].generate(width, height)
    assert maze.width == width
    assert maze.height == height


def test_generate_maze_invalid_dimensions() -> None:
    """Проверяет обработку невалидных размеров лабиринта."""
    with pytest.raises(
        ValueError, match="Размеры лабиринта должны быть положительными."
    ):
        GEN_ALGOS["dfs"].generate(0, 5)
    with pytest.raises(
        ValueError, match="Размеры лабиринта должны быть положительными."
    ):
        GEN_ALGOS["dfs"].generate(-1, 3)


@pytest.mark.parametrize("algo", list(GEN_ALGOS.keys()))
def test_generate_maze_with_seed(algo: Generator) -> None:
    """Проверяет детерминированность генерации при использовании seed."""
    generator = GEN_ALGOS[algo]
    maze1 = generator.generate(5, 5, seed=42)
    maze2 = generator.generate(5, 5, seed=42)

    assert maze1.to_ascii() == maze2.to_ascii()


def test_generate_maze_with_minimal_size() -> None:
    """Проверяет генерацию лабиринта минимального размера."""
    generator = GEN_ALGOS["dfs"]
    maze = generator.generate(1, 1)
    assert maze.width == 1
    assert maze.height == 1

    assert len(list(maze.neighbors(Point(0, 0)))) == 0
