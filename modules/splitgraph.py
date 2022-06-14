import networkx as nx
import numpy as np
import pandas as pd
import random
from scipy import stats
from itertools import combinations
import copy

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
	edges_graphs = []
	indices = [int(i) for i in np.arange(len(edges_list))]
	graphs_indices = partition(indices, n)
	for partition_indices in graphs_indices:
		partition_edges = [edges_list[i] for i in partition_indices]
		edges_graphs.append(partition_edges)
	return edges_graphs

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

def buildNodeGraph(start_node, G, nodes_edges, size_threshold):
	# Base NG
	NG = neighbors_graph(start_node, G)
	NGnodes = [n for n in list(NG.nodes()) if n != start_node]
	NGedges = [(start_node, neighbor) for neighbor in NGnodes]
	print(60*'=')
	print('node: {n} | neighbors: {ns}'.format(n=start_node, ns=len(NGnodes)))
	tracker, graphs = [], [NG]
	for node in NGnodes:
		NGedges += nodes_edges[node]
		NG = nx.from_edgelist(NGedges)
		graphs.append(NG)
		tracker.append([node, len(NGedges), len(NG)])
		if len(NG.nodes()) > size_threshold:
			break
	result = graphs[-2]
	print(pd.DataFrame(tracker, columns=['node', 'acc_edges', 'graph_size']))
	print('{n} nodes in sub-graph:'.format(n=len(result.nodes())), result.nodes())
	return result


def calc_sparsity_score(G):
	A = nx.adjacency_matrix(G)
	none_zero_vals = int(np.sum(A))
	sum_vals = A.shape[0] ** 2
	return none_zero_vals/sum_vals

def split_graph(G, size_threshold):
	'''
	Split a graph to n graphs
	'''
	graphs = []
	nodes_degrees = dict(G.degree())

	# Outlier junctions
	degrees_outliers_high = get_outliers(list(nodes_degrees.values()), threshold=2)
	degrees_outliers_low = get_outliers(list(nodes_degrees.values()), threshold=1)
	degrees_outliers_low = [j for j in degrees_outliers_low if j not in degrees_outliers_high]

	#sorted_nodes = [k for k, v in sorted(nodes_degrees.items(), key=lambda item: item[1], reverse=True)]
	sorted_nodes = [k for k, v in sorted(nodes_degrees.items(), key=lambda item: item[1])]
	graphs_list = [neighbors_graph(node, G) for node in sorted_nodes]
	# Edges per node
	nodes_edges = np.load('nodes_edges.npy', allow_pickle=True)[()]
	step = 0
	step, isolates, tracker, Gtracker = 0, [], [], copy.deepcopy(G)
	while list(G):
		print(60*'*')
		step += 1
		print('step:', step)
		print('{n} G nodes start:'.format(n=len(G.nodes())), G.nodes())
		# Remove isolates formed by nodes removal in the prevoius step
		nodes_degrees = dict(G.degree())
		step_isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]
		for isolate in step_isolates: G.remove_node(isolate)
		# Keep step isolates to join to their neighbours on the subgraphs that will be built
		isolates += step_isolates

		# Build a graph using the first node that was not joined in a previous step
		node = list(G.nodes())[0]
		NG = buildNodeGraph(node, G, nodes_edges, size_threshold)
		graphs.append(NG)
		subgraph_size = len(NG.nodes())

		# Clean graph of the nodes joined to a subgraph and isolates
		joined_isolates = list(NG.nodes()) + step_isolates
		Gbefore = len(G.nodes())
		#nodes_remove = [n for n in joined_isolates if n in list(G.nodes())]
		#for node_remove in nodes_remove: G.remove_node(node_remove)
		print('joined_isolates:', joined_isolates)
		for node_remove in joined_isolates:
			if node_remove in list(G.nodes()): G.remove_node(node_remove)
		Gafter = len(G.nodes())
		#nodes_remove = list(NG.nodes())
		#for node_remove in nodes_remove: G.remove_node(node_remove)
		print('{n} G nodes end:'.format(n=len(G.nodes())), G.nodes())
		# Iterations tracking parameters
		tracker.append([step, subgraph_size, Gbefore, Gafter, len(joined_isolates), len(step_isolates)])

	print('{n} step isolates collected'.format(n=len(isolates)))
	tracker_df = pd.DataFrame(tracker, columns=['step', 'subgraph_size', 'G_before', 'G_after', 'nodes_removed', 'isolates'])
	tracker_df.to_excel('tracker6.xlsx', index=False)
	# todo: merge isolates to sub-graphs
	return graphs
