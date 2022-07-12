import time
import numpy as np
import random

def timer(func):
	def run_function(*args):
		start = time.time()
		func(*args)
		end = time.time()
		duration = round(end-start, 2)
		return duration
	return run_function

@timer
def search_sorted(queries, sorted_sequence):
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted1(queries, sorted_sequence):
	queries = sorted(queries)
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted2(queries, sorted_sequence):
	queries = sorted(queries)
	sorted_sequence = np.array(sorted_sequence)
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted3(queries, sorted_sequence):
	queries = sorted(queries)
	queries_min, queries_max = queries[0], queries[-1]
	sorted_sequence = np.array(sorted_sequence)
	filtered_sequence = sorted_sequence[queries_min <= sorted_sequence]
	filtered_sequence = filtered_sequence[filtered_sequence <= queries_max]
	in_sorted = []
	for q in queries:
		if q in filtered_sequence: in_sorted.append(q)
	return in_sorted



# Data
population = list(np.arange(0, 10000, 0.1))
population = [round(p, 2) for p in population]
sample = random.sample(population, 24490)
sorted_sample = sorted(sample)
queries = random.sample(population, 20728)
duration = search_sorted3(queries, sorted_sample)
print(duration)


'''
Duration
current (strings, not sorted): 6
search_sorted: 8.58
search_sorted1 += queries sorted: 8.6
search_sorted2 += target as list: 8.6
search_sorted3 += filtered by queries min-max: 0.22
'''