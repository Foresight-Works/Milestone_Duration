from modules.libraries import *
from modules.graphs import *
class wormWalk:
	def __init__(self, G, recentWormID, chains_path, birth_certificate):
		self.birth_certificate = birth_certificate
		self.wormIndex = birth_certificate[0]
		self.anchor_chain_id = birth_certificate[1]
		self.start_node = birth_certificate[2]
		self.graph = G
		self.successors = list(G.successors(self.start_node))
		self.chains_path = chains_path
		self.recentWormID = recentWormID

	def previous_step_chain(self):
		chains_df = pd.read_pickle(self.chains_path)
		chain_id = self.anchor_chain_id
		worm_chains = list(chains_df['nodes'][chains_df['chain'] == self.anchor_chain_id])
		chain_to_return = max(worm_chains, key=len).split(',')
		return chain_to_return

	def grow(self):
		chainIndex = self.anchor_chain_id + 1
		next_node = self.successors[0]
		chain = self.previous_step_chain() + [next_node]
		return chainIndex, chain

	def reproduce(self):
		descendants = []
		#chain_id = self.anchor_chain_id + 1
		v = self.successors
		direction_nodes = self.successors[1:]
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
