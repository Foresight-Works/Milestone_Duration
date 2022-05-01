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

def get_longest_path(element, paths):
	'''
	Identify the longest path containing a element of nodes
	A path contains a element of nodes if the nodes are in the path 
	The longest path from the paths containing the element of nodes, is the path in which the gap between  
	nodes (=the numebr of intermediate nodes) is the longest
	:param element: Query name element
	:param paths: Sequences of nodes
	:return: The longest sequence containing the nodes element
	'''
	print(paths[0])
	print(30*'=')
	print('element:', element, type(element))
	if type(element) == str:
		print('1')
		paths_with_element = [path for path in paths if element in path]
	else: paths_with_element = [path for path in paths if set(element).issubset(path)]
	for p in paths_with_element: print(p)
	paths_lengths = [len(p) for p in paths_with_element]
	print('paths_lengths:', paths_lengths)
	longest_path_length = max(paths_lengths)
	longest_path = [p for p in paths_with_element if len(p) == longest_path_length][0]
	print('longest_path:', longest_path)
	
	return longest_path

pairs = list(milestones_paths.values())
paths = list(milestones_paths.values())
#paths_lengths = [len(p) for p in paths]
#print(paths_lengths)
elements = []
for pair in pairs: elements += pair
elements = list(set(elements))
print('{n} elements, sample:'.format(n=len(elements)), elements[:10])

start = time.time()
for element in elements: longest_path = get_longest_path(element, paths)
#for pair in pairs: longest_path = get_longest_path(pair, paths)
write_duration('process', start)
