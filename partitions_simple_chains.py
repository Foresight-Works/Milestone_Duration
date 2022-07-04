from modules.config import *
from modules.libraries import *
from modules.graphs import *
from modules.chains import *

chains = []

# Check cropped for simple chains
partitions = np.load(os.path.join(experiment_path, 'partitions1.npy'), allow_pickle=True)[()]
simple_graph_chains = chains_from_linear_graphs(partitions)
simple_graph_chains_indices = list(simple_graph_chains.keys())
for index in simple_graph_chains_indices:
	del partitions[index]
np.save(os.path.join(experiment_path, 'linear_partitions.npy'), simple_graph_chains)
chains += list(simple_graph_chains.values())
simple_graph_chains = chains_from_star_graphs(partitions, partition_size_cutoff)
simple_graph_chains_indices = list(simple_graph_chains.keys())
for index in simple_graph_chains_indices:
	del partitions[index]
np.save(os.path.join(experiment_path, 'star_partitions.npy'), simple_graph_chains)
np.save(os.path.join(experiment_path, 'partitions2.npy'), partitions)
chains += list(simple_graph_chains.values())
path = os.path.join(experiment_path, 'chains2.pkl')
write_chains(chains, path, how='pickle')
print('{p} partitions written'.format(p=len(partitions)))
