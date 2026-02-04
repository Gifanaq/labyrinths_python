from src.maze import Maze, Point


def test_to_ascii_renders_maze_with_start_end_and_path() -> None:
    """Проверяет корректность отрисовки лабиринта с началом, концом и путем."""
    maze = Maze(2, 2)
    path = [Point(0, 0), Point(1, 0), Point(1, 1)]

    maze.connect(Point(0, 0), Point(1, 0))
    maze.connect(Point(0, 0), Point(0, 1))
    maze.connect(Point(1, 0), Point(1, 1))
    maze.connect(Point(0, 1), Point(1, 1))

    output = maze.to_ascii(start=path[0], end=path[-1], path=path)

    assert output == [
        "#####",
        "#O..#",
        "# #.#",
        "#  X#",
        "#####",
    ]
