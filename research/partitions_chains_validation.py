import networkx as nx
import numpy as np
import os
# Graph
file_path = os.path.join(os.getcwd(), 'data/MWH-06-UP#13_FSW_REV.graphml')
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
Gnodes, Gedges = list(G.nodes()), G.edges()

partitions_chains = np.load('partitions_chains.npy', allow_pickle=True)[()]
Gedges = set(list(G.edges()))
chains_edges = []
for partition, pchains in partitions_chains.items(): chains_edges += list(partition.edges())
chains_edges = set(chains_edges)
diff = chains_edges.difference(Gedges)
intersect = set(chains_edges).intersection(Gedges)
a = 0