import mysql.connector as mysql
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SELECT * FROM chains;")
chains = [i[0] for i in c.fetchall()]
chains = c.fetchall()
print(chains)
for chain in chains: print(chain)