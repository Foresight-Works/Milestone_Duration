import networkx as nx
import numpy as np
import os
from itertools import combinations

partitions_chains = np.load('./results/partitions_chains.npy', allow_pickle=True)[()]
chains = []
for partition, pchains in partitions_chains.items(): chains += pchains
cleaned_chains = []
for chain in chains:
	chain = [c[0] if type(c)==list else c for c in chain]
	cleaned_chains.append(tuple(chain))
chains_start_end = {}
for chain in cleaned_chains:
	#print(chain)
	chains_start_end[chain] = (chain[0], chain[-1])
	a = 0

conected_chains, checked_chains = [], []
for index, chain1 in enumerate(cleaned_chains):
	print(index)
	for chain2 in cleaned_chains:
		#print('chain1, 2:', chain1, chain2)
		if ((chain2 != chain1) & (chain2 not in checked_chains)):
			s1, e1 = chains_start_end[chain1]
			s2, e2 = chains_start_end[chain2]
			if e1 == s2:
				chain1 = chain1[:-1]
				conected_chain = chain1 + chain2
			elif e2 == s1:
				chain2 = chain2[:-1]
				conected_chain = chain2 + chain1
			else:
				conected_chain = chain1
			#print('conected_chain:', conected_chain)
			conected_chains.append(conected_chain)
	checked_chains.append(chain1)
