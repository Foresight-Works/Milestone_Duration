import time
import numpy as np
from bisect import bisect_left
import inspect

def timer(func):
	def run_function(*args):
		start = time.time()
		func(*args)
		end = time.time()
		duration = round(end-start,  2)
		return duration
	return run_function

@timer
def search_sorted(queries,  sorted_sequence):
	print(inspect.stack()[0][3])
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted1(queries,  sorted_sequence):
	print(inspect.stack()[0][3])
	queries = sorted(queries)
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted2(queries,  sorted_sequence):
	print(inspect.stack()[0][3])
	queries = sorted(queries)
	sorted_sequence = np.array(sorted_sequence)
	in_sorted = []
	for q in queries:
		if q in sorted_sequence: in_sorted.append(q)
	return in_sorted

@timer
def search_sorted3(queries,  sorted_sequence):
	print(inspect.stack()[0][3])
	queries = sorted(queries)
	queries_min,  queries_max = queries[0],  queries[-1]
	sorted_sequence = np.array(sorted_sequence)
	filtered_sequence = sorted_sequence[queries_min <= sorted_sequence]
	filtered_sequence = filtered_sequence[filtered_sequence <= queries_max]
	in_sorted = []
	for q in queries:
		if q in filtered_sequence: in_sorted.append(q)
	return in_sorted

@timer
def BinarySearch(queries,  sorted_sequence):
	print(inspect.stack()[0][3])
	in_sorted = []
	for q in queries:
		i = bisect_left(sorted_sequence,  q)
		if i != len(sorted_sequence) and sorted_sequence[i] == q:
			in_sorted.append(q)
	return in_sorted

@timer
def binarySearchFilter(queries_list, target):
	print(inspect.stack()[0][3])
	target = sorted(target)
	in_sorted = []
	for q in queries_list:
		i = bisect_left(target,  q)
		if i != len(target) and target[i] == q:
			in_sorted.append(q)
	return in_sorted


# Data
sorted_sample = [float(i) for i in open('sorted_sample.txt').read().split('\n')]
queries = [float(i) for i in open('queries.txt').read().split('\n')]
#sorted_sample = [1, 2, 3, 5, 6, 7, 8, 9, 33, 45, 65, 23]
#queries = [1, 2, 8, 99]

functions = [search_sorted, search_sorted1, search_sorted2, search_sorted3, BinarySearch, binarySearchFilter]
functions = [BinarySearch, binarySearchFilter]
for function in functions:
	duration = function(queries, sorted_sample)
	print(duration)


#duration = BinarySearch(queries,  sorted_sample)
#print(duration)

'''
Functions - Duration results:
search_sorted
3.91
search_sorted1
3.9
search_sorted2
0.18
search_sorted3
0.2
BinarySearch
0.01
binarySearchFilter
0.01
'''