# Filter a list of chains of overlapping chain
# if b in a exclude b
import re
import time
import os
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
import shutil
import pandas as pd

executor = ProcessPoolExecutor(6)
results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir = 'pairs'
pairs_path = os.path.join(results_path, pairs_dir)
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(pairs_path)]

def chain_in_chain(chunk_index):
	chunk_exclude, exclude_indices, chunk_keep = [], [], []
	pairs_df = pd.read_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=chunk_index)))
	for index, pair in pairs_df.iterrows():
		p1, p2 = pair
		if ((p1 not in chunk_exclude) & (p2 not in chunk_exclude)):
			if p1 in p2:
				exclude_indices.append(index)
				chunk_keep.append(p1)
			elif p2 in p1:
				exclude_indices.append(index)
				chunk_keep.append(p2)
	pairs_df = pairs_df[~pairs_df.index.isin(exclude_indices)]
	chunk_keep = list(set(chunk_keep))
	keep_pairs = list(set(combinations(chunk_keep, 2)))
	keep_pairs_df = pd.DataFrame(keep_pairs, columns=['p1', 'p2'])
	pairs_df = pd.concat([pairs_df, keep_pairs_df])
	return pairs_df

start = time.time()
c = 0
for chunk_df in map(chain_in_chain, chunks_indices):
	c += 1
	print(c, len(chunk_df))
	chunk_df.to_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=c)))

print('chain filter duration=', time.time()-start)
