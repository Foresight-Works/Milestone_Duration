import networkx as nx
import numpy as np
G = nx.DiGraph()
G_edges = [('N1', 'N2'), ('N2', 'N3'), ('N2', 'N4'), ('N2', 'N5'), ('N5', 'N6'),\
           ('N1', 'N7'), ('N7', 'N8'), ('N8', 'N9'), ('N9', 'N10'), ('N10', 'N11'),\
           ('N7', 'N12'), ('N12', 'N13'), ('N13', 'N14'), ('N13', 'N15'),\
           ('N15', 'N16'), ('N15', 'N17')]
G = nx.from_edgelist(G_edges)
A = nx.adjacency_matrix(G)#.toarray()
d = int(np.sum(A))
e = A.shape
c=0