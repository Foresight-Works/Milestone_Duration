import numpy as np
from itertools import combinations
import networkx as nx
import sys
modules_path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_path not in sys.path: sys.path.append(modules_path)
from vizz import draw_graph

# Fully connected graph
G = nx.Graph()
node_ids = np.arange(10)
node_pairs = list(set(combinations(node_ids, 2)))
G.add_edges_from(node_pairs)
nx.write_adjlist(G, "./data/fully_connected_graph.adjlist")
# draw_graph(G)

# list_connected_nodes test graph
import networkx as nx
G = nx.Graph()
G.add_edge('a', 'b', weight=1)
G.add_edge('a', 'c', weight=1)
G.add_edge('c', 'd', weight=1)
G.add_edge('c', 'e', weight=1)
G.add_edge('c', 'f', weight=1)
G.add_edge('f', 'g', weight=1)
G.add_edge('m', 'n', weight=1)
nx.write_adjlist(G, "./data/list_connected_nodes.adjlist")
draw_graph(G)