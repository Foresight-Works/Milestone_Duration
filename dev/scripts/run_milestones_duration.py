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
data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
graphml_str = open(file_path).read().replace('&amp;', '')
file_path = 'tmp.graphml'
with open(file_path, 'w') as f: f.write(graphml_str)
G = nx.read_graphml(file_path)
G = nx.DiGraph(G)
os.remove(file_path)


# Calculate duration
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
start = time.time()
data_df = parse_graphml(file_name, graphml_str, headers)
ids_names = dict(zip(list(data_df['ID']), list(data_df['Label'])))
data_df.to_excel('./results/data_df.xlsx', index=False)
planned_duration = activities_duration(data_df, 'planned')
np.save('results/planned_duration.npy', planned_duration)
planned_duration_df = pd.DataFrame(list(zip(list(planned_duration.keys()), list(planned_duration.values()))), columns=['ID', 'planned_duration'])
planned_duration_df.to_excel('./results/duration_df.xlsx', index=False)
write_duration('Graphml parsing and duration calculation', start)


print(count_node_types(G))

# Milestone attributes keyed by task ID
milestones = milestone_nodes(G)
milestone_ids = list(milestones.keys())

# Get milestone pairs
start = time.time()
milestone_paths = list_shortest_paths_parallel(G, milestone_ids)
'''
* milestone_path example * 
('MWH06.C2.E1330', 'MWH-06-01-SSC-F'): 
	['MWH06.C2.E1330', 'MWH06.C2.C4190', 'MWH06.C2.C4340', 'MWH06-C2.P1800', 'MWH.06.M1010', 'MWH06.C1.Cx4000', 'MWH06.C1.Cx4010', 'MWH-06-01-SSC-F']
'''
print('{n} milestone_paths'.format(n=len(milestone_paths)))
write_duration('list_shortest_paths', start)
print('Calculating milestone durations')
start = time.time()
milestones_duration = milestones_pairs_duration(milestone_paths, planned_duration, ids_names)
print('milestones_duration example')
first_key = list(milestones_duration.keys())[0]
print(first_key, milestones_duration[first_key])
np.save('results/paired_milestones_duration.npy', milestones_duration)
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

# Collect ids for milestones that appear in two milestone pairs and the pairs in which it appears
milestones_in_pairs = {}
for id in milestone_ids:
	pairs_with_id = []
	for pair in milestone_pairs:
		if id in pair:
			pairs_with_id.append(pair)
	if len(pairs_with_id) > 1:
		milestones_in_pairs[id] = pairs_with_id

# Calculate the duration for extended pairs (pairs with 1+ intermediate milestones)
extended_milestones_duration = {}
for id, pairs in milestones_in_pairs.items():
	pairs0, pairs1 = [], []
	for pair in pairs:
		if id == pair[0]: pairs0.append(pair)
		else: pairs1.append(pair)

	# If the milestone was identified as both first and second in the pairs in which it was identified
	if pairs0 and pairs1:
		result_dict = {}
		for pair1 in pairs1:
			tasks_duration1 = milestones_duration[pair1]['tasks_duration']
			for pair0 in pairs0:
				tasks_duration0 = milestones_duration[pair0]['tasks_duration']
				tasks_duration = {**tasks_duration1, **tasks_duration0}
				connected_duration = milestones_duration[pair0]['milestone_duration'] + milestones_duration[pair1]['milestone_duration']
				extended_milestones_duration[(pair1[0], pair1[1])]\
					= {'milestone_duration': connected_duration, 'tasks_duration': tasks_duration}

write_duration('Extended pairs identification and duration calculation', start)
np.save('results/milestones_duration.npy', milestones_duration)
np.save('results/extended_milestones_duration.npy', extended_milestones_duration)

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
