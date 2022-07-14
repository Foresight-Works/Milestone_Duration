import os
#from itertools import combinations
import time

import networkx as nx
import numpy as np

from modules.config import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.encoders import *
from modules.worm_modules import *
start = time.time()
import warnings
warnings.filterwarnings("ignore")

from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("The run started on", current_time)

# Data
G = build_graph(file_path)

#file_path = '/home/rony/Projects_Code/Milestones_Duration/tests/data/worm_walk_demo.edgelist'
#G = nx.read_edgelist(file_path, create_using=nx.DiGraph())
Gnodes, Gedges = list(G.nodes()), G.edges()
isolates = graph_isolates(G)
print('Graph with {n} nodes and {e} edges'.format(n=len(Gnodes), e=len(Gedges)))
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)

Gnodes = list(set(Gnodes).difference(isolates))
print('{n} none-isolate nodes'.format(n=len(Gnodes)))
#nodes_combinations = list(set(combinations(Gnodes, 2)))

nodes_combinations = [(root_node, terminal_node) for terminal_node in terminal_nodes]
def remove_path(G, path):
	sp = []
	for i in range(0, len(path) - 1):
		sp.append((path[i], path[i + 1]))
	for u, v in sp:
		G.remove_edge(u, v)
	return G

shortest_paths, no_paths_pairs = [], []
for index, pair in enumerate(nodes_combinations):
	root, terminal = pair
	start = time.time()
	pair_shortest_paths = []
	while nx.has_path(G, root, terminal):
		pair_shortest_path = nx.shortest_path(G, source=root, target=terminal)
		pair_shortest_paths.append(pair_shortest_path)
		G = remove_path(G, pair_shortest_path)
	if pair_shortest_paths:
		shortest_paths += pair_shortest_paths
		print(30*'+')
		print(index, pair)
		print(len(pair_shortest_paths), len(shortest_paths))
		#for path in pair_shortest_paths: print(path)
	else:
		no_paths_pairs.append(terminal)
paths_count = len(shortest_paths)
shortest_paths = [','.join(p) for p in shortest_paths]
shortest_paths = list(set(shortest_paths))
results = []
for index, path_nodes in enumerate(shortest_paths):
	results.append([index, path_nodes])
chains_df = pd.DataFrame(results, columns=['chain', 'nodes'])
chains_df.to_excel(os.path.join(results_path, 'shortest_path_chains.xlsx'), index=False)
#print(chains_df)
shortest_paths = '\n'.join(shortest_paths)
with open(os.path.join(results_path, 'shortest_path_chains.txt'), 'w') as f: f.write(shortest_paths)

print('{n} shortest paths identified'.format(n=paths_count))
print('{n1} of {nt} terminals nodes have no path to the root:\n'.format(n1=len(no_paths_pairs), nt=len(terminal_nodes)), no_paths_pairs)
with open(os.path.join(results_path, 'terminals_no_path_to_root.txt'), 'w') as f: f.write('\n'.join(no_paths_pairs))
#print('shortest path produced in {t} seconds'.format(t=time.time()-start))
