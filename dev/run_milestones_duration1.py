import time
import numpy as np
import networkx as nx
import pandas as pd
import sys
import os
modules_dir = '/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from nodes import *
from milestones import *
from paths import *
from evaluate import *
from parsers import *
from utils import *
data_path = '/data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
graphml_str = open(file_path).read().replace('&amp;', '')
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']

# Calculate duration
start = time.time()
data_df = parse_graphml(file_name, graphml_str, headers)
data_df.to_excel('./results/data_df.xlsx', index=False)
planned_duration = activities_duration(data_df, 'planned')
np.save('planned_duration.npy', planned_duration)
planned_duration = np.load('planned_duration.npy', allow_pickle=True)[()]
planned_duration_df = pd.DataFrame(list(zip(list(planned_duration.keys()), list(planned_duration.values()))), columns=['ID', 'planned_duration'])
planned_duration_df.to_excel('./results/duration_df.xlsx', index=False)
write_duration('Graphml parsing and duration calculation', start)

file_path = 'tmp.graphml'
with open(file_path, 'w') as f: f.write(graphml_str)
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
os.remove(file_path)

print(count_node_types(G))

# Milestone attributes keyed by task ID
milestones = milestone_nodes(G)
milestone_ids = list(milestones.keys())

# Get milestone pairs
start = time.time()
milestone_paths = list_shortest_paths_parallel(G, milestone_ids)
write_duration('list_shortest_paths', start)

print('{n} milestone_paths'.format(n=len(milestone_paths)))
if 'milestone_paths.txt' in os.listdir('../results'): os.remove('./results/milestone_paths.txt')
print('Calculating milestone durations')
start = time.time()
milestones_duration = milestones_pairs_duration(milestone_paths, planned_duration)
np.save('paired_milestones_duration.npy', milestones_duration)
write_duration('Milestone pairs identification and duration calculation', start)

print('Identify extended pairs and calculate their duration')
start = time.time()
milestone_pairs = list(milestones_duration.keys())
milestone_ids = []
for pair in milestone_pairs: milestone_ids += list(pair)
milestone_ids = list(set(milestone_ids))
print('{n} milestone pairs'.format(n=len(milestone_pairs)))
print('{n} unique milestones'.format(n=len(milestone_ids)))

start = time.time()
# Milestones and the pairs their in if they appear in more than one pair
milestones_in_pairs = {}
for id in milestone_ids:
	pairs_with_id = []
	for pair in milestone_pairs:
		if id in pair:
			pairs_with_id.append(pair)
	if len(pairs_with_id) > 1:
		milestones_in_pairs[id] = pairs_with_id

extended_milestones_duration = {}
for id, pairs in milestones_in_pairs.items():
	pairs0, pairs1 = [], []
	for pair in pairs:
		if id == pair[0]: pairs0.append(pair)
		else: pairs1.append(pair)

	# If the milestone was identified as both first and second in the pairs in which it was identified
	if pairs0 and pairs1:
		test_extended_milestones_duration = {}
		if pairs0 and pairs1:
			for pair1 in pairs1:
				for pair0 in pairs0:
					connected_duration = milestones_duration[pair0]['milestone_duration'] + milestones_duration[pair1]['milestone_duration']
					extended_milestones_duration[(pair1[0], pair0[1])] = connected_duration

write_duration('Extended pairs identification and duration calculation', start)

milestones_duration = {**milestones_duration, **extended_milestones_duration}
#for k, v in milestones_duration.items(): print(k, v)
np.save('milestones_duration.npy', milestones_duration)
