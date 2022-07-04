from modules.libraries import *
from modules.config import *
from modules.splitgraph import *
from modules.vizz import *
from modules.chains import *
start = time.time()

partitions_plots_path = '/home/rony/Projects_Code/Milestones_Duration/results/validation/partitions'
partitions = np.load(os.path.join(experiment_path, 'partitions2.npy'), allow_pickle=True)[()]

## Build chains from branched graphs
# todo: parallelize build chains
counter = 0
chains = []
for index, partition in partitions.items():
	counter += 1
	print('\n*** partition {c} index {i} ***'.format(c=counter, i=index))
	#draw_graph(partition, os.path.join(partitions_plots_path, 'partition{i}.png'.format(i=index)))
	if len(partition)>0:
		partition_chains = root_chains(partition)
		chains += partition_chains
		print('{n1} chains produced | {n2} total chains'.format(n1=len(partition_chains), n2=len(chains)))
		write_chains(partition_chains, os.path.join(partitions_plots_path, 'partition{i}_chains.txt'.format(i=index)))
		a = 0
a = 0
print('chain building duration=', round(time.time()-start))
path = os.path.join(experiment_path, 'chains3.pkl')
write_chains(chains, path, how='pickle')
