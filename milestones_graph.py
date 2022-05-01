import networkx as nx
import numpy as np
import sys
modules_path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_path not in sys.path: sys.path.append(modules_path)
from vizz import *

milestones_duration_dict = np.load('results/milestones_duration.npy', allow_pickle=True)[()]
milestone_pairs = list(milestones_duration_dict.keys())
print('{n} milestone pairs'.format(n=len(milestone_pairs)))
print(milestone_pairs[:10])
G = nx.DiGraph()
G.add_edges_from(milestone_pairs)
nx.write_adjlist(G, "results/milestones_graph.adjlist")
nx.write_gml(G, "results/milestones_graph.gml")
