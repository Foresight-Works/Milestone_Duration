import re

import pandas as pd
import os
import re
import collections
files = [f for f in os.listdir() if (('merged' not in f) & ('.xlsx' in f))]
f_nums = [re.findall('\d{1,}', f)[0] for f in files]
files = dict(zip(f_nums, files))
od = collections.OrderedDict(sorted(files.items()))
files = dict(od)
print(files)
files = list(files.values())
print(files)
files_terms, dfs = {}, {}
for f in files:
	f_num = re.findall('\d{1,}', f)[0]
	df = pd.read_excel(f)
	del df['Unnamed: 0']
	terms = list(df['successor'])
	counts = list(df['count'])
	files_terms[f_num] = terms
	print('file and term counts:', f, sum(counts))
	dfs[f_num] = df

for f1, t1 in files_terms.items():
	for f2, t2 in files_terms.items():
		print('intesect {f1} {f2} terms'.format(f1=f1, f2=f2))
		comp = set(t1).intersection(set(t2))
		len_comp = len(comp)
		print(len(t1), len(set(t1)), len(t2), len(set(t2)), len_comp)

from functools import reduce
df_merged = reduce(lambda left, right: pd.merge(left, right, on=['successor'],
                                            how='outer'), dfs.values())
df_merged.to_excel('vc_merged.xlsx', index=False)