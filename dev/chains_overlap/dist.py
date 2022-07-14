import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/Jul13_22/chains.txt'
chains = open(chains_path).read().split('\n')
executor = ProcessPoolExecutor(10)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("The run started on", current_time)

# Data preparation
nodes_chains =[]
for index, chain in enumerate(chains):
	nodes_chains.append((index, chain, chains))

def get_chain_overlaps(chain_chains):
	index1, chain, chains = chain_chains
	chains.remove(chain)
	for index1, chain2 in enumerate(chains):
		if chain in chain2:
			overlap = chain
			longer = chain2
			return chain, overlap, longer
	return None, None, None

start = time.time()
chains_overlaps = []
c = 0
for chain, overlap, longer in map(get_chain_overlaps, nodes_chains):
	c += 1
	print(80*'*')
	print(c, chain)
	print('overlap:', overlap)
	print('longer:', longer)

	chains_overlaps.append(overlap)

print('duration=', time.time()-start)
print(len(chains_overlaps))