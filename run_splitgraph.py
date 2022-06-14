import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats
from modules.splitgraph import *

# params
file_path = '/home/rony/Projects_Code/Milestones_Duration/data/MWH-06-UP#13_FSW_REV.graphml'
sparsity_threshold = 0.1

# Graph
G = nx.read_graphml(file_path)
# Rebuild the graph from edges to exclude isolates
nodes_degrees = dict(G.degree())
isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n]==0]
for isolate in isolates: G.remove_node(isolate)

# Edges dependency
G = nx.DiGraph(G)
edges_dependency = {}
Gedges = G.edges(data=True)
for Gedge in Gedges:
	edges_dependency[frozenset((Gedge[0], Gedge[1]))] = Gedge[2]['Dependency']

size_threshold = 50 # int(len(G.nodes)/15)
print('{n} graph nodes | size threshold = {t}'.format(n=len(G.nodes()), t=size_threshold))
partitions = split_graph(G, size_threshold)
for index, partition in enumerate(partitions):
	print(30*'--')
	print(index, len(partition.nodes()), partition.nodes())
	print(partition.edges())
