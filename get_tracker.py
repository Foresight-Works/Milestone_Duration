import sys
import matplotlib.pyplot as plt
path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if path not in sys.path: sys.path.append(path)
from config import *
from libraries import *
df = pd.read_sql('SELECT * FROM {t}'.format(t=tracker_table), con=conn)
print(df.head())
#df.to_excel('tracker.xlsx', index=False)
chain_vals = list(df['chains'])
step_duration_vals = list(df['stepd'])
update_duration_vals = list(df['updated'])
print('run duration for {n} chains='.format(n=chain_vals[-1]), sum(step_duration_vals))
dur0, dur1 = len(df[df['stepd'] == 0]), len(df[df['stepd'] == 1])

plt.scatter(chain_vals, step_duration_vals, marker='.')
plt.xlabel('Chain Produced in a Step')
plt.ylabel('Step Duration')
plt.show()
