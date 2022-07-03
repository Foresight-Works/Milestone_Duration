from itertools import combinations, product
from modules.libraries import *
from modules.splitgraph import *
from modules.paths import *
from modules.vizz import *

def build_graph(file_path):
	# Graph
	G = nx.read_graphml(file_path)
	G = nx.DiGraph(G)
	return G

def graphs_nodes_count(graphs):
	nodes = []
	for graph in graphs: nodes += list(graph.nodes())
	return (len(set(nodes)))

def graph_isolates(G):
	nodes_degrees = dict(G.degree())
	return [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]

def graph_pair_overlap(g1, g2):
	# Clean partitions of overlapping chain-parts
	mutual_edges = []
	g1edges, g2edges = list(g1.edges()), list(g2.edges())
	edges_combinations = list(product(g1edges, g2edges))
	for edges_combination in edges_combinations:
		if edges_combination[0] == edges_combination[1]:
			mutual_edges.append(edges_combination[0])
	return mutual_edges

def terminal_edge(g1index, g2index, g1, g2, mutual_edge):
	result = -1
	e1, e2 = mutual_edge
	deg = dict(g1.degree())
	e1deg, e2deg = deg[e1], deg[e2]
	if ((e1deg == 2) & (e2deg == 1)): result = g1index
	else:
		deg = dict(g2.degree())
		e1deg, e2deg = deg[e1], deg[e2]
		if ((e1deg == 2) & (e2deg == 1)): result = g2index
	return result

def get_terminal_edges(g1index, g2index, g1, g2, mutual_edges):
	graphs_edges = {}
	indices_graphs = {g1index: g1, g2index: g2}
	for mutual_edge in mutual_edges:
		graph_to_clean_index = terminal_edge(g1index, g2index, g1, g2, mutual_edge)
		if graph_to_clean_index != -1:
			graphs_edges[graph_to_clean_index] = (indices_graphs[graph_to_clean_index], mutual_edge)
	return graphs_edges
#g1.remove_nodes_from([e1, e2])

def graph_pairs_overlap(indexed_graphs):
	cleaned_graphs = {}
	graph_pairs = list(set(combinations(list(indexed_graphs.keys()), 2)))
	# Iterate graph pairs to identify overlaps by comparing their edges
	for g1index, g2index in graph_pairs:
		print(g1index, g2index)
		g1, g2 = indexed_graphs[g1index], indexed_graphs[g2index]
		# validation
		val1, val2 = list(g1.edges()), list(g2.edges())
		#draw_graph(g1, 'g1.png')
		#draw_graph(g2, 'g2.png')
		mutual_edges = graph_pair_overlap(g1, g2)
		if mutual_edges:
			graphs_edges = get_terminal_edges(g1index, g2index, g1, g2, mutual_edges)
			for graph_index, graph_edge in graphs_edges.items():
				graph, edge = graph_edge
				nodes = [edge[0], edge[1]]
				cleaned_graphs[graph_index] = graph.remove_nodes_from(nodes)
	return cleaned_graphs

def predecessors_successors(file_path):
	'''Edges direction validation table
	example: <edge id="MWH06-10609-MWH06-10608" source="MWH06-10609" target="MWH06-10608"> -> nodes as source and target
	'''
	graphml_edges = [l for l in open(file_path).read().split('\n') if 'edge id' in l]
	pairs = [tuple(re.findall('[source|target]="(.+?)"', l)) for l in graphml_edges]
	edge_relations = pd.DataFrame(pairs, columns=['predecessor', 'successor'])
	#predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])
	return edge_relations

def partition_graph(G, file_path, partition_size_cutoff):
	Gnodes = list(G.nodes())
	edge_relations = predecessors_successors(file_path)
	predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])
	source_isolates = graph_isolates(G)
	partitions,  connected_nodes, tracker = {}, [], []
	seeds = [n for n in Gnodes if n not in source_isolates]
	partition_index = 0

	# Build partitions
	for index, seed in enumerate(seeds):
		partition_edges = get_successors_edges(seed, G)
		NG = nx.from_edgelist(partition_edges)
		NGdegrees = dict(NG.degree())
		outer_nodes = [n for n in NGdegrees.keys() if (NGdegrees[n] == 1)]
		for outer_node in outer_nodes:
			outer_node_neighbors_edges = get_successors_edges(outer_node, G)
			# Validate partition edges
			for edge_pair in outer_node_neighbors_edges:
				p1, p2 = edge_pair
				if p1 in predecessors:
					predecessor = edge_relations['successor'][edge_relations['predecessor']==p1].values[0]
					if p2 == predecessor:
						partition_edges.append(edge_pair)
			partition_edges += outer_node_neighbors_edges
			if len(partition_edges) < partition_size_cutoff:
				NG = nx.from_edgelist(partition_edges, create_using=nx.DiGraph)
		if NG:
			partition_index += 1
			partitions[partition_index] = NG
		partition_has_cycle, cycle = has_cycle(NG)
		connected_nodes = list(set(connected_nodes + [seed] + list(NG.nodes())))
		a = 0
		nodes_degrees = dict(NG.degree())
		isolates_count = len([n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0])
		tracker_row = [index, seed, len(set(NG.nodes())), len(set(NG.edges())), len(partition_edges),\
		            isolates_count, str(partition_has_cycle)]
		tracker.append(tracker_row)
	partitioning_tracker = pd.DataFrame(tracker, columns=['step', 'seed', 'nodes', 'edges', 'partition_edges',\
	                                            'isolates', 'has cycle'])
	return partitions, partitioning_tracker

