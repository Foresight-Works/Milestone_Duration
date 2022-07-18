import os

import pandas as pd

from modules.config import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.encoders import *
from modules.filters import *
from modules.worm_modules2 import *
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
first_certificate = copy.deepcopy(certificate)
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
terminal_nodes_tracker = copy.deepcopy(terminal_nodes)
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
def validate(chain):
	if chain:
		pairs = []
		chain_pairs = []
		for index, id in enumerate(chain):
			if index<len(chain)-1:
				chain_pairs.append((id, chain[index+1]))
		pairs += chain_pairs
		pairs = list(set(pairs))
		pairs_in_source = [p for p in pairs if p in source_pairs]
		error_pairs = list(set(pairs).difference(set(pairs_in_source)))
	else:
		error_pairs = []
	return error_pairs

while terminal_nodes_tracker:
	pointer_node = certificate[-1]
	step += 1
	start1 = time.time()
	chain_built, new_chain, applied_certificates_count, \
    chains_count, growth_duration, write_duration, reproduce_duration,\
    update_duration = 0, 0, 0, 0, 0, 0, 0, 0
	print(step)


	# Worm/Chain growth
	recentWormID = get_recent_id(certificates)
	chains_built_df = pd.DataFrame(chains_built, columns=['chain', 'nodes']).drop_duplicates(subset='nodes')
	walk = wormWalk(G, recentWormID, chains_path, certificate, chains_built_df)
	applied_certificates.append(certificate)
	#with open('applied_certificates.txt', 'w') as f: f.write('\n'.join([str(c) for c in applied_certificates]))
	start = time.time()
	chainIndex, chain = walk.grow()
	growth_duration = round(time.time() - start, 3)
	if chain:
		chain_built = 1
		growth_tip = chain[-1]
		wormIndex = certificate[0]
		chains_count = len(chains_built)
		chain_str = '<>'.join([n.rstrip().lstrip() for n in chain])

		#cert_chains.append((certificate, chain_str))
		#pd.DataFrame(cert_chains, columns=['certificate', 'chain']).to_excel('certificates_chains.xlsx', index=False)
		if (chainIndex, chain_str) not in chains_built:
			chains_built.append((chainIndex, chain_str))
			new_chain = 1
			chains_results_row = [wormIndex, chainIndex, chain_str] + list(certificate[2:])
			if len(chains_results_row) == 4: chains_results_row += [None]
			if len(chain) > 1:
				chains_results_rows.append(tuple(chains_results_row))
				chains_results_rows = list(set(chains_results_rows))
			if len(chains_results_rows) == 100:
				statement = insert_rows('{db}.chains'.format(db=db_name), chains_cols, chains_results_rows)
				c.execute(statement)
				conn.commit()
				chains_results_rows = []

			growth_certificate = (wormIndex, chainIndex, growth_tip)
			certificates['growth_certificates'].append(growth_certificate)
			write_duration = round(time.time() - start, 3)
			# Update birth_certificates with decendants' birth certificates
			start = time.time()
			birth_certificates = walk.reproduce(growth_tip)
			reproduce_duration = round(time.time() - start, 3)
			certificates['birth_certificates'] += birth_certificates
			chains_count = len(chains_built)

	# Update birth and growth certfiicates
	start = time.time()
	birth_certificates, growth_certificates = \
		certificates['birth_certificates'], certificates['growth_certificates']

	growth_certificates_count = len(set([str(c) for c in growth_certificates]))
	birth_certificates_count = len(set([str(c) for c in birth_certificates]))

	#todo: birth_cetificate filtering reumed
	growth_certificates = list(set(lists_filter(growth_certificates, applied_certificates)))
	birth_certificates = list(set(lists_filter(birth_certificates, applied_certificates)))
	update_duration = round(time.time() - start, 3)

	filtered_growth_certificates_count = len(set([str(c) for c in growth_certificates]))
	filtered_birth_certificates_count = len(set([str(c) for c in birth_certificates]))

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
	step_duration = round(time.time()-start1, 3)
	processes_duration = growth_duration + write_duration + reproduce_duration +\
	                     update_duration
	diff = round(step_duration-processes_duration, 3)
	diff_ratio = round(diff/step_duration, 3)
	applied_certificates_count = len(applied_certificates)
	tracker_row = [step, chain_built, new_chain, growth_certificates_count, filtered_growth_certificates_count,\
	               birth_certificates_count, filtered_birth_certificates_count, applied_certificates_count, \
                   chains_count, growth_duration, write_duration, reproduce_duration,\
                   update_duration, processes_duration, step_duration, diff, diff_ratio]
	statement = insert_row('{db}.tracker'.format(db=db_name), list(tracker_cols_types.keys()), tracker_row)
	c.execute(statement)
	conn.commit()