import re
import time
import os
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
import shutil
import pandas as pd
from modules.chains import *
executor = ProcessPoolExecutor(10)
# Todo experiment/runs path setup as in CA
run_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir, results_dir = 'pairs', 'chains'
# todo integration: join pairs and result dicrtories
pairs_path = os.path.join(run_path, pairs_dir)
results_path = os.path.join(run_path, results_dir)
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(pairs_path)]
# Extension iteration test
# todo: place chain as a while loop iteration triggering step i+1 if new chains have been produced in step i
start = time.time()
keep = []
c = 0
indices_path = [(index, pairs_path, results_path) for index in chunks_indices]
for extended_chains_count in executor.map(extend_chunk_pairs, indices_path):
	c += 1
	print(c, extended_chains_count)
print('chain extension duration=', time.time()-start)