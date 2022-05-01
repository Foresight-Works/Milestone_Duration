import numpy as np
def milestones_pair_string(pair_key, pair_vals):

	'''
	Build a string representation for a duration result per milestone pair, including the names and ids of the start milestone,
	end milestone and intermediary steps, that were written to a dictionary in a previous step
	Milestone pair values example:
	('MWH06.C4.E1460', 'MWH06-C4.P2300') {'milestone_duration': 42, 'tasks_duration': {'MWH06.C4.E1460': ('PDU ROJ COLO-4 Cell-4', 0),
	'MWH06.C4.C4350': ("PDU's Installation", 2),
	 'MWH06.C4.C4450': ('Light Fixtures Installation', 8), 'MWH06-C4.P1900': ('COLO 4 CSA complete', 0),
	 'MWH.06.M4010': ('MWH06 COLO4 - LV3 Cx Complete (CO-66: 28-Dec-21)', 0), 'MWH06.C4.Cx4000': ('COLO 4 Level 4  Level 5 IST', 20),
	'MWH06.C4.Cx4020': ('Punch List COLO-4', 12), 'MWH06-C4.P2300': ('TCO COLO 4', 0)}, 'milestone_names': ('PDU ROJ COLO-4 Cell-4', 'TCO COLO 4')}
	:param pair_key(tuple): Start/end milestone IDS
	:param pair_vals: The names of the milestones, milestones duration and the tasks and the names for intermediate tasks
	'''
	milestone_names, tasks, milestone_duration =\
		pair_vals['milestone_names'], pair_vals['tasks_duration'], pair_vals['milestone_duration']
	pair_str = 60 * '=' + '\n'
	id1, id2 = pair_key[0], pair_key[1]
	n1, n2 = milestone_names[0], milestone_names[1]
	pair_str += '{mid} {mn}\n'.format(mid=id1, mn=n1)
	pair_str += 60 * '-' +'\n'
	for k, v in tasks.items():
		pair_str += '{id} {name}, {duration} days\n'.format(id=k, name=v[0], duration=v[1])
	pair_str += 60 * '-' + '\n'
	pair_str += '{mid} {mn}'.format(mid=id2, mn=n2)
	pair_str += '\n' + 6 * '*' + '\n'
	pair_str += 'Milestones duration = {md} days\n\n'.format(md=milestone_duration)

	return pair_str

milestones_duration = np.load('./results/milestones_duration.npy', allow_pickle=True)[()]

# ('MWH06.C3.E1420', 'MWH-06-01-DRY-F') ['MWH06.C3.E1420', 'MWH06-C1.P1300', 'MWH-06-01-DRY-F']
query_pairs = [('MWH06.C3.E1420', 'MWH06-C1.P1300'), ('MWH06-C1.P1300', 'MWH-06-01-DRY-F')]
milestones_duration = {k:v for k, v in milestones_duration.items() if k in query_pairs}
print('milestones_duration:', milestones_duration)
pairs_str = ''
for id_pair, v in milestones_duration.items():
	print(id_pair)
	pair_str = milestones_pair_string(id_pair, v)
	print(pair_str)
	pairs_str += pair_str

with open('./results/milestone_pairs_exploration.txt', 'w') as f: f.write(pairs_str)