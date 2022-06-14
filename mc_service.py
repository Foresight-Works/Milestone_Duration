import time
from datetime import datetime
import numpy as np
import networkx as nx
import pandas as pd
import sys
import os
import mysql.connector as mysql
from flask import Flask
import socket
from flask import Response, jsonify, request, redirect, url_for, send_from_directory
from zipfile import ZipFile

conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()
from modules.nodes import *
from modules.milestones import *
from modules.paths import *
from modules.config import *

working_dir = os.getcwd()
results_dir = os.path.join(working_dir, 'results')

# Prepare and empty validation directories
validation_dir = os.path.join(results_dir, 'validation')
val_dirs = ['chains', 'milestone_chains']
for dir in val_dirs:
	path = os.path.join(validation_dir, dir)
	files = os.listdir(path)
	for f in files:
		fpath = os.path.join(path, f)
		os.remove(fpath)

app = Flask(Flask.__name__)
app.config['UPLOAD_FOLDER'] = './data'

headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']
link_types = ['<FS>', '<SF>', '<SS>', '<FF>']

# Prepare data and run pipeline
@app.route('/cluster_analysis/api/v0.1/milestones', methods=['POST'])
def run_service():
	# Parse data
	zipped_files = request.files.get('file', '')
	zipped_files.save('temp.zip')
	zipped_object = ZipFile('temp.zip', "r")
	if 'temp.zip' in os.listdir(): os.remove('temp.zip')
	file_names = zipped_object.namelist()
	print('file_names:', file_names)
	if file_names:
		# File cluster_key to pass to the results table (temp. proxy for experiment name)
		# File name validation
		for file_name in file_names:
			print('===={f}===='.format(f=file_name))
			encodings = ['utf-8-sig', 'latin-1', 'ISO-8859-1', 'Windows-1252']
			encoded, index = False, 0
			while encoded == False:
				encoding = encodings[index]
				print('encoding using', encoding)
				try:
					graphml_str = zipped_object.read(file_name).decode(encoding=encoding)
					graphml_str = graphml_str.replace('&amp;', '')
					encoded = True
				except UnicodeDecodeError as e:
					print(e)
					index += 1

	# Graph
	file_path = 'tmp.graphml'
	with open(file_path, 'w') as f: f.write(graphml_str)
	G = nx.read_graphml(file_path)

	# Rebuild the graph from edges to exclude isolates
	nodes_degrees = dict(G.degree())
	isolates = [n for n in list(nodes_degrees.keys()) if nodes_degrees[n]==0]
	for isolate in isolates: G.remove_node(isolate)
	###
	G = nx.DiGraph(G)
	os.remove(file_path)
	print(count_node_types(G))
	res, cycle = has_cycle(G)
	print('has cycle:', res, cycle)

	# Nodes
	Gnodes = list(G.nodes())
	Gnodes_ser = pd.Series(Gnodes)
	unique_nodes = Gnodes_ser.unique()
	print('{n1} nodes | {n2} unique nodes'.format(n1=len(Gnodes), n2=len(unique_nodes)))

	# Milestone chains
	print('Milestone chains')
	start = time.time()
	print("Root chains start:", datetime.now().strftime("%H:%M:%S"))
	root_chains(G, conn, num_executors)
	write_duration('Milestone chains', start)
	# Read milestone chains
	c.execute("SELECT chain FROM milestone_chains;")
	chains = c.fetchall()
	# Validation
	with open(os.path.join(validation_dir, 'milestone_chains.txt'), 'w') as f:
		for chain in chains: f.write('{c}\n'.format(c=', '.join(chain)))

if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='0.0.0.0', port=servicePort)