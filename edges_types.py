import os
import networkx as nx
# Graph
graphml_str = open('./data/MWH-06-UP#13_FSW_REV.graphml').read().replace('&amp;', '')
file_path = 'tmp.graphml'
with open(file_path, 'w') as f: f.write(graphml_str)
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
os.remove(file_path)
Gedges = G.edges(data=True)
edges_types = {}
for Gedge in Gedges:
	print(Gedge)
	edges_types[(Gedge[0], Gedge[1])] = Gedge[2]['Dependency']
print(edges_types)
dep_types = list(set(edges_types.values()))
print('dependency types:', dep_types)
not_FS = [t for t in list(set(edges_types.values())) if t != 'FS']
print(not_FS)