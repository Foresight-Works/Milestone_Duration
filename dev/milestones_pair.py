import numpy as np
import networkx as nx
import pandas as pd
import sys
import os
modules_dir = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from nodes import *
from milestones import *
from paths import *
from evaluate import *
from parsers import *
data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
graphml_str = open(file_path).read().replace('&amp;', '')
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']

# Calculate duration
data_df = parse_graphml(file_name, graphml_str, headers)
data_df.to_excel('data_df.xlsx', index=False)
planned_duration = activities_duration(data_df, 'planned')
planned_duration_df = pd.DataFrame(list(zip(list(planned_duration.keys()), list(planned_duration.values()))), columns=['ID', 'planned_duration'])
# todo:  using planned duration, add actual if needed
planned_duration_df.to_excel('planned_duration.xlsx', index=False)
# actual_duration = activities_duration(data_df, 'actual')
# actual_duration_df = pd.DataFrame(list(zip(list(actual_duration.keys()), list(actual_duration.values()))), columns=['ID', 'actual_duration'])
# planned_actual = pd.merge(planned_duration_df, actual_duration_df, how='outer')
# data_duration_df = pd.merge(data_df, planned_actual)
# #data_duration_df.to_excel('data_duration_df.xlsx', index=False)

file_path = 'tmp.graphml'
with open(file_path, 'w') as f: f.write(graphml_str)
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
os.remove(file_path)
#types_count = count_node_types(G)
#print(types_count)
'''
  Type  Count
0     TT_Task   4464
1  TT_FinMile   1467
2     TT_Mile   1302
2769 milestones
3832296 node pairs
'''

# Milestone attributes keyed by task ID
milestones = milestone_nodes(G)
milestone_ids = list(milestones.keys())

# Get milestone pairs
milestone_paths = list_shortest_paths(G, milestone_ids)
print('{n} milestone_paths'.format(n=len(milestone_paths)))
milestones_duration = {}
for milestones_pair, inter_milestone_tasks in milestone_paths.items():
	milestone_duration = 0
	print(60*'=')
	print('Milestones:', milestones_pair)
	for task_id in inter_milestone_tasks:
		task_duration = planned_duration[task_id]
		print(task_id, task_duration)
		milestone_duration += task_duration
	print('Milestone Duration=', milestone_duration)
	milestones_duration[milestones_pair] = milestone_duration
np.save('milestones_duration.npy', milestones_duration)