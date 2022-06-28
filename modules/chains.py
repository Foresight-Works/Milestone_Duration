from itertools import combinations
import pandas as pd
import os
import re

def extend_chains(a, b):
	extended_chains = []
	interecting_nodes = set(a).intersection(set(b))
	for n in interecting_nodes:
		extension1, extension2 = [], []
		aindex, bindex = (a.index(n), b.index(n))
		# If an intersecting node is a chains' start node
		if aindex == 0:
			a = a[1:]
			extension1 = b + a
		elif bindex == 0:
			b = b[1:]
			extension1 = a + b
		# If an intersecting node is a chains' end node
		elif aindex == len(a) -1:
			a = a[:-1]
			extension1 = a + b
		elif bindex == len(b) -1:
			b = b[:-1]
			extension1 = b + a
		# If an intersecting node is inside a chain
		else:
			extension1 = a[:aindex] + b[bindex:]
			extension2 = b[:bindex] + a[aindex:]
		extensions = [e for e in [extension1, extension2] if e]
		extended_chains += extensions

	return extended_chains
# For parallelized calculation
def extend_chains(pair):
	extended_chains = []
	interecting_nodes = set(a).intersection(set(b))
	for n in interecting_nodes:
		extension1, extension2 = [], []
		aindex, bindex = (a.index(n), b.index(n))
		# If an intersecting node is a chains' start node
		if aindex == 0:
			a = a[1:]
			extension1 = b + a
		elif bindex == 0:
			b = b[1:]
			extension1 = a + b
		# If an intersecting node is a chains' end node
		elif aindex == len(a) -1:
			a = a[:-1]
			extension1 = a + b
		elif bindex == len(b) -1:
			b = b[:-1]
			extension1 = b + a
		# If an intersecting node is inside a chain
		else:
			extension1 = a[:aindex] + b[bindex:]
			extension2 = b[:bindex] + a[aindex:]
		extensions = [e for e in [extension1, extension2] if e]
		extended_chains += extensions
	return extended_chains

def dict_chains_to_chains(key_chains_dict):
	chains = []
	for node, pchains in key_chains_dict.items(): chains += pchains
	return chains

def numeric_kv(strings, use_floats=True):
	'''
	Hash strings as a floating point number
	:param strings (list): A list of strings
	:return: A dictionary of strings: flaoting point number
	'''
	mapping = {}
	if use_floats: numeric_val, increment, decimal = 0.0, 0.1, 2
	else: numeric_val, increment, decimal = 0, 1, 0
	for string in strings:
		numeric_val = round(numeric_val + increment, decimal)
		mapping[string] = numeric_val
	return mapping

def lists_items(items_lists):
	items = []
	for items_list in items_lists:
		items_list = [c[0] if type(c) == list else c for c in items_list]
		items += items_list
	return items

def items_hash_map(items_lists):
	items = lists_items(items_lists)
	return numeric_kv(items)

def hash_lists(items_lists, items_map, result_type = 'tuple'):
	hashed_lists = []
	for items_list in items_lists:
		items_list = [items_map[n] for n in items_list]
		hashed_lists.append(tuple(items_list))
	return hashed_lists

def hash_chunk_chains(index_path):
	chunk_index, chains_map, pairs_path, hashed_chains_path = index_path
	pairs_df0 = pd.read_pickle(os.path.join(pairs_path, 'chunk{c}.pkl'.format(c=chunk_index)))
	pairs = [tuple(p) for p in pairs_df0.values.tolist()]
	hashed_pairs = []
	for index, pair in enumerate(pairs):
		hashed_pair = []
		for items_list in pair:
			items_list = items_list.split(',')
			hashed_list = str([chains_map[item] for item in items_list])
			hashed_list = re.sub("\[|\]|'|\s", '', hashed_list)
			hashed_pair.append(hashed_list)
			a = 0
		hashed_pairs.append(tuple(hashed_pair))
	hashed_pairs_df = pd.DataFrame(hashed_pairs, columns=['p1', 'p2'])
	hashed_pairs_df.to_pickle(os.path.join(hashed_chains_path, 'chunk{c}.pkl'.format(c=chunk_index)))

	return hashed_pairs_df

def chains_overlap(index_path):
	chunk_index, pairs_path = index_path
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
