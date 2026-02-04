from .dfs_generator import DFSGenerator
from .kruskal_generator import KruskalGenerator
from .prima_generator import PrimGenerator
from .sidewinder_generator import SidewinderGenerator

GEN_ALGOS = {
    "dfs": DFSGenerator(),
    "prim": PrimGenerator(),
    "sidewinder": SidewinderGenerator(),
    "kruskal": KruskalGenerator(),
}
