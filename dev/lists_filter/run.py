import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from filters import *
from encoders import *
# Data
tokens = open('tokens.txt').read().split('\n')
# Samples and queries
sample_sizes = np.arange(30000, 300000, 30000)
samples_queries = {}
for size in sample_sizes:
	sample = random.sample(tokens, size)
	query = random.sample(tokens, size)
	samples_queries[size] = (sample, query)

duration_values = []
for size, data in samples_queries.items():
	size_duration = []
	print(size)
	sample, queries = data
	start = time.time()
	filtered = binarySearchFilter(sample, queries)
	dur1 = round(time.time()-start, 2)
	start = time.time()
	filtered = lists_filter(sample, queries)
	dur2 = round(time.time() - start, 2)
	duration_values.append([size, dur1, dur2, round(dur1/dur2, 2)])

duration_df = pd.DataFrame(duration_values, columns=['size', 'binary', 'set', 'ratio'])
duration_df.to_excel('filters_comparison.xlsx', index=False)
print(duration_df)

x, y1, y2 = list(duration_df['size']), list(duration_df['binary']), list(duration_df['set'])
plt.plot(x, y2, label="set")
plt.plot(x, y1, label="binary")
plt.xlabel('sample size')
plt.legend()
plt.show()
plt.savefig('filters_comparison.png')
