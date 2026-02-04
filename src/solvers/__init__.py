from .astar_solver import AStarSolver
from .bfs_solver import BFSSolver
from .djikstra_solver import DijkstraSolver
from .greedy_solver import GreedySolver

SOLVE_ALGOS = {
    "dijkstra": DijkstraSolver(),
    "astar": AStarSolver(),
    "bfs": BFSSolver(),
    "greedy": GreedySolver(),
}
