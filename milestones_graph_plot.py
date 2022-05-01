import time
import numpy as np
import sys
import networkx as nx
from pyvis.network import Network
modules_path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_path not in sys.path: sys.path.append(modules_path)
modules_dir = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from utils import *
from vizz import *

milestones_duration_dict = np.load('results/old/paired_milestones_duration.npy', allow_pickle=True)[()]
milestone_pairs = list(milestones_duration_dict.keys())
print('{n} milestone pairs'.format(n=len(milestone_pairs)))
print(milestone_pairs[:10])
G = nx.Graph()
G.add_edges_from(milestone_pairs)
nx.write_adjlist(G, "results/old/milestones_graph.adjlist")
nt = Network('100%', '100%')
# populates the nodes and edges data structures
nt.from_nx(G)
start = time.time()
nt.show_buttons()
nt.show('./results/milestones_graph.html')
write_duration('Plotting took', start)
#draw_graph(G)
