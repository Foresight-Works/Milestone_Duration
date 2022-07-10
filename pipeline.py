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
while terminal_nodes_tracker:
	recentWormID = get_recent_id(certificates)
	walk = wormWalk(G, recentWormID, chains_path, certificate)
	applied_certificates.append(certificate)
	chainIndex, chain = walk.grow()

	# Update results
	if chain:
		growth_tip = chain[-1]
		wormIndex = certificate[0]
		chain_str = ','.join([n.rstrip().lstrip() for n in chain])
		chains_list = list(pd.read_pickle(chains_path)['nodes'])
		if chain_str not in chains_list:
			chains_results_rows.append([wormIndex, chainIndex, chain_str])
			chains = pd.DataFrame(chains_results_rows, columns=columns)
			#print(certificate)
			#print(chains)
			chains.to_pickle(chains_path)

			growth_certificate = [wormIndex, chainIndex, growth_tip]
			certificates['growth_certificates'].append(growth_certificate)

			# Update birth_certificates with decendants' birth certificates
			birth_certificates = walk.reproduce(growth_tip)
			certificates['birth_certificates'] += birth_certificates

	# Update birth and growth certfiicates
	birth_certificates, growth_certificates = \
		certificates['birth_certificates'], certificates['growth_certificates']
	birth_certificates = [bc for bc in birth_certificates if bc not in applied_certificates]
	growth_certificates = [gc for gc in growth_certificates if gc not in applied_certificates]

	# Iteration condition
	if growth_certificates:
		certificate = growth_certificates[0]
		growth_certificates.pop(0)
		a=0
	#if growth_tip in terminal_nodes:
	elif birth_certificates:
		certificate = birth_certificates[0]
		birth_certificates.pop(0)
	terminal_nodes_tracker = [n for n in terminal_nodes if n != growth_tip]
	print('{n} chains duration='.format(n=len(chains)), round(time.time()-start, 2))

chains.to_excel('chains.xlsx', index=False)