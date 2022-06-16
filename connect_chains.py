import numpy as np
import networkx as nx
partitions_chains = np.load('partitions_chains1.npy', allow_pickle=True)[()]
print(type(partitions_chains))
print(partitions_chains.keys())
a = 0