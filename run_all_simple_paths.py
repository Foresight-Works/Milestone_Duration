import os
#from itertools import combinations
import time

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
chains = []
for p1, p2 in nodes_combinations:
	print(p1, p2)
	start = time.time()
	pair_chains = list(nx.all_simple_paths(G, p1, p2))
	print('{n} pair chains produced in {t} seconds'.format(n=len(pair_chains), t=time.time()-start))
	chains += pair_chains
	print(pair_chains)