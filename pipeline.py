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

# Testing only
partitions = np.load(os.path.join(experiment_path, 'partitions.npy'), allow_pickle=True)[()]

## Partition chains
chains = []
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
np.save(os.path.join(experiment_path, 'partitions.npy'), partitions)
chains += list(simple_graph_chains.values())
a = 0
## Crop overlapping terminal nodes ##
# Clean partitions of overlapping sequences
partitions = np.load(os.path.join(experiment_path, 'partitions.npy'), allow_pickle=True)[()]
#k, v = list(partitions.keys())[:300], list(partitions.values())[:300]
#partitions = dict(zip(k, v))
partitions1 = copy.deepcopy(partitions)
start1 = time.time()
cropped = crop_terminals(partitions)
print('cropping duration=', round(time.time()-start1))
np.save(os.path.join(experiment_path, 'cropped.npy'), cropped)
# Validation
results = []
before = set(graphs_nodes(list(partitions1.values())))
after = set(graphs_nodes(list(cropped.values())))
print(before.difference(after))
for k, v1 in partitions1.items():
	v2 = cropped[k]
	cropped_nodes = ','.join(list(set(v1).difference(set(v2))))
	results.append([k, len(v1), len(v2), cropped_nodes])
results = pd.DataFrame(results, columns=['graph', 'nodes_count', 'cropped_nodes_count', 'cropped_nodes'])
results.to_excel('cropping.xlsx', index=False)

# Check cropped for simple chains
partitions = np.load(os.path.join(experiment_path, 'cropped.npy'), allow_pickle=True)[()]
print('simple chains from cropped graphs')
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
np.save(os.path.join(experiment_path, 'partitions.npy'), partitions)
chains += list(simple_graph_chains.values())
chains_str = '\n'.join(str(chain) for chain in chains)
with open(os.path.join(experiment_path, 'chains.txt'), 'w') as f: f.write(chains_str)
a = 0