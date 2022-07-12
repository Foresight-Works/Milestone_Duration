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
import pymysql.cursors
user, password, database = 'rony', 'exp8546$fs', 'MCdb'
conn_params = {'host': 'localhost', 'user': user, 'password': password, 'database': database}
conn = mysql_con.connect(**conn_params, allow_local_infile = True)
c = conn.cursor()

# todo dependency management: store and import from standard utils
def isfloat(value):
    '''
    Check if the input value type is float
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False

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

def extend_chain(chains_successors_links):
	'''
	Extend a chain of nodes using the successors of the last node in the chain
	:param chains_successors_links(list): The chain to extend followed by a dictionary of link types for each combination of the last node in the chain and a successor
	Example:
	['MWH.06.M1000'], {('MWH.06.M1000', 'A1170'): 'FS', ('MWH.06.M1000', 'MWH06-2029'): 'FS', ('MWH.06.M1000', 'MWH06-2527'): 'FS', ('MWH.06.M1000', 'MWH06.D1.S1010'): 'FS'...}
	:return:
	'''
	chain_visited_edges = []
	chain, successors_links = chains_successors_links
	last_node_successors = list(successors_links.keys())
	chain_successor_chains = []
	for last_node_successor in last_node_successors:
		chain_visited_edges.append(last_node_successor)
		pair_link_type = successors_links[last_node_successor]
		chain_successor = chain + ['<{lt}>'.format(lt=pair_link_type), last_node_successor[1]]
		chain_successor_chains.append(chain_successor)
	chain_successor_chains = chain_successor_chains
	chain_visited_edges = list(set(chain_visited_edges))
	return chain_successor_chains, chain_visited_edges

def write_chains(chains, table_name, tmp_path):
	with open(tmp_path, 'w') as f:
		for chain in chains:
			chain = [str(task_float) for task_float in chain]
			chain = ''.join(chain)
			f.write('{c}\n'.format(c=chain))
	statement = "LOAD DATA LOCAL INFILE '{tp}' INTO TABLE {tn} LINES TERMINATED BY '\n'".format(
		tp=tmp_path, tn=table_name)
	c.execute(statement)

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

def get_tasks_types(chains, ids_types, hash_nodes_map):
	chain_links = [handle_link_type(chain) for chain in chains]
	chains_tasks_types = []
	for index, chain in enumerate(chains):
		chain_link = chain_links[index]
		chain_nodes = [n for n in chain if n != chain_link]
		nodes_types = {k: v for k, v in ids_types.items() if k in chain_nodes}
		chains_tasks_types.append((chain, nodes_types))
	return (chains_tasks_types)

def collect_filter_results(chains, num_executors, tmp_path, ids_types, hash_nodes_map):
	executor2 = ProcessPoolExecutor(num_executors)
	## Write chains for the next iteration
	write_chains(chains, 'chains', tmp_path)
	# Identify the type of each task in the chains identified
	chains_tasks_types = get_tasks_types(chains, ids_types, hash_nodes_map)
	## Filter tasks chains
	milestone_chains = []
	# Parallelized
	for chain2, confirm in executor2.map(is_milestones_chain, chains_tasks_types):
	#for chain2, confirm in map(is_milestones_chain, chains_tasks_types):
		if confirm:
			nodes_str =''.join(chain2)
			milestone_chains.append(nodes_str)
	executor2.shutdown()
	## Write results: milestone chains
	write_chains(milestone_chains, 'milestone_chains', tmp_path)
	return milestone_chains


def get_successors_types(node, successors, edges_types):
	'''
	Identify the types of links between a node and each of its successors
	:param node (list): A graph node name
	:param successors(list): The node's successors
	:param edges_types(dict): The list of link types per edge keyed by a tuple of the nodes connected by this edge
	:return: A dictionary of link types per successor keyed by (node, successor) tuple
	'''
	successors_types = {}
	for successor in successors:
		pair = (node, successor)
		successors_types[pair] = edges_types[pair]
	return successors_types

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

def root_chains(G):
	'''
	Identify node chains in a directed graph that start from the root node
	:param G: DiGraph object
	:return: List of node chains
	'''

	Gnodes = G.nodes()
	nodes_hash_map = strings_floats_hash(Gnodes)
	hash_nodes_map = {v: k for k, v in nodes_hash_map.items()}
	G = nx.relabel_nodes(G, nodes_hash_map)
	ids_types = build_ids_types(G)
	Gnodes, Gedges = G.nodes(), G.edges()
	edges_count = len(Gedges)
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
	visited_edges = []
	visited_edges_count = 0
	milestones_chain_count = 0
	link_types = ['<FS>', '<SF>', '<SS>', '<FF>']
	link_types_str = '|'.join(link_types)
	tmp_path = os.path.join(os.getcwd(), 'chains_temp.txt')

	while visited_edges_count != edges_count:
		start1 = time.time()
		step += 1
		print(50 * '=')
		print('step {s}| {n1} edges, of which {n2} visited'.format(s=step, n1=edges_count, n2=visited_edges_count))
		start = time.time()
		print('part1')
		c.execute("SELECT chain FROM chains;".format(v=root_node))
		chains_fetched = c.fetchall()
		chains_fetched = tuple([chain[0] for chain in chains_fetched])
		chains = tuple([tuple(re.split('({lt})'.format(lt=link_types_str), chain)) for chain in chains_fetched])
		del chains_fetched
		chains_count = len(chains)
		print('part 1 duration=', time.time()-start)
		start = time.time()
		print('part2: Tracking successors for {n} chains'.format(n=chains_count))
		# Couple each chain to the successors of its last node
		chains_successors_links = []
		for chain in chains:
			chain = [float(t) for t in chain if isfloat(t)]
			last_node = float(chain[-1])
			last_node_successors = list(G[last_node].keys())
			successors_types = get_successors_types(last_node, last_node_successors, edges_types)
			chains_successors_links.append((chain, successors_types))

		# Split chains_successors_links to chunks
		size = len(chains_successors_links)
		mem_size = sys.getsizeof(chains_successors_links)
		print('size of chains = {c}'.format(c=mem_size))
		mem_threshold = 10485760
		num_chunks = int(mem_size/mem_threshold) + 1
		chunk_size = int(size/num_chunks)
		del chains
		print('part 2 duration=', time.time() - start)
		# Extend chains using the last node successors of each
		print('part3: chains extensions by node children'.format(n=chains_count))
		num_executors = 6
		executor1 = ProcessPoolExecutor(num_executors)
		# Iterate input chanks
		for num_chunk in range(num_chunks):
			num_chunk1 = num_chunk + 1
			chunk_index = num_chunk1 * chunk_size
			chunk = chains_successors_links[:chunk_index]
			chains_successors_links = chains_successors_links[chunk_index:]
			mem_size = sys.getsizeof(chunk)
			print('input chunk {i} of size {s}'.format(i=num_chunk1, s=mem_size))
			write_chunk, chains_produced_count, write_chunks_count = 10000, 0, 0
			start = time.time()
			tasks_chains = []
			mem_sizes = []
			for chain_successor_chains, chain_visited_edges in executor1.map(extend_chain, chunk):
			#for chain_successor_chains, chain_visited_edges in map(extend_chain, chunk):
				mem = psutil.virtual_memory().percent
				mem_sizes.append(mem)
				# mem_dict = psutil.virtual_memory()._asdict()
				visited_edges += chain_visited_edges
				del chain_visited_edges
				chains_produced_count += len(chain_successor_chains)
				tasks_chains += chain_successor_chains
				del chain_successor_chains
				Xn = len(tasks_chains)
				if Xn >= write_chunk:
					write_chunks_count += 1
					milestone_chains = collect_filter_results(tasks_chains, num_executors, tmp_path, ids_types, hash_nodes_map)
					milestones_chain_count += len(milestone_chains)
					tasks_chains = []
			if write_chunks_count > 0:
				print('{n1} chains produced, written in {nc} write_chunks'.format(n1=chains_produced_count, nc=write_chunks_count))
			if Xn > 0:
				print('writing {n} successor chains that were not written in write_chunks'.format(n=len(tasks_chains)))
				milestone_chains = collect_filter_results(tasks_chains, num_executors, tmp_path, ids_types, hash_nodes_map)
				milestones_chain_count += len(milestone_chains)
			del tasks_chains, milestone_chains
			mean_mem = np.mean(np.array(mem_sizes))
			print('mean memory used percentage=', mean_mem)
		executor1.shutdown()

		print('part 3 duration=', time.time() - start)
		visited_edges_count1 = len(visited_edges)
		print('visited_edges_count:', visited_edges_count1)
		visited_edges_count = len(set(visited_edges))
		print('unique visited_edges_count:', visited_edges_count)
		iteration_duration = time.time()-start1
		print('iteration duration=', iteration_duration)
		print('{n} milestone chains identified'.format(n=milestones_chain_count))

		# Validation results
		c.execute("SELECT chain FROM milestone_chains;".format(v=root_node))
		milestone_chains = '\n'.join([i[0] for i in c.fetchall()])
		with open('./results/validation/milestone_chains/step_{s}.txt'.format(s=step), 'w') as f: f.write(milestone_chains)

		# val_to_write = ''
		# split_chain = re.split('({lt})'.format(lt=link_types_str), chain)
		# for element in split_chain:
		# 	if element in link_types:
		# 		val_to_write += element
		# 	else:
		# 		element_hash = float(element)
		# 		element_type = ids_types[element_hash]
		# 		val_to_write += '{e}({t})'.format(e=element, t=element_type)
		# f.write('{c}\n'.format(c=val_to_write))

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