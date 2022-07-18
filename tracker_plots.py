import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import sys
mp = '/home/rony/Projects_Code/Cluster_Activities/modules'
if mp not in sys.path: sys.path.append(mp)
from plots import *
from modules.config import *

experiment_dir = 'alt_write'
results_path = os.path.join(results_path, experiment_dir)
plots_path = os.path.join(results_path, 'plots')
tracker = pd.read_excel(os.path.join(results_path, 'tracker.xlsx'))
no_chain_steps = tracker[tracker['chain_built'] == 0]
built_chain_steps = tracker[(tracker['chain_built'] == 1) & (tracker['new_chain'] == 0)]
new_chain_steps = tracker[tracker['new_chain'] == 1]

group_data = {'steps': tracker, 'noChain': no_chain_steps,\
            'builtChain': built_chain_steps, 'newChain': new_chain_steps}

#print(tracker.columns)
#val_cols = [c for c in df.columns if c != 'step']

def plot_df(df, name):
	xy_pairs = [('writed', 'stepd'), ('chains', 'stepd'), ('chains', 'writed'), ('chains', 'growthd'), ('chains', 'reproduced'), \
	            ('growth_certificates', 'growthd'), ('birth_certificates', 'reproduced'), \
	            ('birth_certificates', 'filtered_birth_certificates'),
	            ('growth_certificates', 'filtered_growth_certificates'), \
	            ('chains', 'step_processes_diff_ratio')]
	for x_col, y_col in xy_pairs:
		x, y = list(df[x_col]), list(df[y_col])
		plt.scatter(x, y, marker='.', s=1)
		plt.xlabel(x_col)
		plt.ylabel(y_col)
		figname = '{n}_{a}_vs_{b}.png'.format(n=name,a=y_col, b=x_col)
		plt.savefig(os.path.join(plots_path, figname))
		plt.close()

for group, df in group_data.items(): plot_df(df, group)

# for col in val_cols:
# 	print(col)
# 	x = list(tracker[col])
# 	x = [i for i in x if i]
# 	histogram_stats(x, col, col, os.path.join(plots_path, '{c}.png'.format(c=col)))
