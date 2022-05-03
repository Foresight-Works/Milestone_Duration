import networkx as nx
import numpy as np
import sys
import time

modules_dir = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from paths import *
from utils import *
G = nx.read_adjlist('./results/milestones_graph.adjlist')
Gnodes = G.nodes()
print('{n} nodes'.format(n=len(Gnodes)))
start = time.time()
connected_milestones = list_shortest_paths_parallel(G, Gnodes)#, num_pairs=1000)
#print('connected_milestones:', connected_milestones)

np.save('./results/connected_milestones_paths.npy', connected_milestones)
write_duration('Milestones pairs paths calculation', start)
