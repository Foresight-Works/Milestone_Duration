from modules.libraries import *
from modules.parsers import *
from modules.evaluate import *
from modules.graphs import *
from modules.worm_modules import *
from modules.config import *

# Data
G = build_graph(file_path)
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)

source_path = os.path.join(results_path, 'validation', 'predecessors_successors.xlsx')
source = pd.read_excel(source_path)
source_pairs = list(zip(source['Predecessor'], source['Successor']))
print('{n} source pairs; sample:'.format(n=len(source_pairs)), source_pairs[:10])

chains_df = pd.read_sql('SELECT * FROM {t}'.format(t=chains_table), con=conn)
chains = list(chains_df['nodes'])
n1, n2 = len(chains), len(set(chains))
print(chains_df.info())
print('{n1} chains | {n2} unique chains'.format(n1=n1, n2=n2))

chains_printout_path = os.path.join(results_path, 'chains.txt')
chains_str = '\n'.join(chains)
with open(chains_printout_path, 'w') as f: f.write(chains_str)

# Count terminal nodes reached
chains_lists = [c.split(',') for c in chains]
chains_terminals = list(set([c[-1] for c in chains_lists]))
terminals_in_chains = [t for t in terminal_nodes if t in chains_terminals]
terminated_chains_count = 0
for chain in chains_lists:
	if chain[-1] in terminals_in_chains:
		terminated_chains_count += 1
print('{n1} of {n2} terminal nodes reached by chains'\
      .format(n1=len(terminals_in_chains), n2=len(terminal_nodes)))
print('{n1} of {n2} chains reached a terminal node'\
      .format(n1=terminated_chains_count, n2=len(chains)))

# Validation: Chains pairs in source successor-predecessor pairs
pairs = []
for index, chain in enumerate(chains):
	#chain = [r.split(':')[0].rstrip().lstrip() for r in chain]
	chain = chain.split(',')
	chain_pairs = []
	for index, id in enumerate(chain):
		if index<len(chain)-1:
			chain_pairs.append((id, chain[index+1]))
	pairs += chain_pairs

pairs = list(set(pairs))
print('{n} pairs; sample:'.format(n=len(pairs)), pairs[:10])

pairs_in_source = [p for p in pairs if p in source_pairs]
print('{n} pairs in source; sample:'.format(n=len(pairs_in_source)), pairs_in_source[:10])

# Todo Validation: All successor-predecessor pairs in chains pairs