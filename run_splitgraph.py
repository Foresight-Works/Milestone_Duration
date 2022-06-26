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
source_isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]
graph_nodes_count = len(G.nodes())
for isolate in source_isolates: G.remove_node(isolate)
# Edges dependency

G = nx.DiGraph(G)
edges_dependency = {}
Gedges = G.edges(data=True)
for Gedge in Gedges:
	edges_dependency[frozenset((Gedge[0], Gedge[1]))] = Gedge[2]['Dependency']
graph_no_isolates_nodes_count = len(set(G.nodes()))
size_threshold = 50 # int(len(G.nodes)/15)
print('{n} graph nodes | size threshold = {t}'.format(n=len(G.nodes()), t=size_threshold))
partitions1, chain_isolates = split_graph(G, size_threshold)

## Collect chains from partitions
partitions = []
# Split connected components to partitions
for step, partition in partitions1.items():
	components = [partition.subgraph(c).copy() for c in nx.connected_components(partition)]
	for component in components:
		partitions.append(component)

## Partition chains
partitions_chains = {}
print('Building Single Chains from {n} Partitions'.format(n=len(partitions)))

# Single-chain graphs
checked = []
for partition in partitions:
	chain = single_chain_graph_to_chains(partition)
	if chain:
		checked.append(partition)
		partitions_chains[partition] = chain
nodes = []
for p, chain in partitions_chains.items():
	nodes += chain
single_chains_nodes_count = len(set(nodes))
partitions = [p for p in partitions if p not in checked]

# Check partitions count
nodes = []
for p in partitions:
	nodes += list(p.nodes())
multiple_chains_nodes_count = len(set(nodes))
# Branched graphs
print('{n1} single chain graphs analyzed, {n2} branched graphs to go'\
      .format(n1=len(checked), n2=len(partitions)))
start = time.time()
executor = ProcessPoolExecutor(6)
c, chains_count = 0, 0
#for partition, partition_chains in executor.map(graph_to_chains, partitions):
for partition, partition_chains in map(graph_to_chains, partitions):
	c += 1
	print(c, partition)
	partitions_chains[partition] = partition_chains
	chains_count += len(partition_chains)
np.save('partitions_chains1.npy', partitions_chains)
print('{n} chains produced from sub_graphs'.format(n=chains_count))
print('duration:', time.time()-start)