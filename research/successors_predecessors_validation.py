import pandas as pd
import ast
source_path = '/home/rony/Projects_Code/Milestones_Duration/results/validation/predecessor_successor.xlsx'
results_path = '/home/rony/Projects_Code/Milestones_Duration/results/validation/chains_task_types.txt'
source = pd.read_excel(source_path)
source_pairs = list(zip(source['Predecessor'], source['Successor']))
print('{n} source pairs; sample:'.format(n=len(source_pairs)), source_pairs[:10])

results = open(results_path).read().split('\n')
pairs = []
for index, result in enumerate(results):
	result = result.replace('}', '').replace('{', '').split(',')
	result = [r.split(':')[0].rstrip().lstrip() for r in result]
	result_pairs = []
	for index, id in enumerate(result):
		if index<len(result)-1:
			result_pairs.append((id, result[index+1]))
	pairs += result_pairs

pairs = list(set(pairs))
print('{n} pairs; sample:'.format(n=len(pairs)), pairs[:10])

pairs_in_source = [p for p in pairs if p in source_pairs]
print('{n} pairs in source; sample:'.format(n=len(pairs_in_source)), pairs_in_source[:10])
