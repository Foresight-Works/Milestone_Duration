# todo: replace hashing loops by the hash modules in modules.chains

import time

import networkx as nx
import numpy as np
import os
from itertools import combinations
from modules.chains import *

partitions_chains = np.load('./results/partitions_chains.npy', allow_pickle=True)[()]
chains = []
for partition, pchains in partitions_chains.items(): chains += pchains
cleaned_chains, nodes = [], []
for chain in chains:
	chain = [c[0] if type(c)==list else c for c in chain]
	cleaned_chains.append(tuple(chain))
	nodes += chain
nodes = list(set(nodes))
nodes_hash_map = numeric_kv(nodes)

hashed_chains = []
for chain in cleaned_chains:
	chain = [nodes_hash_map[n] for n in chain]
	hashed_chains.append(tuple(chain))
print(hashed_chains[:5])

# Nodes - Intersecting Chains
start = time.time()
nodes_chains = {}
for index, node in enumerate(nodes):
	node_hash = nodes_hash_map[node]
	node_chains = [c for c in hashed_chains if node_hash in c]
	nodes_chains[node] = node_chains
print('dict duration=', time.time()-start)
start = time.time()
np.save('./results/nodes_chains.npy', nodes_chains)
print('write duration=', time.time()-start)