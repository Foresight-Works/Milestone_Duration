# Filter a list of chains of overlapping chain
# if b in a exclude b
import re
import time
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import shutil
import pandas as pd
from modules.chains import *
from modules.strings import *
executor = ProcessPoolExecutor(6)
results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/chains'
filtered_chains_dir = 'filtered_chains'
filtered_chains_path = os.path.join(results_path, filtered_chains_dir)
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(chains_path)]
indices_paths = [(index, chains_path, filtered_chains_path) for index in chunks_indices]

start = time.time()
c = 0
indices_paths = [(index, chains_path, filtered_chains_path) for index in chunks_indices]
# todo: output as lists in text files, not as pickled chunks
def chains_overlap(items_path):
	start = time.time()
	data_chunk_index, data_path, results_path = items_path
	items = open(os.path.join(data_path, 'chunk{i}.txt'.format(i=data_chunk_index))).read().split('\n')
	exclude = []
	for i1 in items:
		for i2 in items:
			if i1 == i2:
				exclude.append(i2)
			else:
				pair = [i1, i2]
				if (any(y not in exclude for y in pair)):
					overlap, shorter = pair_overlap(pair)
					if overlap:
						exclude.append(shorter)
		a = 0
	keep = [i for i in items if i not in exclude]
	if keep:
		keep = '\n'.join([str(c) for c in keep])
		with open(os.path.join(results_path, 'chunk{c}.txt'.format(c=chunk_index)), 'w') as f: f.write(keep)
	print('chains file filter duration=', time.time()-start)
	return len(keep)

for filtered_count in executor.map(chains_overlap, indices_paths):
	c += 1
	print(c, filtered_count)
