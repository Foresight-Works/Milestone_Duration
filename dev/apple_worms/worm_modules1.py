import pandas as pd

from modules.libraries import *
from modules.graphs import *
class wormWalk:
	def __init__(self, G, recentWormID, chains_path, birth_certificate):
		self.wormIndex = birth_certificate[0]
		self.anchor_chain_id = birth_certificate[1]
		self.start_node = birth_certificate[2]
		self.graph = G
		self.successors = list(G.successors(self.start_node))
		self.chains_path = chains_path
		self.recentWormID = recentWormID

	def previous_step_chain(self):
		chains_df = pd.read_pickle(self.chains_path)
		worm_chains = list(chains_df['chain_nodes'][chains_df['worm'] == self.wormIndex]['chain_nodes'])
		return max(worm_chains, key=len).split(',')

	def extend_chain(self):
		chain_id = self.anchor_chain_id + 1
		next_node = self.successors[0]
		chain = wormWalk.previous_step_chain() + [next_node]
		return (chain_id, chain)

	def reproduce(self):
		descendants = []
		chain_id = self.anchor_chain_id + 1
		wormID = self.recentWormID
		for descendant_start_node in self.successors:
			wormID = wormID + 1
			birth_certificate = (wormID, chain_id, descendant_start_node)
			descendants.append(birth_certificate)
		return descendants

# The degree of terminal nodes as terminal nodes coverage indicator
def get_terminal_nodes(G):
	Gnodes = list(G.nodes())
	isolates = graph_isolates(G)
	return [n for n in Gnodes if ((G.out_degree(n) == 0) & (n not in isolates))]

def get_nodes_predecessors(G, nodes):
	nodes_preds = [G.predecessors(n) for n in nodes]
	return dict(zip(nodes, nodes_preds))

def sum_nodes_predecessors(nodes_preds):
	return sum(list(nodes_preds.values()))

def get_recent_id(progeny):
	'''
	Return the ID for the last decendant born
	:param progeny(list): Worms decendants' birth certificates
	'''
	return max([d(0) for d in progeny])
