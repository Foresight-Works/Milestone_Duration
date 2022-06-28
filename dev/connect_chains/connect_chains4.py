import time

import networkx as nx
import numpy as np
import os
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
from modules.chains import *
start = time.time()
nodes_chains = np.load('./results/nodes_chains.npy', allow_pickle=True)[()]

extended_chains, checked_chains = [], []
start = time.time()
c = 0
for node, chains in nodes_chains.items():
	c += 1
	print(c)
	chain_pairs = list(set(combinations(chains, 2)))
	# Todo: multiprocessing
	for chain1, chain2 in chain_pairs:
		pair_extended_chains = extend_chains(chain1, chain2)
		extended_chains += pair_extended_chains
		if not extended_chains:
			checked_chains = checked_chains + chain1 + chain2
print('chain extension duration=', time.time()-start)

