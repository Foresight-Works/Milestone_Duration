import matplotlib.pyplot as plt
import networkx as nx

# Visualize
def draw_graph(G):
	'''
	Extension to networkx/matplotlib graph drawing function, adding node names and visual properties
	:param G: Graph object
	:show: A graph plot that can be saved
	'''
	pos = nx.spring_layout(G)
	nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'), node_size=500)
	nx.draw_networkx_labels(G, pos)
	nx.draw_networkx_edges(G, pos, edge_color='r')
	nx.draw_networkx_edges(G, pos)
	plt.show()


