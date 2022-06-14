import networkx as nx
import numpy as np
import random

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
def split_graph(G, num_partitions):
	'''
	Split a graph to n partitions
	:param G:
	:param n:
	:return:
	'''
	partitions = []
	Gnodes, Gedges = list(G.nodes()), list(G.edges())
	nodes_degrees = dict(G.degree())
	sorted_degrees = sorted(list(nodes_degrees.values()), reverse=True)
	junctions = [n for n in Gnodes if nodes_degrees[n] in sorted_degrees[:num_partitions]]
	# partitions_edges = get_partition_edges(Gedges, n)
	# for partition_edges in partitions_edges:
	# 	partition = nx.from_edgelist(partition_edges)
	return partitions
# params
file_path = '/home/rony/Projects_Code/Milestones_Duration/data/MWH-06-UP#13_FSW_REV.graphml'
num_partitions = 200

# Graph
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
split_graph(G, num_partitions)
