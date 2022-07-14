import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("The run started on", current_time)

chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/Jul13_22/chains.txt'
chains = [n for n in open(chains_path).read().split('\n') if n]
executor = ProcessPoolExecutor(10)

#chain_combinations = list(set(combinations(chains, 2)))
start = time.time()
print('{n} chains with overlaps'.format(n=len(chains)))
c = 0
overlaps = []

while chains:
	c1 = chains[0]
	for c2 in chains:
		if ((c1!=c2) & (c1 in c2)):
			chains.remove(c1)
			break
	c += 1

print('{n} chains without overlaps'.format(n=len(chains)))
chains = '\n'.join(chains)
with open('filtered_chains.txt', 'w') as f: f.write(chains)
print('duration=', time.time()-start)