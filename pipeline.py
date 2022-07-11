import copy
import os
import time

import pandas as pd

from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.worm_modules import *
start = time.time()

# Data
file_path = '/home/rony/Projects_Code/Milestones_Duration/data/MWH-06-UP#13_FSW_REV.graphml'
G = build_graph(file_path)

#file_path = '/home/rony/Projects_Code/Milestones_Duration/tests/data/worm_walk_demo.edgelist'
#G = nx.read_edgelist(file_path, create_using=nx.DiGraph())
Gnodes, Gedges = list(G.nodes()), G.edges()
isolates = graph_isolates(G)
print('Graph with {n} nodes and {e} edges'.format(n=len(Gnodes), e=len(Gedges)))
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)

# Initialized crawling and worms parameters
wormIndex, chainIndex = 1, 1
certificate = (wormIndex, chainIndex, root_node, list(G.successors(root_node))[0])
first_certificate = copy.deepcopy(certificate)
# Results
chains_path = os.path.join(os.getcwd(), 'results', 'chains.pkl')
columns = ['worm', 'chain', 'nodes']
chains_results_rows = [[wormIndex, chainIndex, root_node]]
chains = pd.DataFrame(chains_results_rows, columns=columns)
chains.to_pickle(chains_path)

## Walk ##
# Termination condition: all worms reached terminal nodes
growth_certificates_index, birth_certificates_index = 0, 0
certificates = {'growth_certificates': [], 'birth_certificates': [certificate]}
terminal_nodes_tracker = copy.deepcopy(terminal_nodes)
applied_certificates = []
start = time.time()
step = 0
tracker_rows = []
#while terminal_nodes_tracker:
while step < 3001:
	start1 = time.time()
	step +=1
	print(step)
	recentWormID = get_recent_id(certificates)
	walk = wormWalk(G, recentWormID, chains_path, certificate)
	applied_certificates.append(certificate)
	start = time.time()
	chainIndex, chain = walk.grow()
	growth_duration = round(time.time() - start, 3)
	# Update results
	if chain:
		growth_tip = chain[-1]
		wormIndex = certificate[0]
		chain_str = ','.join([n.rstrip().lstrip() for n in chain])
		chains_list = list(pd.read_pickle(chains_path)['nodes'])
		if chain_str not in chains_list:
			chains_results_rows.append([wormIndex, chainIndex, chain_str])
			growth_certificate = [wormIndex, chainIndex, growth_tip]
			certificates['growth_certificates'].append(growth_certificate)
			growth_to_repr_duration = round(time.time() - start, 3)
			# Update birth_certificates with decendants' birth certificates
			start = time.time()
			birth_certificates = walk.reproduce(growth_tip)
			reproduce_duration = round(time.time() - start, 3)
			certificates['birth_certificates'] += birth_certificates
		else:
			growth_duration, reproduce_duration = 0, 0
	# Update birth and growth certfiicates
	start = time.time()
	birth_certificates, growth_certificates = \
		certificates['birth_certificates'], certificates['growth_certificates']

	growth_certificates_count = len(set([str(c) for c in growth_certificates]))
	birth_certificates_count = len(set([str(c) for c in birth_certificates]))

	growth_certificates = [gc for gc in growth_certificates if gc not in applied_certificates]
	# birth_certificates = [bc for bc in birth_certificates if bc not in applied_certificates]
	update_duration = round(time.time() - start, 3)

	filtered_growth_certificates_count = len(set([str(c) for c in growth_certificates]))
	filtered_birth_certificates_count = len(set([str(c) for c in birth_certificates]))

	start = time.time()
	# Iteration condition
	if growth_certificates:
		certificate = growth_certificates[0]
		growth_certificates.pop(0)
		a = 0
	#if growth_tip in terminal_nodes:
	elif birth_certificates:
		certificate = birth_certificates[0]
		birth_certificates.pop(0)
	terminal_nodes_tracker = [n for n in terminal_nodes if n != growth_tip]
	certificate_select_duration = round(time.time() - start, 3)

	start = time.time()
	chains = pd.DataFrame(chains_results_rows, columns=columns)
	chains.to_pickle(chains_path)
	write_duration = round(time.time() - start, 3)

	step_duration = round(time.time()-start1, 3)
	chains_count = len(chains)
	processes_duration = growth_duration + growth_to_repr_duration + reproduce_duration +\
	                     update_duration + certificate_select_duration + write_duration
	diff = round(step_duration-processes_duration, 3)
	diff_ratio = round(diff/step_duration, 3)
	applied_certificates_count = len(applied_certificates)
	tracker_row = [step, growth_certificates_count, filtered_growth_certificates_count,\
	               birth_certificates_count, filtered_birth_certificates_count, applied_certificates_count, \
                   chains_count, growth_duration, growth_to_repr_duration, reproduce_duration,\
                   update_duration, certificate_select_duration, write_duration, processes_duration,\
                   step_duration, diff, diff_ratio]
	tracker_columns    = ['step', 'growth_certificates', 'filtered_growth_certificates_count',\
	              'birth_certificates', 'filtered_birth_certificates_count', 'applied_certificates', \
	              'chains', 'growthD', 'growth_to_reprD', 'reproduceD', \
	              'updateD', 'certificate_selectD', 'writeD', 'processesD', \
	              'stepD', 'step_processes_diff', 'step_processes_diff_ratio']
	tracker_rows.append(tracker_row)
	tracker_rows_df = pd.DataFrame(tracker_rows, columns=tracker_columns)
	tracker_rows_df.to_excel('chains_worms_tracker2.xlsx', index=False)