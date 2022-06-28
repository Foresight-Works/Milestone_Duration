# todo: replace hashing loops by the hash modules in modules.chains
import numpy as np
import re
import time
import os
from concurrent.futures import ProcessPoolExecutor
import shutil
import pandas as pd
from modules.chains import *
executor = ProcessPoolExecutor(10)

# Chains map
partitions_chains = np.load('./results/partitions_chains.npy', allow_pickle=True)[()]
chains = dict_chains_to_chains(partitions_chains)
chains_map = items_hash_map(chains)
del chains

# Data Identifiers
results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir = 'pairs'
pairs_path = os.path.join(results_path, pairs_dir)
# todo: hashed_chains_path(validation) -> pairs path (production)
hashed_chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/hashed_chains'
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(pairs_path)]
indices_path = [(index, chains_map, pairs_path, hashed_chains_path) for index in chunks_indices]
c = 0
start = time.time()
for chunk_df in executor.map(hash_chunk_chains, indices_path):
	#keep += chunk_keep
	c += 1
	print(c, len(chunk_df))
print('hash chains duration=', time.time()-start)