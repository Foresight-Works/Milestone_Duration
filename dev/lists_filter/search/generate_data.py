import numpy as np
import random

sample_size, queries_size = 24490, 20728
sample_size, queries_size = 40, 20
population = list(np.arange(0, 10000, 0.1))
population = [round(p, 2) for p in population]
sample = random.sample(population, sample_size)
sorted_sample = sorted(sample)
sorted_sample = '\n'.join([str (i) for i in sorted_sample])
with open('small_sorted_sample.txt', 'w') as f: f.write(sorted_sample)
queries = random.sample(population, queries_size)
queries = '\n'.join([str (i) for i in queries])
with open('small_queries.txt', 'w') as f: f.write(queries)

