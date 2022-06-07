data_path = '/home/rony/Projects_Code/Milestones_Duration/data'

## Server
serviceLocation = 'Local'
num_executors = 6
locationIP = {'Local': '0.0.0.0', 'Remote': '172.31.15.123'}
locationPort = {'Local': 6002, 'Remote': 5000}
serviceIP = locationIP[serviceLocation]
servicePort = locationPort[serviceLocation]
url = 'http://{ip}:{port}/cluster_analysis/api/v0.1/milestones'.format(ip=serviceIP, port=servicePort)

# Database connection
#server_db_params = {'Local': {'host': 'localhost', 'user':'rony', 'password': 'exp8546$fs', 'database': db_name},\
#                    'Remote': {'host': serviceIP, 'user': 'researchUIuser', 'password':'query1234$fs', 'database': db_name}}
import mysql.connector as mysql
print('connecting to mysql')
private_serviceIP = '172.31.15.123'
user, password, db_name = 'rony', 'exp8546$fs', 'CAdb'
server_db_params = {'Local': {'host': 'localhost', 'user': user, 'password': password, 'database': db_name},\
                    'Remote': {'host': private_serviceIP, 'user': user, 'password': password, 'database': db_name}}
conn_params = server_db_params[serviceLocation]
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")