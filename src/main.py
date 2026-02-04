from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

from src.config import HELP_MESSAGE, VERSION
from src.generators import GEN_ALGOS
from src.io_utils import read_lines, write_lines
from src.maze import Maze, Point, Terrain
from src.solvers import SOLVE_ALGOS

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s", force=True
)
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def _require(value: object, name: str) -> object:
    if value is None:
        message = f"Аргумент --{name} обязателен для данной команды."
        raise SystemExit(message)
    return value


def _validate_generate_args(
    args: argparse.Namespace,
) -> tuple[str, int, int]:

    algo = _require(args.algorithm, "algorithm")
    if algo not in GEN_ALGOS:
        message = (
            f"Алгоритм генерации лабиринта должен быть одним из: "
            f"{', '.join(GEN_ALGOS)}"
        )
        raise SystemExit(message)
    w = _require(args.width, "width")
    h = _require(args.height, "height")
    if w <= 0 or h <= 0:
        message = "Поля width и height должны иметь положительные значения."
        raise SystemExit(message)
    return algo, w, h


def _validate_solve_args(
    args: argparse.Namespace, maze: Maze
) -> tuple[str, Point, Point]:
    algo = _require(args.algorithm, "algorithm")
    if algo not in SOLVE_ALGOS:
        message = (
            f"Алгоритм решения лабиринта должен быть одним из: "
            f"{', '.join(SOLVE_ALGOS)}"
        )
        raise SystemExit(message)

    start = _parse_point(_require(args.start, "start"))
    end = _parse_point(_require(args.end, "end"))

    _check_bounds(maze, start, end)

    return algo, start, end


def _parse_terrain_prob(s: str | None) -> dict[Terrain, float]:
    if not s:
        return {}

    mapping: dict[Terrain, float] = {}
    for part in s.split(","):
        if not part.strip():
            continue
        k, v = part.split("=", 1)
        k = k.strip().lower()
        v = float(v.strip())
        name_map = {
            "floor": Terrain.FLOOR,
            "sand": Terrain.SAND,
            "mud": Terrain.MUD,
            "road": Terrain.ROAD,
            "coin": Terrain.COIN,
            "песок": Terrain.SAND,
            "болото": Terrain.MUD,
            "монетки": Terrain.COIN,
            "покрытие": Terrain.ROAD,
        }

        if k not in name_map:
            available = ", ".join([k for k, _ in enumerate(name_map)])
            message = f"Неизвестная поверхность: {k}. Доступны: {available}"
            raise SystemExit(message)
        mapping[name_map[k]] = v
    return mapping


def _parse_point(raw: str) -> Point:
    try:
        return Point.parse(raw)
    except ValueError as exc:
        message = f"Некорректная точка: {exc}"
        raise SystemExit(message) from exc


def _check_bounds(maze: Maze, start: Point, end: Point) -> None:
    if not maze.in_bounds(start) or not maze.in_bounds(end):
        message = "Одна или обе точки вне границ лабиринта."
        raise SystemExit(message)


def run_generate(args: argparse.Namespace) -> None:
    """Обрабатывает команду генерации лабиринта."""
    algo, w, h = _validate_generate_args(args)
    maze = GEN_ALGOS[algo].generate(w, h, use_unicode=args.unicode, seed=args.seed)
    probs = _parse_terrain_prob(args.terrain_prob)
    if probs:
        maze.apply_random_terrain(probs, seed=args.seed)
    lines = maze.to_ascii()
    write_lines(lines, args.output)
    print(f"INFO:__main__:Лабиринт [{w} x {h}] сгенерирован с помощью {algo}.", end="")


def run_solve(args: argparse.Namespace) -> None:
    """Обрабатывает команду решения лабиринта."""
    file = _require(args.file, "file")
    lines = read_lines(file)
    maze = Maze.from_ascii(lines, use_unicode=args.unicode)
    algo, start, end = _validate_solve_args(args, maze)
    path = SOLVE_ALGOS[algo].solve(maze, start, end)
    out = maze.to_ascii(start, end, path if path else None)
    write_lines(out, args.output)
    if not path:
        logger.warning("Путь для записи файла не найден.")


def _print_help() -> None:
    print(HELP_MESSAGE)


def _print_version() -> None:
    print(VERSION)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="maze-app", add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-V", "--version", action="store_true")
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser(
        "generate", help="Generate a maze with specified algorithm and dimensions."
    )
    gen_parser.add_argument(
        "--algorithm", type=str, choices=list(GEN_ALGOS.keys()), required=True
    )
    gen_parser.add_argument("--width", type=int, required=True)
    gen_parser.add_argument("--height", type=int, required=True)
    gen_parser.add_argument("--output", type=str, default=None)
    gen_parser.add_argument("--unicode", action="store_true")
    gen_parser.add_argument("--seed", type=int, default=None, help="Seed RNG.")
    gen_parser.add_argument(
        "--terrain-prob",
        type=str,
        default=None,
        help="Вероятности поверхностей, формат: 'mud=0.2,sand=0.1,road=0.05,coin=0.02'",
    )

    solve_parser = subparsers.add_parser(
        "solve", help="Solve a maze with specified algorithm and points."
    )
    solve_parser.add_argument(
        "--algorithm", type=str, choices=list(SOLVE_ALGOS.keys()), required=True
    )
    solve_parser.add_argument("--file", type=str, required=True)
    solve_parser.add_argument("--start", type=str, required=True)
    solve_parser.add_argument("--end", type=str, required=True)
    solve_parser.add_argument("--output", type=str, default=None)
    solve_parser.add_argument("--unicode", action="store_true")

    return parser


def _parse_args(
    argv: Sequence[str] | None = None,
) -> argparse.Namespace:

    parser = _build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "help", False):
        _print_help()
        raise SystemExit(0)

    if getattr(args, "version", False):
        _print_version()
        raise SystemExit(0)

    if getattr(args, "command", None) is None:
        _print_help()
        raise SystemExit(1)

    return args


def main(argv: Sequence[str] | None = None) -> None:
    """Основная функция приложения.

    Args:
    ----
        argv: Аргументы командной строки

    """
    args = _parse_args(argv)

    if args.command == "generate":
        run_generate(args)
    elif args.command == "solve":
        run_solve(args)
    else:
        msg = "Неизвестная команда. Используйте: generate/solve."
        raise SystemExit(msg)


if __name__ == "__main__":
    main()
