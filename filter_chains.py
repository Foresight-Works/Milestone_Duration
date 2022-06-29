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
executor = ProcessPoolExecutor(6)
results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir = 'hashed_chains'
pairs_path = os.path.join(results_path, pairs_dir)
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(pairs_path)]

start = time.time()
keep = []
c = 0
indices_paths = [(index, pairs_path) for index in chunks_indices]

for chunk_df in executor.map(chains_overlap, indices_paths):
	#keep += chunk_keep
	print(c, len(chunk_df))
	if len(chunk_df) > 0:
		c += 1

print('{n1} chains in filtered list'.format(n1=len(keep)))
print('chain filter duration=', time.time()-start)
keep = '\n'.join(list(set(keep)))
with open('./results/filtered_chains.txt', 'w') as f: f.write(keep)
# shutil.rmtree(pairs_path, ignore_errors=True)
