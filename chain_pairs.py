import time
from itertools import combinations
import os
import shutil
import pandas as pd

results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir = 'pairs'
pairs_path = os.path.join(results_path, pairs_dir)
if pairs_dir in os.listdir(results_path):
	shutil.rmtree(pairs_path, ignore_errors=True)
	os.mkdir(pairs_path)

def pairs_chunks(items, chunk_size = 1000):
	'''
	Build chain pairs combination in chunks to avoid memory issues
	:param items(list): The items to pair
	'''
	c = 0
	while items:
		c += 1
		print(c)
		items_chunk = items[:chunk_size]
		items = items[chunk_size:]
		items_chunk_pairs = list(set(combinations(items_chunk, 2)))
		chunk_df = pd.DataFrame(items_chunk_pairs, columns=['p1', 'p2'])
		chunk_df.to_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=c)))

chains = open('./results/chains.txt').read().split('\n')
start = time.time()
pairs_chunks(chains)
print('chunking duration=', time.time()-start)