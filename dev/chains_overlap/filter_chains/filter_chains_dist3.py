# Filter a list of chains of overlapping chain
# if b in a exclude b
import re
import time
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import shutil
import pandas as pd

executor = ProcessPoolExecutor(6)
results_path = '/results/'
pairs_dir = 'pairs'
pairs_path = os.path.join(results_path, pairs_dir)
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(pairs_path)]

def chain_in_chain(chunk_index):
	chunk_exclude, chunk_keep, exclude_indices = [], [], []
	pairs_df0 = pd.read_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=chunk_index)))
	pairs = [tuple(p) for p in pairs_df0.values.tolist()]
	for index, pair in enumerate(pairs):
		p1, p2 = pair
		if ((p1 not in chunk_exclude) & (p2 not in chunk_exclude)):
			if p1 in p2:
				exclude_indices.append(index)
				chunk_keep.append(p1)
			elif p2 in p1:
				exclude_indices.append(index)
				chunk_keep.append(p2)
	pairs_df = pairs_df0[~pairs_df0.index.isin(exclude_indices)]
	chunk_keep = list(set(chunk_keep))
	keep_pairs = list(set(combinations(chunk_keep, 2)))
	keep_pairs_df = pd.DataFrame(keep_pairs, columns=['p1', 'p2'])
	pairs_df = pd.concat([pairs_df, keep_pairs_df])
	if len(pairs_df) == 0:
		print(pairs_df.head())
	pairs_df.to_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=c)))
	return pairs_df

start = time.time()
keep = []
c = 0
for chunk_df in executor.map(chain_in_chain, chunks_indices):
	#keep += chunk_keep
	print(c, len(chunk_df))
	if len(chunk_df) > 0:
		c += 1


print('{n1} chains in filtered list'.format(n1=len(keep)))
print('chain filter duration=', time.time()-start)
keep = '\n'.join(list(set(keep)))
with open('./results/filtered_chains.txt', 'w') as f: f.write(keep)
# shutil.rmtree(pairs_path, ignore_errors=True)
