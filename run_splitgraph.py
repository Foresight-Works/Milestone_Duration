import os
import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats
import time
from concurrent.futures import ProcessPoolExecutor
from modules.splitgraph import *

# params
file_path = os.path.join(os.getcwd(), 'data/MWH-06-UP#13_FSW_REV.graphml')
print(file_path)

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
partitions1, isolates = split_graph(G, size_threshold)
# for index, partition in enumerate(partitions):
# 	print(30*'--')
# 	print(index, len(partition.nodes()), partition.nodes())
# 	print(partition.edges())

## Collect chains from partitions
partitions = []
# Split connected components to partitions
for step, partition in partitions1.items():
	components = [partition.subgraph(c).copy() for c in nx.connected_components(partition)]
	for component in components:
		partitions.append(component)
# Single Chain Partitions
print('Building Single Chains from {n} Partitions'.format(n=len(partitions)))
start = time.time()
partitions_chains = {}
executor = ProcessPoolExecutor(12)
#for index, partition in enumerate(partitions):
c = 0
#partitions = list(partitions1.values())[:10]
#partitions = partitions[:10]
chains_count = 0
for partition, partition_chains in executor.map(graph_to_chains, partitions):
	c += 1
	print(c, partition)
	partitions_chains[partition] = partition_chains
	chains_count += len(partition_chains)
np.save('partitions_chains1.npy', partitions_chains)
print('{n} chains produced from sub_graphs'.format(n=chains_count))
print('duration:', time.time()-start)
