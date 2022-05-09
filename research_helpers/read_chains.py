import pandas as pd
chains = pd.read_pickle('chains_df.pkl')['chain'].value_counts()
chains_counts = pd.DataFrame(list(zip(list(chains.index), list(chains.values))),\
		                                         columns=['chain', 'count'])
chains_counts.to_excel('chains_counts.xlsx', index=False)
chains = pd.read_pickle('chains_df.pkl')['chain'].drop_duplicates()
chains = list(pd.read_pickle('chains_df.pkl')['chain'])
print('{n} chains identified'.format(n=len(chains)))
with open('chains.txt', 'w') as f:
	for chain in chains:
		f.write('{c}\n'.format(c=chain))