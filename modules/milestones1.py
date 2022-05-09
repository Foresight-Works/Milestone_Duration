import networkx as nx
import pandas as pd
from joblib import Parallel, delayed
from concurrent.futures import ProcessPoolExecutor
import time
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

def milestones_pairs_duration(milestone_paths, planned_duration, ids_names):
	milestones_duration = {}
	global milestones_pair_duration

	def milestones_pair_duration(pair_tasks):
		milestones_pair, inter_milestone_tasks = pair_tasks
		milestone_duration = 0
		# start_str = 60 * '='
		# print(60*'=')
		# print('Milestones:', milestones_pair)
		# write_str = '{s}\nMilestones: {mp}\n'.format(s=start_str, mp=milestones_pair)
		tasks_duration = {}
		for task_id in inter_milestone_tasks:
			task_duration = planned_duration[task_id]
			# print(task_id, task_duration)
			#write_str += '\n{tid} | {td}'.format(tid=task_id, td=task_duration)
			milestone_duration += task_duration
			name_duraion = (ids_names[task_id], task_duration)
			tasks_duration[task_id] = name_duraion
		#write_str += '\nMilestone Duration={md}\n'.format(md=milestones_duration)
		# print('Milestone Duration=', milestone_duration)
		# with open('./results/milestone_paths.txt', 'a') as f: f.write(write_str)
		duration_dict = {'milestone_duration': milestone_duration, 'tasks_duration': tasks_duration}
		return pair_tasks, duration_dict

	pairs_tasks = []
	for milestones_pair, inter_milestone_tasks in milestone_paths.items():
		pairs_tasks.append((milestones_pair, inter_milestone_tasks))

	executor = ProcessPoolExecutor(4)
	for pair_tasks, duration_dict in executor.map(milestones_pair_duration, pairs_tasks):
		milestones_pair = pair_tasks[0]
		milestones_duration[milestones_pair] = duration_dict

	#Parallel(n_jobs=4)(delayed(milestones_pair_duration)(i) for i in (pairs_tasks))
	return milestones_duration

from collections import defaultdict
import collections

def is_milestones_chain(chain, ids_types, milestone_types=['TT_Mile', 'TT_FinMile']):
	'''
	Identify a task chain as milestones chains (starts and end in a milestone) based on the identification of chain tasks as milestones
	:param chain: A sequence of tasks
	:param ids_types (dictionary): Graph tasks types keyed by their task ids
	:param milestone_codes (list): The
	:return:
	'''
	confirm = False
	start_id, end_id = chain[0], chain[-1]
	start_type, end_type = ids_types[start_id], ids_types[end_id]
	if ((any(start_type==t for t in milestone_types)) &
		(any(end_type==t for t in milestone_types))):
		confirm = True
	return confirm

def root_chains(G, ids_types):
	'''
	Identify node chains in a directed graph that start from the root node
	:param G: DiGraph object
	:return: List of node chains
	'''
	Gnodes = G.nodes()
	Gedges = list(G.edges())
	edges_count = len(Gedges)
	print('{n2} unique edges between {n1} nodes'.format(n1=len(Gnodes), n2=len(set(Gedges))))
	print('edges sample:', Gedges[:10])
	milestone_nodes = [n for n in Gnodes if ((ids_types[n] == 'TT_Mile') | (ids_types[n] == 'TT_FinMile'))]
	milestone_nodes_str = ', '.join(milestone_nodes)
	with open('milestone_nodes.txt', 'w') as f: f.write(milestone_nodes_str )
	root_node = list(nx.topological_sort(G))[0]
	# Load root node
	chains, visited = [[root_node]], [root_node]
	visited_nodes_count, nodes_count = len(visited), len(Gnodes)
	step = 0
	chains_df = pd.DataFrame(chains, columns=['chain'])
	print(chains_df.head())
	chains_df.to_pickle('chains_df.pkl')
	# Todo: replace length by list contents comparison using intersection, should be more accurate, check speed
	visited_successors, visited_edges = [], []
	steps_tdas, steps_milestones = {}, {}
	#while visited_nodes_count != nodes_count:
	visited_edges_count = 0
	while visited_edges_count != edges_count:
		step += 1
		print('step: {s}| {n1} nodes, of which {n2} visited'.format(s=step, n1=nodes_count, n2=visited_nodes_count))
		print('step: {s}| {n1} edges, of which {n2} visited'.format(s=step, n1=edges_count, n2=visited_edges_count))
		generation_chains = []
		start = time.time()
		chains_df = pd.read_pickle('chains_df.pkl')
		chains = list(chains_df['chain'])
		step_chains = []
		chains = [chain.split(',') for chain in chains]
		tdas = []

		def edges_checked(G, nodes):
			'''
			Count the edges explored in building a tasks chain
			:param G: graph object
			:param nodes: The nodes explored
			:return: Edges count for the nodes explored
			'''
			pass

		for chain in chains:
			last_node = chain[-1]
			#successors = [i for i in list(G[last_node].keys()) if i not in visited_successors]
			successors = list(G[last_node].keys())
			for successor in successors:
				visited_edges.append((last_node, successor))
				chain_to_add = chain+[successor]
				step_chains.append(chain_to_add)
				visited_successors.append(successor)

		visited_edges_count = len(set(visited_edges))
		checked_chains = chains + step_chains
		chains_str = [[','.join(chain)] for chain in checked_chains]
		chains_df = pd.DataFrame(chains_str, columns=['chain']).drop_duplicates()
		chains_df.to_pickle('chains_df.pkl')

		# Compare chain values
		# print('{n} successors visited'.format(n=len(visited_successors)))
		# vc = pd.Series(visited_successors).value_counts()
		# vc = pd.DataFrame(list(zip(list(vc.index), list(vc.values))),\
		#                                          columns=['successor', 'count'])
		# vc.to_excel('vc_{a}.xlsx'.format(a=step), index=False)
		visited_successors = [root_node] + visited_successors
		visited = set(visited_successors)
		visited_nodes_count = len(visited)
		not_visited = [n for n in list(Gnodes) if n not in visited]
		not_visited_edges = {}
		for node in not_visited: not_visited_edges[node] = list(G[node].keys())
		if visited_nodes_count == 507:
			steps_tdas[step] = tdas
			steps_milestones[step] = not_visited

		# Check if different tda values are explored following round 162
		same_vals = True
		for k1, v1 in steps_tdas.items():
			for k2, v2 in steps_tdas.items():
				v1, v2 = set(v1), set(v2)
				if v1.intersection(v2) != v1:
					same_vals = False
					#print('v1:', v1)
					#print('v2:', v2)
					v1_only = [i for i in v1 if i not in v2]
					#print('v1_only:', v1_only)

		iteration_duration = time.time()-start
		print('iteration duration=', iteration_duration)
	if [root_node] in chains: chains.remove([root_node])
	print('filter {n} chains for milestone chains'.format(n=len(chains)))
	milestone_chains_df = pd.DataFrame()
	for chain in chains:
		if not is_milestones_chain(chain, ids_types):

			#chains.remove(chains)
	print('filtering retained {n} milestone chains'.format(n=len(chains)))

	return chains

def milestone_chains(chains, ids_types):
	'''
	Build a list of chains that starts and end in a milestone based on the identification of chain tasks as milestones
	:param chains (list): Root chains to filter
	:param ids_types (dictionary): Graph tasks types keyed by their task ids
	:return: Milestone chains
	'''
	milestone_chains = []
	for chain in chains:
		if is_milestones_chain(chain, ids_types): milestone_chains.append(chain)
	return milestone_chains