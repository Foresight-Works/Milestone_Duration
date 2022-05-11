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
	tmp_path = os.path.join(os.getcwd(), 'chains_temp.txt')

	# Load root node
	visited = [root_node]
	c.execute("DROP TABLE IF EXISTS chains;")
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
		num_executors = 4
		executor = ProcessPoolExecutor(num_executors)
		chunk, chains_produced_count, chunks_count = 10000, 0, 0
		chains_to_write = []
		for chain_successor_chains, chain_visited_edges in executor.map(extend_chain, chains_successors):
			visited_edges += chain_visited_edges
			chains_produced_count += len(chain_successor_chains)
			chains_to_write += chain_successor_chains
			Xn = len(chains_to_write)
			if Xn >= chunk:
				chunks_count += 1
				with open(tmp_path, 'w') as f:
					for chain in chains_to_write: f.write('{c}\n'.format(c=chain))
				statement3 = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE chains LINES TERMINATED BY '\n'".format(tp=tmp_path)
				c.execute(statement3)
				chains_to_write = []
		if chunks_count > 0: print('{n1} chains produced, written in {nc} chunks'.format(n1=chains_produced_count, nc=chunks_count))
		if Xn > 0:
			print('writing {n} successor chains that were not written in chunks'.format(n=len(chains_to_write)))
			with open(tmp_path, 'w') as f:
				for chain in chains_to_write: f.write('{c}\n'.format(c=chain))
			statement4 = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE chains LINES TERMINATED BY '\n'".format(tp=tmp_path)
			c.execute(statement4)

		del chains
		print('part 2 duration=', time.time() - start)
		visited_edges_count1 = len(visited_edges)
		print('visited_edges_count:', visited_edges_count1)
		visited_edges_count = len(set(visited_edges))
		print('unique visited_edges_count:', visited_edges_count)
		## Filter and write milestone chains
		# Extract the tasks chains to filter
		c.execute("SELECT chain FROM chains")
		tasks_chains = [i[0] for i in c.fetchall()]
		start = time.time()
		print('part3: filter {n} chains for milestone chains'.format(n=len(tasks_chains)))
		# Build a dictionary of tasks types for each task in each chain in the chains extracted for filtering
		chains_tasks_types = []
		for chain_str in tasks_chains:
			chain1 = chain_str.split('|')
			chains_tasks_types.append((chain1, {k: v for k, v in ids_types.items() if k in chain1}))
		del tasks_chains
		chains_to_write = []
		for chain2, confirm in executor.map(is_milestones_chain, chains_tasks_types):
			if confirm: chains_to_write.append('|'.join(chain2))
		with open(tmp_path, 'w') as f:
			for chain in chains_to_write: f.write('{c}\n'.format(c=chain))

		# Validation
		with open('./results/validation/chains_task_types.txt', 'w') as f:
			for chain in chains_to_write:
				ids = chain.split('|')
				types = (ids_types[id] for id in ids)
				chains_ids_types = str(dict(zip(ids, types))).replace("'", "")
				f.write('{c}\n'.format(c=chains_ids_types))
		statement3 = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE milestone_chains LINES TERMINATED BY '\n'".format(tp=tmp_path)
		c.execute(statement3)
		print('{n} milestone chains identified in this iteration'.format(n=len(chains_to_write)))
		milestones_chain_count += len(chains_to_write)
		print('{n} milestone chains identified thus far'.format(n=milestones_chain_count))
		del chains_to_write

		print('part 3 duration=', time.time() - start)
		iteration_duration = time.time()-start1
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