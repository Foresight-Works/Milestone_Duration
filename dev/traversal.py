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
T = nx.dfs_tree(G, source=0)
T1_edges = list(T.edges())
print('dfs tree edgs:', T1_edges)

T = nx.dfs_predecessors(G, source=0)
#T1_edges = list(T.edges())
print('dfs predecessors:', T)

print('all_simple_paths')
for path in nx.all_simple_paths(G, source=0, target=3):
    print(path)


#draw_graph(T)