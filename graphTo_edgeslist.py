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
	G = nx.DiGraph(G)
	os.remove(file_path)
	# Hash nodes and edges
	nodes_map = numeric_kv(G.nodes(), use_floats=False)
	nodes_map_str = '\n'.join(['{v}_{k}'.format(k=k, v=v) for k, v in nodes_map.items()])
	with open('./results/nodes_map.txt', 'w') as f: f.write(nodes_map_str)
	G = nx.relabel_nodes(G, nodes_map)
	Gnodes, Gedges = G.nodes(), list(G.edges.data())
	Gedges_str = '\n'.join(['{e1}_{e2}_{l}'.format(e1=edge[0], e2=edge[1],\
	                l=edge[2]['Dependency']) for edge in Gedges])
	with open('./results/edges_list.txt', 'w') as f: f.write(Gedges_str)
	return 'Edge list produced'


if __name__ == '__main__':
    print('host name:', socket.gethostbyname(socket.gethostname()))
    app.run(host='0.0.0.0', port=servicePort)