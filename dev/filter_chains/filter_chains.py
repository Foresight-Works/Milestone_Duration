# Filter a list of chains of overlapping chain
# if b in a exclude b
import time
chains1 = open('./results/chains.txt').read().split('\n')
exclude = []
start = time.time()
for index1, chain1 in enumerate(chains1):
	chains2 = [c for c in chains1 if c not in (exclude + [chain1])]
	for chain2 in chains2:
		if chain1 in chain2:
			exclude.append(chain1)
		elif chain2 in chain1:
			exclude.append(chain2)
print('chain filter duration=', time.time()-start)
exclude = '\n'.join(list(set(exclude)))
filtered_chains = [c for c in chains1 if c not in exclude]
with open('./results/filtered_chains.txt', 'w') as f: f.write(filtered_chains)

