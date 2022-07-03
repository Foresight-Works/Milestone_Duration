from itertools import combinations
import pandas as pd
import os
import re
import time
import networkx as nx

def chains_from_linear_graph(G):
	chain = []
	if len(G) == 2:
		chain = list(G.nodes())
	else:
		max_degree = max([d[1] for d in G.degree()])
		if max_degree == 2:
			try:
				chain = list(nx.topological_sort(G))
			except nx.exception.NetworkXError:
				Gdegrees = dict(G.degree())
				outer_nodes = [n for n in Gdegrees.keys() if Gdegrees[n] == 1]
				chain = list(nx.all_simple_paths(G, outer_nodes[0], outer_nodes[1]))[0]
	return chain

def chains_from_linear_graphs(indexed_graphs):
	chains = {}
	# Single-chain graphs
	for index, graph in indexed_graphs.items():
		chain = chains_from_linear_graph(graph)
		if chain:
			chains[index] = chain
	return chains

def chains_from_star_graph(G):
	chains = []
	Gdegrees = dict(G.degree())
	outer_nodes = [n for n in Gdegrees.keys() if (Gdegrees[n] == 1)]
	seed = [n for n in Gdegrees.keys() if (Gdegrees[n] > 1)]
	outer_node_pairs = list(set(combinations(outer_nodes, 2)))
	for p1, p2 in outer_node_pairs:
		chains.append([p1, seed, p2])
	return chains

def chains_from_star_graphs(indexed_graphs, graph_size_cutoff):
	star_chains = {}
	for index, graph in indexed_graphs.items():
		Gdegrees = dict(graph.degree())
		max_node = [k for k, v in Gdegrees.items() if v > 1]
		# Star signal: Only one node has more than one links
		if len(max_node) == 1:
			chains = chains_from_star_graph(graph)
			if chains:
				star_chains[index] = chains
	return star_chains

def nodes_chains(chains):
	nodes = []
	for chain in chains: nodes += chain
	return nodes

def extend_pair_chains(pair):
	a, b = pair
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

def extend_chunk_pairs(index_path):
	chunk_index, data_path, results_path = index_path
	extended_chains, chunk_exclude, exclude_indices = [], [], []
	pairs_df0 = pd.read_pickle(os.path.join(data_path, 'chunk{c}.pkl'.format(c=chunk_index)))
	pairs = [tuple(p) for p in pairs_df0.values.tolist()]
	for index, pair in enumerate(pairs):
		extended_chains += extend_pair_chains(pair)
		a=0
	extended_chains = list(set(extended_chains))
	if extended_chains:
		extended_chains = '\n'.join([str(c) for c in extended_chains])
		with open(os.path.join(results_path, 'chunk{c}.txt'.format(c=chunk_index)), 'w') as f: f.write(extended_chains)
	return len(extended_chains)

def dict_chains_to_chains(key_chains_dict):
	chains = []
	for node, pchains in key_chains_dict.items(): chains += pchains
	return chains

def chains_nodes_count(chains):
	nodes = []
	for chain in chains: nodes += chain
	return (len(set(nodes)))

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

def pairs_chunks(items_path, chunk_size = 1000):
	'''
	Build chain pairs combination in chunks to avoid memory issues
	:param items(list): The items to pair
	'''
	start = time.time()
	data_chunk_index, chains_path, results_path = items_path
	items = open(os.path.join(chains_path, 'chunk{i}.txt'.format(i=data_chunk_index))).read().split('\n')
	chunk_index = data_chunk_index
	while items:
		chunk_index = round(chunk_index + 0.1, 4)
		items_chunk = items[:chunk_size]
		items = items[chunk_size:]
		items_chunk_pairs = list(set(combinations(items_chunk, 2)))
		chunk_df = pd.DataFrame(items_chunk_pairs, columns=['p1', 'p2'])
		write_path = os.path.join(results_path, 'chunk{c}.pkl'.format(c=chunk_index))
		chunk_df.to_pickle(write_path)
	print('chunking duration=', time.time() - start)
	return 'finished'
