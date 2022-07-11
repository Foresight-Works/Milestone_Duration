import time

from modules.libraries import *
from modules.graphs import *
from modules.config import *

class wormWalk:
	def __init__(self, G, recentWormID, chains_path, birth_certificate):
		self.birth_certificate = birth_certificate
		self.wormIndex = birth_certificate[0]
		self.anchor_chain_id = birth_certificate[1]
		self.start_node = birth_certificate[2]
		self.pointer = None
		if len(birth_certificate) == 4:
			self.pointer = birth_certificate[3]
		self.graph = G
		self.successors = list(G.successors(self.start_node))
		self.chains_path = chains_path
		self.recentWormID = recentWormID

	def previous_step_chain(self):
		chains_df = pd.read_sql('SELECT * FROM {t}'.format(t=chains_table), con=conn)
		worm_chains = list(chains_df['nodes'][chains_df['chain'] == self.anchor_chain_id])
		chain_to_return = max(worm_chains, key=len).split(',')
		return chain_to_return

	def get_chain_id(self):
		chains_df = pd.read_sql('SELECT * FROM {t}'.format(t=chains_table), con=conn)
		chain_ids = list(chains_df['chain'])
		chain_id = max(chain_ids)+1
		return chain_id

	def grow(self):
		#chain_id = self.anchor_chain_id + 1
		chain_id = self.get_chain_id()
		successors = self.successors
		pointer = self.pointer
		if self.pointer:
			successors_chains = []
			for successor in successors:
				chain = self.previous_step_chain() + [successor]
				successors_chains.append(chain)
			for successor_chain in successors_chains:
				if successor_chain[-1] == self.pointer:
					chain = successor_chain
		else:
			if successors:
				next_node = successors[0]
				chain = self.previous_step_chain() + [next_node]
			else:
				chain_id, chain = None, None
		return (chain_id, chain)

	def reproduce(self, growth_node):
		descendants = []
		#chain_id = self.anchor_chain_id + 1
		successors = self.successors
		direction_nodes = [s for s in successors if s != growth_node]
		wormID = self.recentWormID
		descendantID = self.recentWormID + 1
		for direction_node in direction_nodes:
			wormID = wormID + 1
			birth_certificate = (descendantID, self.anchor_chain_id, self.start_node, direction_node)
			descendants.append(birth_certificate)
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
