import os
from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.worm_modules import *
start = time.time()

# Data
# file_path = '/home/rony/Projects_Code/Milestones_Duration/data/MWH-06-UP#13_FSW_REV.graphml'
# G = build_graph(file_path)

file_path = '/home/rony/Projects_Code/Milestones_Duration/tests/data/worm_walk_demo.edgelist'
G = nx.read_edgelist(file_path, create_using=nx.DiGraph())
Gnodes, Gedges = list(G.nodes()), G.edges()
isolates = graph_isolates(G)
print('Graph with {n} nodes and {e} edges'.format(n=len(Gnodes), e=len(Gedges)))
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)

# Initialized crawling and worms parameters
wormIndex, chainIndex = 1, 1
this_node = root_node
next_node = list(G.successors(root_node))[0]
birth_certificate = (wormIndex, chainIndex, this_node)
progeny = [birth_certificate]

# Results
chains_path = os.path.join(os.getcwd(), 'results', 'chains.pkl')
columns = ['worm', 'chain', 'nodes']
chains = pd.DataFrame([[wormIndex, chainIndex, root_node]], columns=columns)
chains.to_pickle(chains_path)
chains_results_rows = []
## Walk ##
# Termination condition: all worms reached terminal nodes
graveyard = [(1, 1, 'N1')]
while progeny:
	# Termination condition: a single worm reached a terminal node
	# A worm is starting its feeding tour
	while next_node not in terminal_nodes:
		recentWormID = get_recent_id(progeny)
		walk = wormWalk(G, recentWormID, chains_path, birth_certificate)
		birth_certificate, chain = walk.grow()
		graveyard.append(birth_certificate)

		# Update results
		wormIndex, chainIndex = birth_certificate[:2]
		chain_str = ','.join([n.rstrip().lstrip() for n in chain])
		chains_results_rows.append([wormIndex, chainIndex, chain_str])
		chains = pd.DataFrame(chains_results_rows, columns=columns)
		chains.to_pickle(chains_path)

		# Update progeny
		descendants = walk.reproduce()
		progeny += descendants
		# todo: update step node
		last_node = chain[-1]
		successors = list(G.successors(last_node))
		if successors:
			next_node = list(successors)[0]
			k = 1
		else:
			next_node = terminal_nodes[0]
		a = 0

	# Append terminal node
	if successors:
		walk = wormWalk(G, recentWormID, chains_path, birth_certificate)
		birth_certificate, chain = walk.grow()
		#descendants = walk.reproduce()
		wormIndex, chainIndex = birth_certificate[:2]
		chain_str = ','.join([n.rstrip().lstrip() for n in chain])
		chains_results_rows.append([wormIndex, chainIndex, chain_str])
		chains = pd.DataFrame(chains_results_rows, columns=columns)
		chains.to_pickle(chains_path)
	b = 0

	# Select a descendant to run its tour
	if progeny:
		progeny = [bc for bc in progeny if bc not in graveyard]
		descendant = progeny[0]
		birth_certificate = descendant
		progeny.pop(0)
		next_node = descendant[2]
	c = 0

print(chains)
chains.to_excel('chains.xlsx', index=False)