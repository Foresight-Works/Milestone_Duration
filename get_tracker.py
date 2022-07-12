import sys
path = '/home/rony/Projects_Code/Milestones_Duration/modules'
if path not in sys.path: sys.path.append(path)
from config import *
from libraries import *
df = pd.read_sql('SELECT * FROM {t}'.format(t=tracker_table), con=conn)
print(df.head())
df.to_excel('tracker.xlsx', index=False)