import numpy as np
import random
def partition (list_in, n):
    random.shuffle(list_in)
    return [list(list_in[i::n]) for i in range(n)]

def partition_edges(edges_list, n):
	edges_partitions = []
	indices = [int(i) for i in np.arange(len(edges_list))]
	partitions_indices = partition(indices, n)
	for partition_indices in partitions_indices:
		for i in partition_indices:
			a = type(i)
			b = edges_list[i]
			partition_edges = [edges_list[i] for i in partition_indices]
		edges_partitions.append(partition_edges)
	return edges_partitions

a = np.arange(20)
b = partition(a, 7)
print(b)
n = 5
c = ['a', 'b', 'n', 't', 'g', 'tt', 'y', 'z', 'r', 'pp',\
     'ma', 'mb', 'mn', 'mt', 'mg', 'mtt', 'my', 'mz', 'mr', 'mpp']
d = partition_edges(c, n)
print(d)
edges = [('MWH.06.M1010', 'MWH06.C1.Cx4000'), ('MWH.06.M1010', 'MWH06.C1.Cx4030'), ('MWH.06.M1000', 'A1170'), ('MWH.06.M1000', 'MWH06-2029'), ('MWH.06.M1000', 'MWH06-2527'), ('MWH.06.M1000', 'MWH06.D1.S1010'), ('MWH.06.M1000', 'MWH06-2537'), ('MWH.06.M1000', 'MWH06-2538'), ('MWH.06.M1000', 'MWH06-2535'), ('MWH.06.M1000', 'MWH06-2536'), ('MWH.06.M1000', 'MWH06-2539'), ('MWH.06.M1000', 'MWH06-2540'), ('MWH.06.M1000', 'MWH06-9714'), ('MWH.06.M1000', 'MWH06-9716'), ('MWH.06.M1000', 'MWH06-9735'), ('MWH.06.M1000', 'MWH06-9789'), ('MWH.06.M1000', 'MWH06-9908'), ('MWH.06.M1000', 'MWH06-9909'), ('MWH.06.M1000', 'MWH06-9904'), ('MWH.06.M1000', 'MWH06-9905')]
e = partition_edges(edges, n)
print(e)
t= 0