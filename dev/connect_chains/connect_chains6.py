from modules.libraries import *
from modules.config import *
from modules.graphs import *
from modules.splitgraph import *
from modules.vizz import *
from modules.chains import *
start = time.time()

chains = []
files = ['chains1.pkl', 'chains2.pkl', 'chains3.pkl']
for file in files:
	path = os.path.join(experiment_path, file)
	file_chains = read_chains(path, how='pickle')
	chains += file_chains
chains1 = list(set(chains))
#chains = chains[:100]
chains = []
for chain in chains1:
	chain = chain.split(',')
	chain = [e.rstrip().lstrip() for e in chain]
	chains.append(chain)

## Connect chains
chains_start, chains_end = build_chains_terminals_dicts(chains)
start_nodes, end_nodes = list(set(chains_start.values())), list(set(chains_end.values()))
es_pairs = list(x for x in itertools.product(end_nodes, start_nodes))
edge_relations = predecessors_successors(file_path)
predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])
zipper = list(zip(predecessors, successors))

# chains_dict = {}
# for index, chain in enumerate(chains): chains_dict[index] = chain
# chains_keys = list(chains_dict.keys())
# chains_pairs = list(set(combinations(chains_keys, 2)))



# todo: chains concatenation cycles
start = time.time()
print('connecting chains')
next_step = True
step_pairs = ['start']
while step_pairs:
	step_pairs = []
	chains_start, chains_end = build_chains_terminals_dicts(chains)
	for chain1, end_node in chains_end.items():
		#print(chain1)
		for chain2, start_node in chains_start.items() :
			#print(chain1, chain2)
			end_start = (end_node, start_node)
			if end_start in zipper:
				step_pairs.append(end_start)
				connected_chain = list(chain1 + chain2)
				#print('connected chain:', connected_chain)
				chains.append(connected_chain)
				print('chains count=',len(chains))
	a=0