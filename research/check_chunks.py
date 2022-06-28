import pandas as pd
import os
path = '/home/rony/Projects_Code/Milestones_Duration/results/pairs'
files = os.listdir(path)
print(files)
for f in files:
	df = pd.read_pickle(os.path.join(path, f))
	print(df.head())
	if len(df) == 0:
		print(f, len(df))
