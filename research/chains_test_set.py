# build a chains test set of all or a sample of the chains identified
import numpy as np
import re
partitions_chains = np.load('./results/partitions_chains.npy', allow_pickle=True)[()]
chains = []
for node, pchains in partitions_chains.items(): chains += pchains
chains = [str(c) for c in chains]
chains = '\n'.join([re.sub("\[|\]|\s|'", '', c) for c in chains])
#['MWH06.S.1890', 'MWH06.S.1910', 'MWH.06.M4010']
with open('./results/chains.txt', 'w') as f: f.write(chains)
