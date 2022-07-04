import numpy as np
import os
import re
from modules.config import *
from modules.splitgraph import *
from modules.vizz import *
from modules.chains import *

partitions_plots_path = '/home/rony/Projects_Code/Milestones_Duration/results/validation/partitions'
chains = open(os.path.join(experiment_path, 'chains.txt')).read().split('\n')
chains = list(set(chains))
chains = [re.sub("\[|\]|\'", '', c).split(',') for c in chains]
partitions = np.load(os.path.join(experiment_path, 'partitions.npy'), allow_pickle=True)[()]
print('{n} chains already produced'.format(n=len(chains)))
print('{n} partitions to build chains from'.format(n=len(partitions)))

## Build chains from branched graphs
counter = 0
for index, partition in partitions.items():
	counter += 1
	print('\n*** partition {c} index {i} ***'.format(c=counter, i=index))
	draw_graph(partition, os.path.join(partitions_plots_path, 'partition{i}.png'.format(i=index)))
	partition_chains = root_chains(partition)
	chains += partition_chains
	print('{n1} chains produced | {n2} total chains'.format(n1=len(partition_chains), n2=len(chains)))
	write_chains(partition_chains, os.path.join(partitions_plots_path, 'partition{i}_chains.txt'.format(i=index)))
	a = 0
a = 0
chains_str = '\n'.join(str(chains) for chain in chains)
with open(os.path.join(experiment_path, 'chains.txt'), 'w') as f: f.write(chains_str)
print('chain building duration=', round(time.time()-start))


# ## Connect chains
# chains_start, chains_end = build_chains_terminals_dicts(chains)
# edge_relations = predecessors_successors(file_path)
# predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])
# zipper = list(zip(predecessors, successors))
#
# # todo: chains concatenation cycles
# start = time.time()
# print('connecting chains')
# next_step = True
# step_pairs = ['start']
# while step_pairs:
# 	step_pairs = []
# 	chains_start, chains_end = build_chains_terminals_dicts(chains)
# 	for chain1, start_node in chains_start.items():
# 		#print(chain1)
# 		for chain2, end_node in chains_end.items():
# 			start_end = (start_node, end_node)
# 			if start_end in zipper:
# 				step_pairs.append(start_end)
# 				connected_chain = chain1 + chain2
# 				#print('connected chain:', connected_chain)
# 				chains.append(connected_chain)
#
#
