import os
import networkx as nx
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import time
import mysql.connector as mysql
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()

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
	:param chain (list): A sequence of tasks
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
	root_node = list(nx.topological_sort(G))[0]

	# Load root node
	visited = [root_node]
	c.execute("DROP TABLE IF EXISTS chains;")
	c.execute("CREATE TABLE IF NOT EXISTS chains (chain varchar(255));")
	c.execute("INSERT INTO chains (chain) values ('{v}')".format(v=root_node))
	# todo: replace drop milestone_chains by creating a results table indexed by file name or id
	c.execute("DROP TABLE IF EXISTS milestone_chains")
	c.execute("CREATE TABLE IF NOT EXISTS milestone_chains (chain varchar(255))")

	visited_nodes_count, nodes_count = len(visited), len(Gnodes)
	step = 0
	visited_successors, visited_edges = [], []
	visited_edges_count = 0
	while visited_edges_count != edges_count:
		step += 1
		print('step {s}| {n1} edges, of which {n2} visited'.format(s=step, n1=edges_count, n2=visited_edges_count))
		start = time.time()
		print('part1')
		c.execute("SELECT chain FROM chains;".format(v=root_node))
		chains = [i[0].split('|') for i in c.fetchall()]
		print('part2: Track {n} chains'.format(n=len(chains)))
		for chain_val in chains:
			last_node = chain_val[-1]
			successors = list(G[last_node].keys())
			for successor in successors:
				print('calc')
				visited_edges.append((last_node, successor))
				chain_successor = chain_val+[successor]
				v = '|'.join(chain_successor)
				print('write')
				statement1 = "INSERT INTO chains (chain) VALUES ('{v}')".format(v=v)
				#print(statement)
				c.execute(statement1)
				conn.commit()
		print('part3')
		visited_edges_count = len(set(visited_edges))

		# Filter and write milestone chains
		c.execute("SELECT chain FROM chains")
		chains = [i[0] for i in c.fetchall()]
		print('filter {n} chains for milestone chains'.format(n=len(chains)))
		m = 0
		for chain_str in chains:
			chain1 = chain_str.split('|')
			if is_milestones_chain(chain1, ids_types):
				m += 1
				statement2 = "INSERT INTO milestone_chains (chain) values ('{v}');".format(v='|'.join(chain1))
				c.execute(statement2)
				conn.commit()
		print('filtering retained {n} milestone chains'.format(n=m))
		iteration_duration = time.time()-start
		print('iteration duration=', iteration_duration)

	return True

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