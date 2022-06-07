import mysql.connector as mysql
conn_params = {'host': 'localhost', 'user':'rony', 'password':'exp8546$fs', 'database': 'MCdb'}
conn = mysql.connect(**conn_params)
c = conn.cursor()
c.execute("SELECT chain FROM chains LIMIT 1000000;")
chains = [i[0] for i in c.fetchall()]
with open('chains.txt', 'w') as f:
	for chain in chains: f.write('{c}\n'.format(c=chain))
lenc = len(chains)
del chains

c.execute("SELECT chain FROM milestone_chains LIMIT 1000000;")
milestone_chains = [i[0] for i in c.fetchall()]
with open('milestone_chains.txt', 'w') as f:
	for chain in milestone_chains: f.write('{c}\n'.format(c=chain))

print('{n1} chains | {n2} milestone chains'.format(n1=lenc, n2=len(milestone_chains)))
