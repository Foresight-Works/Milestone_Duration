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

edge_relations = predecessors_successors(file_path)
predecessors, successors = list(edge_relations['predecessor']), list(edge_relations['successor'])
zipper = list(zip(predecessors, successors))

# todo: chains concatenation cycles
start = time.time()
print('connecting chains')
next_step = True
chain_pairs = ['start']
step = 0
while chain_pairs:
	step += 1
	print(step, len(chains))
	chains_start, chains_end = build_chains_terminals_dicts(chains)
	start_nodes, end_nodes = list(set(chains_start.values())), list(set(chains_end.values()))
	es_pairs1 = list(x for x in itertools.product(end_nodes, start_nodes))
	es_pairs = []
	for e in es_pairs1:
		if e[0] != e[1]:
			es_pairs.append(e)
	for es_pair in es_pairs:
		end_node, start_node = es_pair
		start_chains = [chain for chain, chain_end in chains_end.items() if chain_end == end_node]
		end_chains = [chain for chain, chain_start in chains_start.items() if chain_start == start_node]
		chain_pairs = list(x for x in itertools.product(start_chains, end_chains))
		chain_pairs = [(chain[0]+chain[1]) for chain in chain_pairs]
		chains += chain_pairs
		print(len(chains))

path = os.path.join(experiment_path, 'chains4.pkl')
write_chains(chains, path)
duration = str(time.time()-start)
with open('duration.txt', 'w') as f: f.write(duration)
print('connect chains duration=', duration)