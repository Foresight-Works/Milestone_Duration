import os
import re

import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats
import time
from concurrent.futures import ProcessPoolExecutor
from modules.splitgraph import *
from modules.config import *
from modules.milestones import *
from modules.paths import *
from pyvis.network import Network
nt = Network('100%', '100%')
nt.set_options('''var options = {"nodes": {"size": 20, "shape": "triangle", "width":15,
    "font.size":"2"}, "edges":{"width":1, "font.size":"0"}}''')

start = time.time()
# params
file_path = os.path.join(os.getcwd(), 'data/MWH-06-UP#13_FSW_REV.graphml')
print(file_path)

# Graph
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
Gnodes, Gedges = list(G.nodes()), G.edges()
graph_nodes_count = len(G.nodes())
size_threshold = 50 # int(len(G.nodes)/15)

# Isolates
nodes_degrees = dict(G.degree())
source_isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]

# Edges dependency
# edges_dependency = {}
# for Gedge in Gedges:
# 	edges_dependency[frozenset((Gedge[0], Gedge[1]))] = Gedge[2]['Dependency']
# graph_no_isolates_nodes_count = len(set(G.nodes()))
#
# print('{n} graph nodes | size threshold = {t}'.format(n=len(G.nodes()), t=size_threshold))

# Edges direction validation table
# example: <edge id="MWH06-10609-MWH06-10608" source="MWH06-10609" target="MWH06-10608"> -> nodes as source and target
graphml_edges = [l for l in open(file_path).read().split('\n') if 'edge id' in l]
pairs = [tuple(re.findall('[source|target]="(.+?)"', l)) for l in graphml_edges]
edge_relations = pd.DataFrame(pairs, columns=['predecessor', 'successor'])
predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])

# partition graph
partitions,  connected_nodes, tracker = {}, [], []
seeds = [n for n in Gnodes if n not in source_isolates]
partition_index = 0
for index, seed in enumerate(seeds):
	partition_edges = get_successors_edges(seed, G)
	NG = nx.from_edgelist(partition_edges)
	NGdegrees = dict(NG.degree())
	outer_nodes = [n for n in NGdegrees.keys() if (NGdegrees[n] == 1)]# & (n not in connected_nodes))]
	for outer_node in outer_nodes:
		outer_node_neighbors_edges = get_successors_edges(outer_node, G)
		# Validate partition edges
		for edge_pair in outer_node_neighbors_edges:
			p1, p2 = edge_pair
			if p1 in predecessors:
				predecessor = edge_relations['successor'][edge_relations['predecessor']==p1].values[0]
				if p2 == predecessor:
					partition_edges.append(edge_pair)
		partition_edges += outer_node_neighbors_edges
		if len(partition_edges) < size_threshold:
			NG = nx.from_edgelist(partition_edges, create_using=nx.DiGraph)
	if NG:
		partition_index += 1
		partitions[partition_index] = NG
	NGedges = list(NG.edges())
	edges_diff = set(NGedges).difference(set(partition_edges))
	partition_has_cycle, cycle = has_cycle(NG)
	connected_nodes = list(set(connected_nodes + [seed] + list(NG.nodes())))
	a = 0
	nodes_degrees = dict(NG.degree())
	isolates_count = len([n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0])
	tracker_row = [index, seed, len(set(NG.nodes())), len(set(NG.edges())), len(partition_edges),\
	            isolates_count, str(partition_has_cycle)]
	tracker.append(tracker_row)

tracker_df = pd.DataFrame(tracker, columns=['step', 'seed', 'nodes', 'edges', 'partition_edges',\
                                            'isolates', 'has cycle'])
tracker_df.to_excel('tracker10.xlsx', index=False)

# Nodes count validation
c = []
for p in list(partitions.values()): c += list(p.nodes())
partitions_nodes_count = len(set(c))

'''
Note: Highly connected nodes may produce graphs with more edges than size_threshold, 
but these will produce only "star" like graphs with chains of the form: n1 - seed - n2
that should be extractable at a high speed
'''
## Partition chains
partitions_chains = {}
print('Building Single Chains from {n} Partitions'.format(n=len(partitions)))

# Single-chain graphs
checked = []
for index, partition in partitions.items():
	chain = single_chain_graph_to_chains(partition)
	if chain:
		checked.append(index)
		partitions_chains[partition] = [chain]
for index in checked: del partitions[index]

# Nodes count validation
nodes = []
for p, chain in partitions_chains.items():
	nodes += chain[0]
single_chains_nodes_count = len(set(nodes))
partitions_chains_count = len(partitions_chains)

# Star graphs
checked = []
star_chains = []
for index, partition in partitions.items():
	if len(partition) > size_threshold:
		chains = star_graph_to_chains(partition)
		if chain:
			checked.append(index)
			partitions_chains[partition] = chains
			star_chains.append(chains)
for index in checked: del partitions[index]

print('all remaining graphs')
for index, partition in partitions.items():
	#print(index, partition)
	chains = graph_to_chains(partition)
	partitions_chains[partition] = chains

# Collect chains
chains = []
for p, pchains in partitions_chains.items(): chains += pchains
np.save('partitions_chains.npy', partitions_chains)
print('{n} chains produced from sub_graphs'.format(n=len(chains)))
print('duration:', time.time()-start)