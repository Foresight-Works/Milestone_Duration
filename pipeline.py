from modules.config import *
from modules.experiment import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *

## Graph partitions ##
G = build_graph(file_path)
Gnodes, Gedges = list(G.nodes()), G.edges()
partitions, partitioning_tracker = partition_graph(G, file_path, partition_size_cutoff)
np.save(os.path.join(experiment_path, 'partitions.npy'), partitions)
# Validation
partitioning_tracker.to_excel(os.path.join(experiment_path, 'partitioning_tracker.xlsx'), index=False)
nodes_count = len(nodes_chains(list(partitions.values())))

# testing only
partitions = np.load(os.path.join(experiment_path, 'partitions.npy'), allow_pickle=True)[()]

## Partition chains
partitions_chains = {}
simple_graph_chains = chains_from_linear_graphs(partitions)
simple_graph_chains_indices = list(simple_graph_chains.keys())
for index in simple_graph_chains_indices:
	del partitions[index]
np.save(os.path.join(experiment_path, 'linear_partitions.npy'), simple_graph_chains)

simple_graph_chains = chains_from_star_graphs(partitions, partition_size_cutoff)
simple_graph_chains_indices = list(simple_graph_chains.keys())
for index in simple_graph_chains_indices:
	del partitions[index]
# todo: test partitions following simple chains building
np.save(os.path.join(experiment_path, 'star_partitions.npy'), simple_graph_chains)
np.save(os.path.join(experiment_path, 'partitions.npy'), partitions)
#print('Building Single Chains from {n} Partitions'.format(n=len(partitions)))






