import os
import networkx as nx
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import time
import mysql.connector as mysql_con
import pymysql.cursors
user, password, database = 'rony', 'exp8546$fs', 'MCdb'
conn_params = {'host': 'localhost', 'user': user, 'password': password, 'database': database}
conn = mysql_con.connect(**conn_params, allow_local_infile = True)
c = conn.cursor()

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://{u}:{p}@localhost/{db}' \
                       .format(u=user, p=password, db=database))  #:5432

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

	return milestones_duration

from collections import defaultdict
import collections

def is_milestones_chain(chain_ids_types, milestone_types=['TT_Mile', 'TT_FinMile']):
	'''
	Identify a task chain as milestones chains (starts and end in a milestone) based on the identification of chain tasks as milestones
	:param chain (list): A sequence of tasks
	:param ids_types (dictionary): Graph tasks types keyed by their task ids
	:return:
	'''
	chain, ids_types = chain_ids_types
	confirm = False
	start_id, end_id = chain[0], chain[-1]
	start_type, end_type = ids_types[start_id], ids_types[end_id]
	if ((any(start_type == t for t in milestone_types)) &
			(any(end_type == t for t in milestone_types))):
		confirm = True
	return chain, confirm

def extend_chain(chain_successor):
	chain_visited_edges = []
	chain, last_node_successors = chain_successor
	chain_successor_chains = []
	last_node = chain[-1]
	for successor in last_node_successors:
		chain_visited_edges.append((last_node, successor))
		chain_successor = chain + [successor]
		v = '|'.join(chain_successor)
		chain_successor_chains.append(v)
	chain_visited_edges = list(set(chain_visited_edges))
	#print('{n} chain_visited_edges in extend_chain:'.format(n=len(chain_visited_edges)), chain_visited_edges)
	return chain_successor_chains, chain_visited_edges


def write_chains(chains, table_name, tmp_path):
	with open(tmp_path, 'w') as f:
		for chain in chains: f.write('{c}\n'.format(c=chain))
	statement = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE {tn} LINES TERMINATED BY '\n'".format(
		tp=tmp_path, tn=table_name)
	#print('statement:', statement)
	c.execute(statement)

def get_tasks_types(chains, ids_types):
	chains_tasks_types = []
	for chain_str in chains:
		chain = chain_str.split('|')
		chains_tasks_types.append((chain, {k: v for k, v in ids_types.items() if k in chain}))
	return (chains_tasks_types)

def collect_filter_results(chains, num_executors, tmp_path, ids_types):
	executor2 = ProcessPoolExecutor(num_executors)
	## Write chains for the next iteration
	write_chains(chains, 'chains', tmp_path)
	# Identify the type of each task in the chains identified
	chains_tasks_types = get_tasks_types(chains, ids_types)
	## Filter tasks chains
	milestone_chains = []
	# Parallelized
	#for chain2, confirm in executor2.map(is_milestones_chain, chains_tasks_types):
	#	if confirm: milestone_chains.append('|'.join(chain2))
	for chain2, confirm in map(is_milestones_chain, chains_tasks_types):
		if confirm: milestone_chains.append('|'.join(chain2))
	executor2.shutdown()
	## Write results: milestone chains
	write_chains(milestone_chains, 'milestone_chains', tmp_path)

	return milestone_chains

def root_chains(G, ids_types):
	'''
	Identify node chains in a directed graph that start from the root node
	:param G: DiGraph object
	:return: List of node chains
	'''

	Gnodes = G.nodes()
	Gedges = G.edges(data=True)
	edges_count = len(Gedges)
	print('{n2} unique edges between {n1} nodes'.format(n1=len(Gnodes), n2=len(set(Gedges))))
	root_node = list(nx.topological_sort(G))[0]
	tmp_path = os.path.join(os.getcwd(), 'chains_temp.txt')
	print('aaa')

	edges_types = {}
	for Gedge in Gedges:
		print(Gedge)
		edges_types[(Gedge[0], Gedge[1])] = Gedge[2]['Dependency']
	print('edges_types:', edges_types)

	# Load root node
	visited = [root_node]
	c.execute("DROP TABLE IF EXISTS chains;")
	print('DROP TABLE IF EXISTS chains;')
	c.execute("CREATE TABLE IF NOT EXISTS chains (chain varchar(255));")
	c.execute("INSERT INTO chains (chain) values ('{v}')".format(v=root_node))
	# todo: replace drop milestone_chains by creating a results table indexed by file name or id
	c.execute("DROP TABLE IF EXISTS milestone_chains")
	c.execute("CREATE TABLE IF NOT EXISTS milestone_chains (chain varchar(255))")
	step = 0
	visited_successors, visited_edges = [], []
	visited_edges_count = 0
	milestones_chain_count = 0
	while visited_edges_count != edges_count:
		start1 = time.time()
		step += 1
		print(50 * '=')
		print('step {s}| {n1} edges, of which {n2} visited'.format(s=step, n1=edges_count, n2=visited_edges_count))
		start = time.time()
		print('part1')
		c.execute("SELECT chain FROM chains;".format(v=root_node))
		chains = [i[0].split('|') for i in c.fetchall()]
		chains_count = len(chains)
		print('part 1 duration=', time.time()-start)
		start = time.time()
		print('part2: Tracking successors for {n} chains'.format(n=chains_count))

		# Couple each to the successors of its last node
		chains_successors = []
		for chain_val in chains:
			last_node = chain_val[-1]
			last_node_successors = list(G[last_node].keys())
			chains_successors.append((chain_val, last_node_successors))

		# Extend chains using the last node successors of each
		num_executors = 6
		executor1 = ProcessPoolExecutor(num_executors)
		chunk, chains_produced_count, chunks_count = 10000, 0, 0
		tasks_chains = []
		for chain_successor_chains, chain_visited_edges in executor1.map(extend_chain, chains_successors):
			visited_edges += chain_visited_edges
			chains_produced_count += len(chain_successor_chains)
			tasks_chains += chain_successor_chains
			Xn = len(tasks_chains)
			if Xn >= chunk:
				chunks_count += 1
				milestone_chains = collect_filter_results(tasks_chains, num_executors, tmp_path, ids_types)
				milestones_chain_count += len(milestone_chains)
				tasks_chains = []
			executor1.shutdown()

		if chunks_count > 0: print('{n1} chains produced, written in {nc} chunks'.format(n1=chains_produced_count, nc=chunks_count))
		if Xn > 0:
			print('writing {n} successor chains that were not written in chunks'.format(n=len(tasks_chains)))
			milestone_chains = collect_filter_results(tasks_chains, num_executors, tmp_path, ids_types)
			milestones_chain_count += len(milestone_chains)

		del chains, tasks_chains
		print('part 2 duration=', time.time() - start)
		visited_edges_count1 = len(visited_edges)
		print('visited_edges_count:', visited_edges_count1)
		visited_edges_count = len(set(visited_edges))
		print('unique visited_edges_count:', visited_edges_count)
		iteration_duration = time.time()-start1
		print('iteration duration=', iteration_duration)
		print('{n} milestone chains identified'.format(n=milestones_chain_count))

		## Validation
		c.execute("SELECT chain FROM milestone_chains;".format(v=root_node))
		milestone_chains = [i[0] for i in c.fetchall()]
		with open('./results/validation/chains_task_types.txt', 'w') as f:
			for chain in milestone_chains:
				ids = chain.split('|')
				types = (ids_types[id] for id in ids)
				chains_ids_types = str(dict(zip(ids, types))).replace("'", "")
				f.write('{c}\n'.format(c=chains_ids_types))


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