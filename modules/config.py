import os
import sys
from modules.db_tables import *
from modules.libraries import *

data_path = '/home/rony/Projects_Code/Milestones_Duration/data'
experiment_id = 3
data_file_name = 'MWH-06-UP#13_FSW_REV.graphml'
partition_size_cutoff = 50

## Server
serviceLocation = 'Local'
num_executors = 6
locationIP = {'Local': '0.0.0.0', 'Remote': '172.31.15.123'}
locationPort = {'Local': 6002, 'Remote': 5000}
serviceIP = locationIP[serviceLocation]
servicePort = locationPort[serviceLocation]
url = 'http://{ip}:{port}/cluster_analysis/api/v0.1/milestones'.format(ip=serviceIP, port=servicePort)

# Database connection
#server_db_params = {'Local': {'host': 'localhost', 'user': 'rony', 'password': 'exp8546$fs', 'database': db_name},\
#                    'Remote': {'host': serviceIP, 'user': 'researchUIuser', 'password': 'query1234$fs', 'database': db_name}}
import mysql.connector as mysql
private_serviceIP = '172.31.15.123'
user, password, db_name = 'rony', 'exp8546$fs', 'MCdb'
server_db_params = {'Local': {'host': 'localhost', 'user': user, 'password': password, 'database': db_name},\
                    'Remote': {'host': private_serviceIP, 'user': user, 'password': password, 'database': db_name}}
conn_params = server_db_params[serviceLocation]
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")

# Tables
tracker_table = 'tracker'
tracker_cols_types = {'step': 'INTEGER', 'growth_certificates': 'DECIMAL', 'filtered_growth_certificates': 'INTEGER', \
                   'birth_certificates': 'INTEGER', 'filtered_birth_certificates': 'INTEGER', 'applied_certificates': 'INTEGER', \
                   'chains': 'INTEGER', 'growthD': 'DECIMAL', 'reproduceD': 'DECIMAL', \
                   'updateD': 'DECIMAL', 'certificate_selectD': 'DECIMAL', 'processesD': 'DECIMAL', \
                   'stepD': 'DECIMAL', 'step_processes_diff': 'DECIMAL', 'step_processes_diff_ratio': 'DECIMAL'}
chains_cols_types = {'worm': 'INTEGER', 'chain': 'INTEGER', 'nodes': 'TEXT'}
tracker_table, chains_table = 'tracker', 'chains'

# Directories
working_dir = os.getcwd()
data_path = os.path.join(os.getcwd(), 'data')
file_path = os.path.join(data_path, data_file_name)
results_path = os.path.join(working_dir, 'results')
experiment_dir = 'experiment_{id}'.format(id=experiment_id)
experiment_path = os.path.join(results_path, experiment_dir)
