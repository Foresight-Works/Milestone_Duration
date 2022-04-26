import networkx as nx
import numpy as np
import sys
modules_path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_path not in sys.path: sys.path.append(modules_path)
from vizz import *
G = nx.path_graph(5)
node_pairs = [(1, 5), (5, 6), (6, 7), (2, 8), (8, 9), (9, 10)]
G.add_edges_from(node_pairs)
#draw_graph(G)
# T = nx.dfs_tree(G, source=0)
# T1_edges = list(T.edges())
# print(T1_edges)
