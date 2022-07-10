import pandas as pd
import os
chains_df_path = os.path.join('../results', 'chains.pkl')
chains_path = os.path.join('../results', 'chains.txt')
chains_df = pd.read_pickle(chains_df_path)
chains_nodes = list(chains_df['nodes'])
n1, n2 = len(chains_nodes), len(set(chains_nodes))
print(chains_df.info())
print('{n1} chains | {n2} unique chains'.format(n1=n1, n2=n2))
print(chains_nodes[0], type(chains_nodes[0]))
chains_str = '\n'.join(chains_nodes)
with open(chains_path, 'w') as f: f.write(chains_str)