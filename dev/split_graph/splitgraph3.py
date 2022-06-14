import copy
import networkx as nx
import numpy as np
import pandas as pd
import itertools

def neighbors_graph(node, G):
	neighbors = list(G.neighbors(node)) + list(G.predecessors(node))
	neighbors_as_edges = [(node, neighbor) for neighbor in neighbors]
	result = nx.from_edgelist(neighbors_as_edges)
	return result

def buildNodeGraph(seed, G, nodes_edges, size_threshold):
	# Base NG
	NG = neighbors_graph(seed, G)
	NGnodes = [n for n in list(NG.nodes()) if n != seed]
	NGedges = [(seed, neighbor) for neighbor in NGnodes]
	print(60*'=')
	print('node: {n} | neighbors: {ns}'.format(n=seed, ns=len(NGnodes)))
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

def split_graph(G, size_threshold):
	'''
	Split a graph to n graphs
	'''
	# Edges per node
	# todo: write/call nodes_edges_build as a function
	nodes_edges = np.load('nodes_edges.npy', allow_pickle=True)[()]
	step, graphs, isolates, tracker, Gsource = 0, [], [], [], copy.deepcopy(G)
	while list(G):
		print(60*'*')
		step += 1
		# print('step:', step)
		# print('{n} G nodes start:'.format(n=len(G.nodes())), G.nodes())
		# # Remove isolates formed by nodes removal in the prevoius step
		nodes_degrees = dict(G.degree())
		step_isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]
		for isolate in step_isolates: G.remove_node(isolate)
		# Keep step isolates to join to their neighbours on the partitions that will be built
		isolates += step_isolates

		# Build a graph using the first node that was not joined in a previous step
		node = list(G.nodes())[0]
		NG = buildNodeGraph(node, G, nodes_edges, size_threshold)
		graphs.append(NG)
		subgraph_size = len(NG.nodes())

		# Clean graph of the nodes joined to a subgraph and isolates
		joined_isolates = list(NG.nodes()) #>+ step_isolates
		Gbefore = len(G.nodes())
		#nodes_remove = [n for n in joined_isolates if n in list(G.nodes())]
		#for node_remove in nodes_remove: G.remove_node(node_remove)
		#print('joined_isolates:', joined_isolates)
		for node_remove in joined_isolates:
			if node_remove in list(G.nodes()): G.remove_node(node_remove)
		Gafter = len(G.nodes())
		#nodes_remove = list(NG.nodes())
		#for node_remove in nodes_remove: G.remove_node(node_remove)
		#print('{n} G nodes end:'.format(n=len(G.nodes())), G.nodes())
		# Iterations tracking parameters
		tracker.append([step, subgraph_size, Gbefore, Gafter, len(joined_isolates), len(step_isolates)])

	print('{n} isolates collected'.format(n=len(isolates)))
	tracker_df = pd.DataFrame(tracker, columns=['step', 'subgraph_size', 'G_before', 'G_after', 'nodes_removed', 'isolates'])
	tracker_df.to_excel('tracker6.xlsx', index=False)

	# todo: merge isolates to sub-graphs
	print('tracking isolates')
	graphs_isolates = []
	for isolate in isolates:
		neighbors = list(Gsource.neighbors(isolate)) + list(Gsource.predecessors(isolate))
		for graph in graphs:
			graph_edges = list(graph.edges())
			graph_edges_list = list(set(list(itertools.chain.from_iterable(graph_edges))))
			in_graph = set(graph_edges_list).intersection(set(neighbors))
			if in_graph:
				graph_edges.append((isolate, list(in_graph)[0]))
				graph = nx.from_edgelist(graph_edges)
				graphs_isolates.append(graph)
				pass
			else:
				graphs_isolates.append(graph)

	return graphs
