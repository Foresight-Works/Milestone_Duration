import networkx as nx
import pandas as pd

def count_node_types(G, type_key = 'TaskType'):
	'''
	Count the types of nodes in an input graph
	:param G: Graph object
	:param type_key: The key in the node attributes indexing the node type
	:return: Graph node types and their counts arranged in a table (dataframe)
	'''
	G_nodes = G.nodes()
	node_types = []
	for node in G_nodes: node_types.append(G_nodes[node][type_key])
	types_count = pd.Series(node_types).value_counts()
	types_count = pd.DataFrame(list(zip(list(types_count.index), list(types_count.values))),\
	                           columns=['Type', 'Count'])
	return types_count
