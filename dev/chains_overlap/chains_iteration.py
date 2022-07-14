import time
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/Jul13_22/chains.txt'
chains = open(chains_path).read().split('\n')
executor = ProcessPoolExecutor(10)

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("The run started on", current_time)

#chain_combinations = list(set(combinations(chains, 2)))
overlaps = []
start = time.time()
#chains = chains[:100]
chains_str = '\n'.join([str(c) for c in chains])
with open('chains.txt', 'w') as f: f.write(chains_str)

for index1, c1 in enumerate(chains):
	#print(index1, len(overlaps), len(chains))
	for index2, c2 in enumerate(chains):
		#print(index1, index2)
		if ((c1!=c2) & (c1 in c2)):
			overlaps.append(c1)
	overlaps = list(set(overlaps))
	chains = list(set(chains).difference(set(overlaps)))

filtered = list(set(chains).difference(set(overlaps)))
filtered = [str(c) for c in filtered]
filtered = '\n'.join(filtered)
with open('filtered_chains.txt', 'w') as f: f.write(filtered)
print('duration=', time.time()-start)