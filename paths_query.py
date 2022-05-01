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

milestones_paths = np.load('results/connected_milestones_paths.npy', allow_pickle=True)[()]

def path_by_pairs (pair, pairs):
	'''
	Query a set of paired elements to identify elements that are neighbours of the pair query elements
	If a neighbour to an element is identified, extend the query by the neighbour
	:param pair:
	:param pairs:
	:return:
	'''


pairs = list(milestones_paths.values())
elements = []
for pair in pairs: elements += pair
elements = list(set(elements))
print('{n} elements, sample:'.format(n=len(elements)), elements[:10])

start = time.time()
for element in elements: longest_path = get_longest_path(element, paths)
#for pair in pairs: longest_path = get_longest_path(pair, paths)
write_duration('process', start)
