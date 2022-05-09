import pandas as pd
import os
files = [f for f in os.listdir('./results') if 'pkl' in f]
for f in files:
	df = pd.read_pickle(os.path.join('./results', f))
	print(f)
	print(df.info())
	print(df.head())
