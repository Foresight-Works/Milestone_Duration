import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats
from itertools import combinations

def get_outliers(x, threshold=3):
    '''
    Filter a list of values of outliers
    :param x: A list of numeric values
    param threshold: The outliers cutoff
    :return: The outliters
    '''
    x = pd.DataFrame(x, columns=['value'])
    transformed = x[['value']].transform(stats.zscore)
    x['zscore'] = transformed
    outliers = list(x['value'][x['zscore'] >= threshold].values)
    return outliers

def partition (list_in, n):
    random.shuffle(list_in)
    return [list(list_in[i::n]) for i in range(n)]

def get_partition_edges(edges_list, n):
	edges_partitions = []
	indices = [int(i) for i in np.arange(len(edges_list))]
	partitions_indices = partition(indices, n)
	for partition_indices in partitions_indices:
		partition_edges = [edges_list[i] for i in partition_indices]
		edges_partitions.append(partition_edges)
	return edges_partitions

def neighbors_graph(node, G):
	neighbors = list(G.neighbors(node)) + list(G.predecessors(node))
	neighbors_as_edges = [(node, neighbor) for neighbor in neighbors]
	result = nx.from_edgelist(neighbors_as_edges)
	return result

def sub_graph_neighbors(G, subG):
	subGnodes = list(subG.nodes())
	subG_neighbors = []
	for node in subGnodes:
		neighbors = list(G[node].keys())
		subG_neighbors += neighbors
	return subG_neighbors

import itertools
def connected_nodes(G, G1, G2):
	result = []
	G1neighbors = sub_graph_neighbors(G, G1)
	G2neighbors = sub_graph_neighbors(G, G2)
	# Build all combinations of G1neighbors,G2neighbors
	nodes_combinations = list(x for x in itertools.product(G1neighbors, G2neighbors))
	nodes_combinations = [frozenset(x) for x in nodes_combinations]
	#nodes_combinations2 = list(x for x in itertools.product(G2neighbors, G1neighbors))
	#nodes_combinations = nodes_combinations1 + nodes_combinations2
	#Gedges = list(G.edges())
	Gedges = [frozenset(x) for x in list(G.edges())]
	result = [pair for pair in nodes_combinations if pair in Gedges]
	return result

def link_graphs(G, G1, G2):
	result = []
	G12nodes = connected_nodes(G, G1, G2)
	if G12nodes:
		G12edges = list(G1.edges()) + list(G2.edges())
		result = nx.from_edgelist(G12edges)
	return result

def calc_sparsity_score(G):
	A = nx.adjacency_matrix(G)
	none_zero_vals = int(np.sum(A))
	sum_vals = A.shape[0] ** 2
	return none_zero_vals/sum_vals

def split_graph(G, sparsity_threshold):
	'''
	Split a graph to n partitions
	:param G:
	:param n:
	:return:
	'''
	graphs, partitions = {}, []
	nodes_degrees = dict(G.degree())

	# Outlier junctions
	degrees_outliers_high = get_outliers(list(nodes_degrees.values()), threshold=2)
	degrees_outliers_low = get_outliers(list(nodes_degrees.values()), threshold=1)
	degrees_outliers_low = [j for j in degrees_outliers_low if j not in degrees_outliers_high]

	#sorted_nodes = [k for k, v in sorted(nodes_degrees.items(), key=lambda item: item[1], reverse=True)]
	sorted_nodes = [k for k, v in sorted(nodes_degrees.items(), key=lambda item: item[1])]
	graphs_list = [neighbors_graph(node, G) for node in sorted_nodes]

	# Test: Mid range node graphs
	graphs_list = [neighbors_graph(node, G) for node in sorted_nodes if 10>nodes_degrees[node]>5]
	for i in range(len(graphs_list)):
		graphs[i] = graphs_list[i]
	a = len(graphs)
	indices = np.arange(a)
	indices = list(set(combinations(indices, 2)))
	c = 0
	while graphs:
		print('iteration {c}, {n} graphs to compare'.format(c=c, n=len(graphs)))
		tail_index = len(graphs) - 1
		indices = [p for p in indices if ((p[0] <= tail_index) & (p[1] <= tail_index)) ]
		for indices_pair in indices:
			print(indices_pair)
			p1, p2 = indices_pair
			G1, G2 = graphs[p1], graphs[p2]
			G12 = link_graphs(G, G1, G2)
			if G12:
				sparsity_score = calc_sparsity_score(G12)
				if sparsity_score <= sparsity_threshold:
					partitions.append(G12)
					del graphs[p1], graphs[p2]
	return partitions
