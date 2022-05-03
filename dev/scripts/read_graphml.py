import os
import sys
import networkx as nx
modules_dir = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from nodes import *
from milestones import *
from paths import *
from evaluate import *
from parsers import *
from utils import *

data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
# graphml to DataFrame
# graphml_str = open(file_path).read().replace('&amp;', '')
# headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
# data_df = parse_graphml(file_name, graphml_str, headers)
# print(data_df.head())
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
root = list(nx.topological_sort(G))[0]
print('root:', root)
print(list(G.predecessors(root)))


