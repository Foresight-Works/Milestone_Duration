import os
import sys

import numpy as np
import psutil
import networkx as nx
import re
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
import time
import mysql.connector as mysql_con
from modules.utils import *

user, password, database = 'rony', 'exp8546$fs', 'MCdb'
conn_params = {'host': 'localhost', 'user': user, 'password': password, 'database': database}
conn = mysql_con.connect(**conn_params, allow_local_infile = True)
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

	return milestones_duration

def is_milestones_chain(chain_ids_types, milestone_types=['TT_Mile', 'TT_FinMile']):
	'''
	Identify a task chain as milestones chains (starts and end in a milestone)
	based on the identification of chain tasks as milestones
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
	chain = [str(t) for t in chain]
	return chain, confirm

def extend_chain(tail_successors_submitted):
	'''
	Extend a chain of nodes using the successors of the last node in the chain
	:param successors(list): The chain to extend followed by a dictionary of link types for each combination of the last node in the chain and a successor
	Example:
	['MWH.06.M1000'], {('MWH.06.M1000', 'A1170'): 'FS', ('MWH.06.M1000', 'MWH06-2029'): 'FS', ('MWH.06.M1000', 'MWH06-2527'): 'FS', ('MWH.06.M1000', 'MWH06.D1.S1010'): 'FS'...}
	:return:
	'''
	tail, successors = tail_successors_submitted
	tail_successors = []
	for successor in successors:
		tail_successor = [tail, successor]
		tail_successors.append(tail_successor)
	return tail_successors

def chain_to_string(chain, connector='<>'):
	chain = [str(task_float) for task_float in chain]
	chain = '{c}'.format(c=connector).join(chain)
	return chain
def chains_to_strings(chains):
	chains_str = []
	for chain in chains:
		chain = chain_to_string(chain)
		chains_str.append(chain)
	return chains_str
def write_chains(chains, table_name, tmp_path, conn):
	extended_chains = chains_to_strings(chains)
	extended_chains = '\n'.join(extended_chains)
	with open(tmp_path, 'w') as f: f.write(extended_chains)
	statement = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE {tn} LINES TERMINATED BY '\n'".format(
		tp=tmp_path, tn=table_name)
	c.execute(statement)
	conn.commit()

def handle_link_type(chain, remove=False):
	'''
	Return or remove the type of nodes link from the chain representation of the nodes
	:param chain (list): A representation of the node pair in the form of [node 1, link, node2]
	for example: ['MWH.06.M1000', '<FS>', 'MWH06-2029']
	:param remove (bool): Instruction to remove the chain link
	:return: The chain link (default) or the chain without the link(remove=True)
	'''
	dependency_types = ['FS', 'SF', 'SS', 'FF']
	if remove: return [i for i in chain if not any(t in i for t in dependency_types)]
	else:
		m = [i for i in chain if any(t in str(i) for t in dependency_types)]
		if m: return m[0]
		else: return ''

def get_tasks_types(chains, ids_types):
	chain_links = [handle_link_type(chain) for chain in chains]
	chains_tasks_types = []
	for index, chain in enumerate(chains):
		chain_link = chain_links[index]
		chain_nodes = [n for n in chain if n != chain_link]
		nodes_types = {k: v for k, v in ids_types.items() if k in chain_nodes}
		chains_tasks_types.append((chain, nodes_types))
	return (chains_tasks_types)

def strings_floats_hash(strings):
	'''
	Hash strings as a floating point number
	:param strings (list): A list of strings
	:return: A dictionary of strings: flaoting point number
	'''
	mapping = {}
	float_val = 0.0
	for string in strings:
		float_val = round(float_val + 0.1, 2)
		mapping[string] = float_val
	return mapping

def build_ids_types(G):
	'''
	Map task id to task type for each task in an input graph
	:param G: An input graph object
	:return:
	'''
	tasks_types = list(nx.get_node_attributes(G, "TaskType").values())
	Gnodes = list(G.nodes())
	ids_types = dict(zip(Gnodes, tasks_types))
	return ids_types

def get_successors_links(node, successors, edges_types):
	'''
	Identify the types of links between a node and each of its successors
	:param node (list): A graph node name
	:param successors(list): The node's successors
	:param edges_types(dict): The list of link types per edge keyed by a tuple of the nodes connected by this edge
	:return: A dictionary of link types per successor keyed by (node, successor) tuple
	'''
	successors_links = {}
	for successor in successors:
		pair = (node, successor)
		successors_links[successor] = edges_types[pair]
	return successors_links


def root_chains(G, conn):
	'''
	Identify node chains in a directed graph that start from the root node
	:param G: DiGraph object
	:return: List of node chains
	'''
	Gnodes = G.nodes()
	terminal_nodes = [x for x in Gnodes if G.out_degree(x) == 0 and G.in_degree(x) == 1]
	print('terminal_nodes:', terminal_nodes)

	nodes_hash_map = strings_floats_hash(Gnodes)
	hash_nodes_map = {v: k for k, v in nodes_hash_map.items()}
	G = nx.relabel_nodes(G, nodes_hash_map)
	ids_types = build_ids_types(G)
	Gnodes, Gedges = G.nodes(), G.edges()
	nodes_count = len(Gnodes)
	print('{n2} unique edges between {n1} nodes'.format(n1=len(Gnodes), n2=len(set(Gedges))))
	root_node = list(nx.topological_sort(G))[0]

	Gedges = G.edges(data=True)
	edges_types = {}
	for Gedge in Gedges: edges_types[(Gedge[0], Gedge[1])] = Gedge[2]['Dependency']

	# Load root node
	visited = [root_node]
	c.execute("DROP TABLE IF EXISTS chains;")
	c.execute("CREATE TABLE IF NOT EXISTS chains (chain varchar(255));")
	c.execute("INSERT INTO chains (chain) values ('{v}')".format(v=root_node))
	# todo: replace drop milestone_chains by creating a results table indexed by file name or id
	c.execute("DROP TABLE IF EXISTS milestone_chains")
	c.execute("CREATE TABLE IF NOT EXISTS milestone_chains (chain varchar(255))")
	step = 0
	nodes_visited, nodes_visited_count = [], 0
	tmp_path = os.path.join(os.getcwd(), 'chains_temp.txt')
	while nodes_visited_count != nodes_count:
		# Step params
		start1 = time.time()
		step += 1
		num_executors = 6
		executor1 = ProcessPoolExecutor(num_executors)
		mem_sizes = []
		chunk_size, chains_produced_count, chunk_sizes_count = 10000, 0, 0
		print(50 * '=')
		print('step {s}| {n1} nodes, of which {n2} were visited'.format(s=step, n1=nodes_count, n2=nodes_visited_count))
		start = time.time()
		print('part1')
		c.execute("SELECT chain FROM chains;".format(v=root_node))
		chains_fetched = c.fetchall()
		chains_fetched = [chain[0] for chain in chains_fetched]
		chains = [re.split('<>', chain) for chain in chains_fetched]
		a = 5
		for chain in chains: nodes_visited += chain

		del chains_fetched
		c.execute("DROP TABLE IF EXISTS chains;")
		c.execute("CREATE TABLE IF NOT EXISTS chains (chain varchar(255));")
		print('step 1 duration=', time.time()-start)

		chains_count = len(chains)
		print('step 2: Tracking successors for {n} chains'.format(n=chains_count))
		start = time.time()

		# Collect the successor tasks for the last task in the chain
		tail_successors_submit = []
		tails_chains_dict = {}
		for index, chain in enumerate(chains):
			chain = [float(t) for t in chain]
			tail = chain[-1]
			successors = list(G[tail].keys())
			# Get tasks links
			successors_links = get_successors_links(tail, successors, edges_types)
			# Filter successors that are not <FS> linked to the tail
			successors = []
			for successor, link in successors_links.items():
				if link == 'FS': successors.append(successor)
			tail_successors_submit.append((tail, successors))
			tails_chains_dict[tuple(chain)] = tail
			a = 4
		#mem_size = sys.getsizeof(successors)
		#print('chains memory size = {c} bytes'.format(c=mem_size))
		del chains
		print('step 2 duration=', time.time() - start)
		# Extend chains using the last node successors of each
		print('part 3: chains extensions by node children'.format(n=chains_count))
		start = time.time()
		extended_chains = []
		for tails_chains in executor1.map(extend_chain, tail_successors_submit):
		#for tails_chains in map(extend_chain, tail_successors_submit):
			mem = psutil.virtual_memory().percent
			mem_sizes.append(mem)
			chains_produced_count += len(tails_chains)
			# Concatenate a chain tail successors to it's chain
			for tail_chain in tails_chains:
				tail, chain = tail_chain[0], tail_chain[1:]
				chains_to_extend = {k for k, v in tails_chains_dict.items() if v == tail}
				for chain_to_extend in chains_to_extend:
					extended_chain = list(chain_to_extend) + list(chain)
					extended_chains.append(extended_chain)
			# Filter overlapping chains
			del tails_chains
			Xn = len(extended_chains)
			chunks_count = int(Xn/chunk_size)
		write_duration('chains extension', start)
		chains_validation = chains_to_strings(extended_chains)
		chains_validation = '\n'.join(chains_validation)
		with open('./results/validation/chains/step_{s}.txt'.format(s=step), 'w') as f:
			f.write(chains_validation)

		# Keep milestone chains
		print ('Step 4: Select and write milestone chains')
		start = time.time()
		milestone_chains = select_milestone_chains \
			(extended_chains, num_executors, tmp_path, ids_types, hash_nodes_map, conn)
		write_duration('Milestones selection', start)
		chains_validation = '\n'.join(milestone_chains)
		with open('./results/validation/milestone_chains/step_{s}.txt'.format(s=step), 'w') as f:
			f.write(chains_validation)
		print('{n1} milestone chains selected from {n2} chains identified'.format(n1=len(milestone_chains), n2=Xn))
		print('{n} chains will be written in {nc} chunks'.format(n=Xn, nc=chunks_count+1))
		# Write chains for the next iteration
		start = time.time()
		while Xn >= chunk_size:
			chunk_sizes_count += 1
			chunk = extended_chains[:chunk_size]
			write_chains(chunk, 'chains', tmp_path, conn)
			extended_chains = extended_chains[chunk_size:]
			Xn = len(extended_chains)
		if Xn > 0:
			write_chains(extended_chains, 'chains', tmp_path, conn)
		del extended_chains
		write_duration('writing chains', start)
		executor1.shutdown()
		mean_mem = np.mean(np.array(mem_sizes))
		print('mean memory used percentage=', mean_mem)
		print('step 3 duration=', time.time() - start)
		nodes_visited_count = len(set(nodes_visited))
		iteration_duration = time.time()-start1
		print('iteration duration=', iteration_duration)
		
	return True


def tasks_hash_to_ids(chains, hash_nodes_map):
	ids_chains = []
	for chain in chains:
		chain_ids = [hash_nodes_map[float(task)] for task in chain]
		ids_chains.append(chain_ids)
	return ids_chains

def select_milestone_chains(chains, num_executors, tmp_path, ids_types, hash_nodes_map, conn):
	# Identify the type of each task in the chains identified
	chains_tasks_types = get_tasks_types(chains, ids_types)
	## Filter tasks chains
	milestone_chains = []
	# Parallelized
	executor2 = ProcessPoolExecutor(num_executors)
	for chain2, confirm in executor2.map(is_milestones_chain, chains_tasks_types):
	# for chain2, confirm in map(is_milestones_chain, chains_tasks_types):
		if confirm: milestone_chains.append(chain2)
	executor2.shutdown()
	milestone_chains = tasks_hash_to_ids(milestone_chains, hash_nodes_map)
	milestone_chains = chains_to_strings(milestone_chains)
	## Write results: milestone chains
	write_chains(milestone_chains, 'milestone_chains', tmp_path, conn)
	return milestone_chains
