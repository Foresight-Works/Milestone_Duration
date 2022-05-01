import networkx as nx
from pyvis.network import Network
from IPython.core.display import display, HTML

G = nx.karate_club_graph()
g4 = Network(height='400px', width='50%',notebook=True,heading='Zachary’s Karate Club graph')

g4.from_nx(G)

g4.show_buttons(filter_=['physics'])
g4.show('karate.html')
display(HTML('karate.html'))