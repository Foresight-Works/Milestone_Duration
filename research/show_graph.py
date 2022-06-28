import os
import numpy as np
import networkx as nx
from pyvis.network import Network
nt = Network('100%', '100%')
nt.set_options('''var options = {"nodes": {"size": 20, "shape": "triangle", "width":15,
    "font.size":"2"}, "edges":{"width":1, "font.size":"0"}}''')
graphs_path = '/home/rony/Projects_Code/Milestones_Duration/results/validation/graphs'
graphs = np.load('partitions1_dict.npy', allow_pickle=True)[()]
for i, graph in graphs.items():
	if i>2:
		print('graph', str(i+1))
		a = input('save/show graph')
		if a == 'y':
			nt.from_nx(graph)
			nt.show(os.path.join(graphs_path, 'graph{i}.html'.format(i=str(i+1))))
