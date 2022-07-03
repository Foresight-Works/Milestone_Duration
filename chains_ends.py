import numpy as np
chains = open('./results/chains.txt').read().split('\n')
chains = [chain.split(',') for chain in chains]
chains_ends = {}
for chain in chains:
	chains_ends[tuple(chain)] = (chain[0], chain[-1])
np.save('./results/chains_ends.npy', chains_ends)

