def get_terminals(node_indexed_graphs):
	node, indexed_graphs = node_indexed_graphs
	node_graphs = []
	for index, graph in indexed_graphs.items():
		if node in graph_terminals(graph):
			node_graphs.append(index)
	return node, node_graphs

def build_terminals_graphs_dict(indexed_graphs):
	nodes = graphs_nodes(list(indexed_graphs.values()))
	nodes_indexed_graphs = [(node, indexed_graphs) for node in nodes]
	terminals_graphs = {}
	executor = ProcessPoolExecutor(10)
	for node, node_graphs in executor.map(get_terminals, nodes_indexed_graphs):
		terminals_graphs[node] = node_graphs
	#executor.shutdown()
	terminals_graphs = {k: v for k, v in terminals_graphs.items() if len(v)>1}
	return terminals_graphs