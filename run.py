import time
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
from utils import *

working_dir = os.getcwd()
results_dir = os.path.join(working_dir, 'results')
monitor_dir = os.path.join(results_dir, 'monitor')

# Data
data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
graphml_str = open(file_path).read().replace('&amp;', '')

# Parse data
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
start = time.time()
data_df = parse_graphml(file_name, graphml_str, headers)
ids_names = dict(zip(list(data_df['ID']), list(data_df['Label'])))
ids_types = dict(zip(list(data_df['ID']), list(data_df['TaskType'])))
data_df.to_excel(os.path.join(monitor_dir, 'data_df.xlsx'), index=False)

# Calculate duration
planned_duration = activities_duration(data_df, 'planned')
np.save(os.path.join(monitor_dir, 'planned_duration.npy'), planned_duration)
planned_duration_df = pd.DataFrame(list(zip(list(planned_duration.keys()), list(planned_duration.values()))), columns=['ID', 'planned_duration'])
planned_duration_df.to_excel(os.path.join(monitor_dir, 'duration_df.xlsx'), index=False)
write_duration('Graphml parsing and duration calculation', start)

# Graph
file_path = 'tmp.graphml'
with open(file_path, 'w') as f: f.write(graphml_str)
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
os.remove(file_path)
print(count_node_types(G))

# Milestone attributes keyed by task ID
milestones = milestone_nodes(G)
milestone_ids = list(milestones.keys())

# Milestone chains
print('Milestone chains')
start = time.time()
chains = root_chains(G)
# with open(os.path.join(monitor_dir, 'chains.txt'), 'w') as f:
# 	for chain in chains: f.write('{c}\n'.format(c=', '.join(chain)))
chains = milestone_chains(chains, ids_types)
with open(os.path.join(monitor_dir, 'milestone_chains.txt'), 'w') as f:
	for chain in chains: f.write('{c}\n'.format(c=', '.join(chain)))
print('{n} chains'.format(n=len(chains)))
write_duration('Milestone chains', start)

# Milestone chains duration
print('Calculating milestone durations')
start = time.time()
milestones_duration = milestones_pairs_duration(chains, planned_duration, ids_names)
print('milestones_duration example')
first_key = list(milestones_duration.keys())[0]
print(first_key, milestones_duration[first_key])
np.save(os.path.join(results_dir, 'milestones_duration.npy', milestones_duration))
write_duration('Milestone chains duration calculation', start)


# milestones_duration_prep = {**milestones_duration, **extended_milestones_duration}
# # Add milestone name to key
# milestones_duration = {}
# for ids_pair, v in milestones_duration_prep.items():
# 	id1, id2 = ids_pair[0], ids_pair[1]
# 	name1, name2 = ids_names[id1], ids_names[id2]
# 	v['milestone_names'] = (name1, name2)
# 	milestones_duration[ids_pair] = v
#
# print('milestones_duration result')
# for k, v in milestones_duration.items(): print(k, v)
# np.save('results/milestones_duration.npy', milestones_duration)
