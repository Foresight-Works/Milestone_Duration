
print('all remaining graphs')
for index, partition in partitions.items():
	#print(index, partition)
	chains = graph_to_chains(partition)
	partitions_chains[partition] = chains

# Collect chains
chains = []
for p, pchains in partitions_chains.items(): chains += pchains
np.save('partitions_chains.npy', partitions_chains)
print('{n} chains produced from sub_graphs'.format(n=len(chains)))
print('duration:', time.time()-start)