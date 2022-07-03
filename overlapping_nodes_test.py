import numpy as np
from modules.graphs import *
from modules.config import *
# Clean partitions of overlapping sequences
partitions = np.load(os.path.join(experiment_path, 'partitions.npy'), allow_pickle=True)[()]
k, v = list(partitions.keys())[:20], list(partitions.values())[:20]
partitions = dict(zip(k, v))
cleaned_graphs = graph_pairs_overlap(partitions)
partitions = {k: v for k, v in partitions.items() if k not in cleaned_graphs.keys()}
partitions = {**partitions, **cleaned_graphs}
