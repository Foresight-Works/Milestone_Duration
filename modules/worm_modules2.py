import time

from modules.libraries import *
from modules.graphs import *
from modules.config import *

class wormWalk:
	def __init__(self, G, recentWormID, chains_path, certificate, chains_built_df):
		self.certificate = certificate
		self.wormIndex = certificate[0]
		self.anchor_chain_id = certificate[1]
		self.start_node = certificate[2]
		self.pointer = None
		if len(certificate) == 4:
			self.pointer = certificate[3]
		self.graph = G
		self.successors = list(G.successors(self.start_node))
		self.chains_path = chains_path
		self.recentWormID = recentWormID
		self.chains_built_df = chains_built_df

	def previous_step_chain(self):
		worm_chains = list(self.chains_built_df['nodes'][self.chains_built_df['chain'] == self.anchor_chain_id])
		chain_to_return = []
		if worm_chains:
			chain_to_return = max(worm_chains, key=len).split('<>')
		return chain_to_return

	def get_chain_id(self):
		chain_ids = list(self.chains_built_df['chain'])
		if chain_ids:
			chain_id = max(chain_ids)+1
		else:
			chain_id = 0
		return chain_id

	def grow(self):
		previous_step_chain = self.previous_step_chain()
		chain_id = self.get_chain_id()
		successors = self.successors
		if self.pointer:
			successors_chains = []
			for successor in successors:
				chain = previous_step_chain + [successor]
				successors_chains.append(chain)
			for successor_chain in successors_chains:
				if successor_chain[-1] == self.pointer:
					chain = successor_chain
			a = 0
		else:
			if successors:
				next_node = successors[0]
				chain = previous_step_chain + [next_node]
			else:
				chain_id, chain = None, None
			a=0
		return (chain_id, chain)

	def reproduce(self, growth_node):
		descendants = []
		successors = self.successors
		direction_nodes = [s for s in successors if s != growth_node]
		wormID = self.recentWormID
		descendantID = self.recentWormID + 1
		for direction_node in direction_nodes:
			wormID = wormID + 1
			certificate = (descendantID, self.anchor_chain_id, self.start_node, direction_node)
			descendants.append(certificate)
		return descendants

# The degree of terminal nodes as terminal nodes coverage indicator
def get_terminal_nodes(G):
	Gnodes = list(G.nodes())
	isolates = graph_isolates(G)
	return [n for n in Gnodes if ((G.out_degree(n) == 0) & (n not in isolates))]

def get_recent_id(certificates_dict):
	'''
	Return the ID for the last decendant born
	:param certificates_dict(dict): Worms' growth and birth certificates
	'''
	certificates = []
	for k, v in certificates_dict.items(): certificates += v
	if certificates:
		return max([d[0] for d in certificates])
	else:
		return 1
