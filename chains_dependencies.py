'''
Add the dependency information to the links between graph chains
'''
start = time.time()
# params
file_path = os.path.join(os.getcwd(), 'data/MWH-06-UP#13_FSW_REV.graphml')
print(file_path)

# Graph
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
Gnodes, Gedges = list(G.nodes()), G.edges()
graph_nodes_count = len(G.nodes())
size_threshold = 50 # int(len(G.nodes)/15)

# Isolates
nodes_degrees = dict(G.degree())
source_isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n] == 0]

Edges dependency
edges_dependency = {}
for Gedge in Gedges:
	edges_dependency[frozenset((Gedge[0], Gedge[1]))] = Gedge[2]['Dependency']
graph_no_isolates_nodes_count = len(set(G.nodes()))

print('{n} graph nodes | size threshold = {t}'.format(n=len(G.nodes()), t=size_threshold))
