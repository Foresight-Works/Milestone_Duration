import os
import time
import numpy as np
import networkx as nx
from pyvis.network import Network
nt = Network('100%', '100%')
nt.set_options('''var options = {"nodes": {"size": 20, "shape": "triangle", "width":15,
    "font.size":"2"}, "edges":{"width":1, "font.size":"0"}}''')
partitions_chains = np.load('partitions_chains1.npy', allow_pickle=True)[()]

# Graph
file_path = os.path.join(os.getcwd(), 'data/MWH-06-UP#13_FSW_REV.graphml')
G = nx.read_graphml(file_path)
Gnodes = list(G.nodes())
graph_nodes_count = list(set(Gnodes))

# Nodes from graphs that produced and the graphs that did not produce chains
partitions_graphs_nodes, chains_in_partitions, partitions_chains_nodes = [], [], []
for graph, chains in partitions_chains.items():
	graph_nodes = list(graph.nodes())
	if chains:
		partitions_graphs_nodes += graph_nodes
		chains_in_partitions += chains
		for chain in chains:
			partitions_chains_nodes += chain

partitions_graphs_nodes, partitions_chains_nodes = set(partitions_graphs_nodes), set(partitions_chains_nodes)
nodes_intersection = partitions_chains_nodes.intersection(partitions_graphs_nodes)
partitions_graphs_nodes_count = len(partitions_graphs_nodes)
partitions_chains_nodes_count = len(partitions_chains_nodes)

#graphs_nodes_not_chains = [n for n in ]

# Populate a chain to graph dictionary
start = time.time()

## Isolates
# Nodes without neighbors in the source graph
source_isolates = []
for node in Gnodes:
	neighbors = list(G.neighbors(node)) + list(G.predecessors(node)) + list(G.successors(node))
	if not neighbors: source_isolates.append(node)
# Nodes not captured in chains
chain_isolates = [n for n in Gnodes if n not in partitions_graphs_nodes]
chain_isolates_count = len(set(chain_isolates))
source_isolates_count = len(set(source_isolates))

# Filter chain isolates of source isolates
isolates = [i for i in chain_isolates if i not in source_isolates]
filtered_isolates_count = len(set(isolates))
k = 0
isolates_neighbours, neighbors_chains, chains_graph, isolates_graphs = {}, {}, {}, {}
neighbors = []

# Collect isolates' neighbors in the Graph
for isolate in isolates:
	isolates_neighbours[isolate] =\
		list(G.neighbors(isolate)) + list(G.predecessors(isolate)) + list(G.successors(isolate))
	neighbors += isolates_neighbours[isolate]
# Identify a chain for each neighbor and the graph for this chain
a = 0
for neighbor in neighbors:
	for graph, chains in partitions_chains.items():
		for chain in chains:
			if neighbor in chain:
				neighbors_chains[neighbor] = chain
				chains_graph[tuple(chain)] = graph
isolates_chains = []
# Rebuild chains to include isolates
exceptions = []
for index, isolate in enumerate(isolates):
	print(index)
	# Select a neighbor from the isolate neighbors
	isolate_neighbors = isolates_neighbours[isolate]
	isolate_neighbors = [n for n in isolate_neighbors if n in list(neighbors_chains.keys())]
	if isolate_neighbors:
		for isolate_neighbor in isolate_neighbors:
			# Identify a chain for the neighbor selected and the graph used to identify this chain
			neighbor_chain = neighbors_chains[isolate_neighbor]
			neighbor_graph = chains_graph[tuple(neighbor_chain)]

			# Concatenate the isolate to the graph via its neighbor
			neighbor_graph.add_edge(isolate_neighbor, isolate, weight=1)
			# nt.from_nx(neighbor_graph)
			# nt.show('neighbor_isolate_graph.html')

			# Identify the outer nodes in neighbor_graph
			nodes_degrees = dict(neighbor_graph.degree())
			outer_nodes = [n for n in nodes_degrees.keys() if nodes_degrees[n] == 1]
			# Connect the isolate to each of the other outer nodes
			targets = [n for n in outer_nodes if n != isolate]
			for target in targets:
				# Identify a chain between the isolate and the target
				isolate_chain = nx.shortest_path(neighbor_graph, source=isolate, target=target)
				isolates_chains.append(isolate_chain)
				a=0
	else:
		exceptions.append(isolate)
print('{n} exceptions'.format(n=len(exceptions)))
print('{n} chains rebuilt'.format(n=len(isolates_chains)))

chains = chains_in_partitions + isolates_chains
partitions_graphs_nodes = []
for chain in chains:
	partitions_graphs_nodes += chain
	a = 0
partitions_graphs_nodes = [c for c in list(set(partitions_graphs_nodes)) if c not in source_isolates]
print('{n1} chains using {n2} nodes'.format(n1=len(chains), n2=len(set(partitions_graphs_nodes))))
print('{n1} nodes unaccounted for'.format(n1= len(set(Gnodes)) - len(partitions_graphs_nodes) - len(source_isolates)))
unaccounted = [i for i in Gnodes if i not in (partitions_graphs_nodes+source_isolates)]
a = set(unaccounted).intersection(set(neighbors))
chains_str = [','.join(chain) for chain in chains]
chains_str = '\n'.join(chains_str)
with open('isolates_chains_chains.txt', 'w') as f: f.write(chains_str)
print('handling isolates duration=', time.time()-start)