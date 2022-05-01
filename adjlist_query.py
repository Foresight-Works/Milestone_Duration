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

'''
'''
adjlist = read milestones_graph.adjlist
nodes_lists = the list of nodes_lists in adjlist (the neigubours for the first node in the list)
1st nodes list: iterate neighbours
for each neighbour search other nodes lists to capture the next neighbours