import time

import networkx as nx
import numpy as np
import os
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
#from modules.chains import *
start = time.time()
nodes_chains = np.load('./results/nodes_chains.npy', allow_pickle=True)[()]

def extend_chains(a, b):
	#a, b = chains_pair
	extended_chains = []
	interecting_nodes = set(a).intersection(set(b))
	for n in interecting_nodes:
		extension1, extension2 = [], []
		aindex, bindex = (a.index(n), b.index(n))
		# If an intersecting node is a chains' start node
		if aindex == 0:
			a = a[1:]
			extension1 = b + a
		elif bindex == 0:
			b = b[1:]
			extension1 = a + b
		# If an intersecting node is a chains' end node
		elif aindex == len(a) -1:
			a = a[:-1]
			extension1 = a + b
		elif bindex == len(b) -1:
			b = b[:-1]
			extension1 = b + a
		# If an intersecting node is inside a chain
		else:
			extension1 = a[:aindex] + b[bindex:]
			extension2 = b[:bindex] + a[aindex:]
		extensions = [e for e in [extension1, extension2] if e]
		extended_chains += extensions
	return extended_chains

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

