import networkx as nx
import copy
from pyvis.network import Network
nt = Network('100%', '100%')
nt.set_options('''var options = {"nodes": {"size": 20, "shape": "triangle", "width":15,
    "font.size":"2"}, "edges":{"width":1, "font.size":"0"}}''')

def graph_to_chains(G):
	chains = []
	Gdegrees = dict(G.degree())
	top_sort = list(nx.topological_sort(G))
	root_node = top_sort[0]
	outer_nodes = [n for n in Gdegrees.keys() if ((n != root_node) & (Gdegrees[n] == 1))]
	for node in outer_nodes:
		chains += nx.all_simple_paths(G, root_node, node)
	return chains

print('single chain graph')
G1 = nx.DiGraph()
G_edges = [('N6', 'N7'), ('N2', 'N5'), ('N1', 'N2'), ('N5', 'N6')]
G1.add_edges_from(G_edges)
chains = graph_to_chains(G1)
print('chains:', chains)
nt.from_nx(G1)
nt.show('single_chain_graph.html')

print('single branch graph')
G2 = nx.DiGraph()
G_edges = [('N6', 'N7'), ('N2', 'N5'), ('N1', 'N2'), ('N5', 'N6'), ('N5', 'N8'), ('N8', 'N9')]
G2.add_edges_from(G_edges)
chains = graph_to_chains(G2)
print('chains:', chains)
nt.from_nx(G2)
nt.show('single_branch_graph.html')

print('multi branch graph')
G3 = nx.DiGraph()
G_edges = [('N1', 'N2'), ('N2', 'N3'), ('N2', 'N4'), ('N2', 'N5'), ('N5', 'N6'),\
           ('N1', 'N7'), ('N7', 'N8'), ('N8', 'N9'), ('N9', 'N10'), ('N10', 'N11'),\
           ('N7', 'N12'), ('N12', 'N13'), ('N13', 'N14'), ('N13', 'N15'),\
           ('N15', 'N16'), ('N15', 'N17')]
G3.add_edges_from(G_edges)
chains = graph_to_chains(G3)
print('chains:')
for c in chains: print(c)
nt.from_nx(G3)
nt.show('multi_branch_graph.html')




# Branched directed graph
# G = nx.DiGraph()
# G_edges = [('N1', 'N2'), ('N2', 'N3'), ('N2', 'N4'), ('N2', 'N5'), ('N5', 'N6'),\
#            ('N1', 'N7'), ('N7', 'N8'), ('N8', 'N9'), ('N9', 'N10'), ('N10', 'N11'),\
#            ('N7', 'N12'), ('N12', 'N13'), ('N13', 'N14'), ('N13', 'N15'),\
#            ('N15', 'N16'), ('N15', 'N17')]
# G.add_edges_from(G_edges)
# root = list(nx.topological_sort(G))[0]
# print('root:', root)
# print('sorted:', list(nx.topological_sort(G)))
# nx.write_edgelist(G, "directed_branched_graph.edgelist")
# nt.from_nx(G)
# nt.show('directed_branched_graph.html')
