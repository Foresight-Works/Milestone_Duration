import time
import os
import sys
import pandas as pd
import numpy as np
import mysql.connector as mysql

modules_path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if modules_path not in sys.path: sys.path.append(modules_path)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from modules.utils import *
from parsers import *
from evaluate import *
from milestones import *
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()

# Milestone chains
start = time.time()
c.execute("SELECT chain FROM milestone_chains;")
milestone_chains = [i[0] for i in c.fetchall()]
# with open('milestone_chains.txt', 'w') as f:
# 	for chain in milestone_chains: f.write('{c}\n'.format(c=chain))
write_duration('read results', start)
print('{n2} milestone chains'.format(n2=len(milestone_chains)))
milestone_chains = [c.split('<>') for c in milestone_chains]
sample = [c for c in milestone_chains if len(c)>4]
ms_print = ['<>'.join(c) for c in sample]
for c in ms_print[:10]: print(c)

# Tasks metadata
# data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
# file_name = 'MWH-06-UP#13_FSW_REV.graphml'
# file_path = os.path.join(data_path, file_name)
# graphml_str = open(file_path).read().replace('&amp;', '')
# # Parse data
# headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
# start = time.time()
# data_df = parse_graphml(file_name, graphml_str, headers)
# data_df.to_excel('data_df.xlsx', index=False)
data_df = pd.read_excel('data_df.xlsx')
# Dates

print(data_df.info())

results_dir = '/home/rony/Projects_Code/Milestones_Duration/results/duration'
## Milestone chains duration
for index, milestone_chain in enumerate(sample):
	chain_df = milestones_achievement_duration(milestone_chain, data_df)
	file_path = os.path.join(results_dir, 'chain_{i}.xlsx'.format(i=index+1))
	chain_df.to_excel(file_path, index=False)
