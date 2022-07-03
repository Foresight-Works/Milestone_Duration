import numpy as np
from modules.graphs import *
from modules.config import *
import copy
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