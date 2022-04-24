def milestone_nodes(G, include_fin = True):
	'''
	:param G: Graph object
	:return: The nodes for the milestones in the input graph
	'''
	G_nodes, G_edges = G.nodes(), G.edges()
	reg_milestone_ids = [node for node in G_nodes if G_nodes[node]['TaskType'] == 'TT_Mile']
	if include_fin:
		fin_milestone_ids = [node for node in G_nodes if G_nodes[node]['TaskType'] == 'TT_FinMile']
		milestone_ids = reg_milestone_ids + fin_milestone_ids
	milestones = {}
	for milestone_id in milestone_ids: milestones[milestone_id] = G_nodes[milestone_id]
	return milestones

def milestones_pair_route(milestone_node, graph_object):
	'''
	Identify connected milestones pair by the sequence of successors/predecessors
	:param milestone_node:
	:param graph_object:
	:return:
	'''
	# todo: search or develop a walk algorithm to identify connected nodes
	connected_milestone = ''
	return connected_milestone
