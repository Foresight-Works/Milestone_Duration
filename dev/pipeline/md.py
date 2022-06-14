import time
import numpy as np
import networkx as nx
import pandas as pd
import sys
import os
import mysql.connector as mysql
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()

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
validation_dir = os.path.join(results_dir, 'validation')

start = time.time()
c.execute("SELECT chain FROM milestone_chains;")
chains = [i[0] for i in c.fetchall()]
write_duration('Milestone chains read', start)

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
