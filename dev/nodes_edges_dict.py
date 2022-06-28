import time

import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats

from modules.splitgraph import *

# params
file_path = './data/MWH-06-UP#13_FSW_REV.graphml'
sparsity_threshold = 0.1

# Graph
G = nx.read_graphml(file_path)
# Rebuild the graph from edges to exclude isolates
nodes_degrees = dict(G.degree())
isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n]==0]
for isolate in isolates: G.remove_node(isolate)
G = nx.DiGraph(G)

start = time.time()
Gnodes, Gedges = G.nodes(), G.edges()
nodes_edges = {}
for node in Gnodes:
	node_edges = []
	for edge in Gedges:
		if node in edge: node_edges.append(edge)
	nodes_edges[node] = node_edges
np.save('nodes_edges.npy', nodes_edges)
print('nodes edges duration=', time.time()-start)
