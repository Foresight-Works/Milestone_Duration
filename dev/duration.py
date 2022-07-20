import sys
modules_dir = '/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
modules_dir = '/home/rony/Projects_Code/Cluster_Activities/modules'
if modules_dir not in sys.path: sys.path.append(modules_dir)
from libraries import *
from parsers import *
from evaluate import *
data_path = './data'
file_name = 'MWH-06-UP#13_FSW_REV.graphml'
file_path = os.path.join(data_path, file_name)
graphml_str = open(file_path).read().replace('&amp;', '')
headers = ['ID', 'TaskType', 'Label', 'PlannedStart', 'PlannedEnd', 'ActualStart', 'ActualEnd', 'Float', 'Status']

# Calculate duration
start = time.time()
data_df = parse_graphml(file_name, graphml_str, headers)
planned_duration = activities_duration(data_df, 'planned')
planned_duration_df = pd.DataFrame(list(zip(list(planned_duration.keys()), list(planned_duration.values()))), columns=['ID', 'planned_duration'])
actual_duration = activities_duration(data_df, 'actual')
actual_duration_df = pd.DataFrame(list(zip(list(actual_duration.keys()), list(actual_duration.values()))), columns=['ID', 'actual_duration'])
planned_actual_df = pd.merge(planned_duration_df, actual_duration_df, how='left')
data_duration = pd.merge(data_df, planned_actual_df)
data_duration.to_excel('./results/data_duration_df.xlsx', index=False)
