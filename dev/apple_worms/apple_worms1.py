import os
import pandas as pd

from modules.config import *
from modules.experiment import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *
from modules.worm_modules import *
start = time.time()

# Data
G = build_graph(file_path)
Gnodes, Gedges = list(G.nodes()), G.edges()
isolates = graph_isolates(G)
print('Graph with {n} nodes and {e} edges'.format(n=len(Gnodes), e=len(Gedges)))
root_node = list(nx.topological_sort(G))[0]
terminal_nodes = get_terminal_nodes(G)
terminal_nodes_preds = get_nodes_predecessors(G, terminal_nodes)
sum_deg = sum_nodes_predecessors(terminal_nodes)

# Initialized crawling and worms parameters
wormIndex, chainID = 0, 0
this_node = root_node
next_node = list(G.successors(root_node))[0]
anchor_chain_id = 0
birth_certificate = (wormIndex, anchor_chain_id, this_node)
progeny = [birth_certificate]

# Results
chains_path = os.path.join(os.getcwd(), 'results', 'chains.pkl')
columns = ['worm', 'chainID', 'chain_nodes', 'descendants']
chains = pd.DataFrame([[wormIndex, chainID, root_node, None]], columns=columns)
chains.to_excel(chains_path)
chains_results_rows = []
## Walk ##
# Termination condition: all worms reached terminal nodes
while sum_deg > 0:
	# Termination condition: a single worm reached a terminal node
	# A worm is starting its feeding tour
	while next_node not in terminal_nodes:
		recentWormID = get_recent_id(progeny)
		walk = wormWalk(G, recentWormID, chains_path, birth_certificate)
		chain_nodes = wormWalk.extend_chain()

		# Prepare results
		chainID += 1
		# todo: descendants are tuples, not strings
		descendants = [d[0].rstrip().lstrip() for d in descendants]
		descendants = ','.join(descendants)
		chains_results_rows.append([wormIndex, chainID, root_node, descendants])
		chains = pd.DataFrame(chains_results_rows, columns=columns)
		chains.to_excel(chains_path)

		# Update progeny
		descendants = wormWalk.reproduce()
		progeny += descendants
		# todo: update step node
		next_node = list(G.successors(root_node))[0]

	# When a worm has finished its tour
	wormIndex += 1
	wormIndex = 'W{wi}'.format(wi=wormIndex)
	terminal_nodes_preds[next_node] -= 1
	if (terminal_nodes_preds[next_node])==0:
		del terminal_nodes_preds[next_node]
	sum_deg = sum_nodes_predecessors(terminal_nodes)

	# Select a descendant to run its tour
	descendant = progeny[0]
	progeny.pop(descendant)
	birth_certificate = descendant
