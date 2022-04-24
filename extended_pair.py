import numpy as np
milestones_duration = np.load('milestones_duration.npy', allow_pickle=True)[()]
milestone_pairs = list(milestones_duration.keys())
milestone_ids = []
for pair in milestone_pairs: milestone_ids += list(pair)
milestone_ids = list(set(milestone_ids))
print('{n} milestone pairs'.format(n=len(milestone_pairs)))
print('{n} uniuqe milestones'.format(n=len(milestone_ids)))
milestones_in_pairs = {} # Milestones and the pairs their in if they appear in more than one pair
for id in milestone_ids:
	pairs_with_id = []
	for pair in milestone_pairs:
		if id in pair:
			pairs_with_id.append(pair)
	if len(pairs_with_id) >1:
		milestones_in_pairs[id] = pairs_with_id

connected_milestones_duration = {}
for id, pairs in milestones_in_pairs.items():
	pairs0, pairs1 = [], []
	for pair in pairs:
		if id == pair[0]: pairs0.append(pair)
		else: pairs1.append(pair)

	if pairs0 and pairs1:
		test_connected_milestones_duration = {}
		if pairs0 and pairs1:
			print(30 * '=')
			print('Milestone ID:', id)
			print('first in pairs:', {k:v for k,v in milestones_duration.items() if k in pairs0})
			print('second in pairs:', {k:v for k,v in milestones_duration.items() if k in pairs1})
			for pair1 in pairs1:
				for pair0 in pairs0:
					connected_duration = milestones_duration[pair0] + milestones_duration[pair1]
					connected_milestones_duration[(pair1[0], pair0[1])] = connected_duration
					test_connected_milestones_duration[(pair1[0], pair0[1])] = connected_duration
			print('connected duration', test_connected_milestones_duration)

np.save('connected_duration.npy', connected_milestones_duration)
with open('extended_pairs_duration.txt', 'w') as f:
	for k, v in connected_milestones_duration.items():
		kvstr = '{k}:{v}\n'.format(k=str(k), v=str(v))
		f.write(kvstr)
# print(30 * '*')
# print('Connected Pairs and Duration')
# for k,v in connected_milestones_duration.items(): print(k, v)
