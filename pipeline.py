import os
import time

import pandas as pd

from modules.config import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.encoders import *
from modules.filters import *
from modules.worm_modules import *
start = time.time()
import warnings
warnings.filterwarnings("ignore")

# Data
G = build_graph(file_path)

#file_path = '/home/rony/Projects_Code/Milestones_Duration/tests/data/worm_walk_demo.edgelist'
#G = nx.read_edgelist(file_path, create_using=nx.DiGraph())
Gnodes, Gedges = list(G.nodes()), G.edges()
isolates = graph_isolates(G)
print('Graph with {n} nodes and {e} edges'.format(n=len(Gnodes), e=len(Gedges)))
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)

# Results tables
c.execute("DROP TABLE IF EXISTS {t}".format(t=tracker_table))
c.execute("DROP TABLE IF EXISTS {t}".format(t=chains_table))

statement = build_create_table_statement('{t}'.format(t=tracker_table), tracker_cols_types)
c.execute(statement)
statement = build_create_table_statement('{t}'.format(t=chains_table), chains_cols_types)
c.execute(statement)

# Initialized crawling and worms parameters
wormIndex, chainIndex = 1, 0
certificate = (wormIndex, chainIndex, root_node, list(G.successors(root_node))[0])
# Results
chains_path = os.path.join(os.getcwd(), 'results', 'chains.pkl')
chains_results_row = [wormIndex, chainIndex, root_node, root_node, None]
statement = insert_row('{db}.chains'.format(db=db_name), chains_cols, chains_results_row)
c.execute(statement)
conn.commit()

## Walk ##
# Termination condition: all worms reached terminal nodes
growth_certificates_index, birth_certificates_index = 0, 0
certificates = {'growth_certificates': [], 'birth_certificates': [certificate]}

applied_certificates = []
start = time.time()
step = 0
tracker_rows = []
chains_built = [(0, root_node)]
chains_results_rows = []
cert_chains = []

# Pairs validation
source_path = os.path.join(results_path, 'validation', 'predecessors_successors.xlsx')
source = pd.read_excel(source_path)
source_pairs = list(zip(source['Predecessor'], source['Successor']))

start_process = time.time()
while certificate:
	error_pairs = []
	step_start = time.time()
	growth_tip = ['no tip']
	step += 1
	print(step)
	chain_built=new_chain=applied_certificates_count=\
    chains_count=start_duration=growth_duration=prep_chain_duration=write_duration=reproduce_duration=\
    update_duration=certificate_select_duration = 0
	start_duration = round(time.time() - step_start, 3)
	# Worm/Chain growth
	start = time.time()
	recentWormID = get_recent_id(certificates)
	chains_built_df = pd.DataFrame(chains_built, columns=['chain', 'nodes']).drop_duplicates(subset='nodes')
	walk = wormWalk(G, recentWormID, chains_path, certificate, chains_built_df)
	applied_certificates.append(certificate)
	chainIndex, chain = walk.grow()
	growth_duration = round(time.time() - start, 3)
	if chain:
		# Assert and prepare new chain
		start = time.time()
		chain_built = 1
		growth_tip = chain[-1]
		wormIndex = certificate[0]
		chains_count = len(chains_built)
		chain_str = '<>'.join([n.rstrip().lstrip() for n in chain])
		if (chainIndex, chain_str) not in chains_built:
			error_pairs = validate(chain, source_pairs)
			chains_built.append((chainIndex, chain_str))
			chains_count = len(chains_built)
			new_chain = 1
			chains_results_row = [wormIndex, chainIndex, chain_str] + list(certificate[2:])
			if len(chains_results_row) == 4: chains_results_row += [None]
			if len(chain) > 1:
				chains_results_rows.append(tuple(chains_results_row))
				chains_results_rows = list(set(chains_results_rows))
			prep_chain_duration = time.time()-start
			start = time.time()
			if len(chains_results_rows) == 100:
				statement = insert_rows('{db}.chains'.format(db=db_name), chains_cols, chains_results_rows)
				c.execute(statement)
				conn.commit()
				chains_results_rows = []
				write_duration = round(time.time() - start, 3)

			# Update birth_certificates with decendants' birth certificates
			start = time.time()
			birth_certificates = walk.reproduce(growth_tip)
			reproduce_duration = round(time.time() - start, 3)

			# Update birth and growth certfiicates
			start = time.time()
			growth_certificate = [(wormIndex, chainIndex, growth_tip)]
			growth_certificate = list(set(lists_filter(growth_certificate, applied_certificates)))
			birth_certificates = list(set(lists_filter(birth_certificates, applied_certificates)))
			if birth_certificates: certificates['birth_certificates'] += birth_certificates
			if growth_certificate: certificates['growth_certificates'].append(growth_certificate[0])
			if error_pairs:
				print('errors:', error_pairs)
				print('certificate:', certificate)
				print('recentWormID:', recentWormID)
				print(chains_built_df)
			update_duration = round(time.time() - start, 3)

	# Next iteration certificate
	start=time.time()
	birth_certificates, growth_certificates = \
		certificates['birth_certificates'], certificates['growth_certificates']
	if growth_certificates:
		certificate = growth_certificates[0]
		growth_certificates.pop(0)
		a = 0
	#if growth_tip in terminal_nodes:
	elif birth_certificates:
		certificate = birth_certificates[0]
		birth_certificates.pop(0)
	certificate_select_duration = time.time()-start
	# Duration tracking summation and write-up
	step_duration = round(time.time()-step_start, 3)
	processes_duration_vals = [start_duration, growth_duration, prep_chain_duration, write_duration, reproduce_duration, \
	                                                                                         update_duration, certificate_select_duration]
	processes_duration = sum(processes_duration_vals)
	diff = round(step_duration-processes_duration, 3)
	diff_ratio = round(diff/step_duration, 3)
	applied_certificates_count = len(applied_certificates)
	ratios = [round(duration_val/step_duration, 2) for duration_val in processes_duration_vals]
	
	tracker_row = [step, chain_built, new_chain, applied_certificates_count, \
                   chains_count, start_duration, growth_duration, prep_chain_duration, write_duration, reproduce_duration,\
                   update_duration, certificate_select_duration, processes_duration, step_duration, diff, diff_ratio] + ratios
	statement = insert_row('{db}.tracker'.format(db=db_name), list(tracker_cols_types.keys()), tracker_row)
	c.execute(statement)
	conn.commit()

# Write the last batch of chains
statement = insert_rows('{db}.chains'.format(db=db_name), chains_cols, chains_results_rows)
c.execute(statement)
conn.commit()