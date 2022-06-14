import networkx as nx
import numpy as np
import random
import sys
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from plots import *

file_path = '/home/rony/Projects_Code/Milestones_Duration/data/MWH-06-UP#13_FSW_REV.graphml'
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
nodes_degrees = list(G.degree())
degrees = [d[1] for d in nodes_degrees]
histogram_stats(degrees, 'Node degrees', 'degree', 'node_degrees.png')
nodes_in_degrees = list(G.in_degree())
degrees = [d[1] for d in nodes_in_degrees]
histogram_stats(degrees, 'Node in-degrees', 'In degree', 'node_in_degrees.png')
nodes_out_degrees = list(G.out_degree())
degrees = [d[1] for d in nodes_out_degrees]
histogram_stats(degrees, 'Node out-degrees', 'out degree', 'node_out_degrees.png')
