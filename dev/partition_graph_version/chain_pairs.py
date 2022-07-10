results_path = '/home/rony/Projects_Code/Milestones_Duration/results/'
pairs_dir = 'pairs'
pairs_path = os.path.join(results_path, pairs_dir)
if pairs_dir in os.listdir(results_path):
	shutil.rmtree(pairs_path, ignore_errors=True)
	os.mkdir(pairs_path)

# 'chains.txt' holds the first generation chains produced from the partitions
# todo: write/read chains.txt as chunk0.txt to the chains directory
# chains = open('./results/chains.txt').read().split('\n')

# todo dev: use hashed chains rather than chains, pairs to run after chains filter
# todo integration: chains path set-up in config
chains_path = '/home/rony/Projects_Code/Milestones_Duration/results/chains'
chunks_indices = [int(re.findall('\d{1,}', c)[0]) for c in os.listdir(chains_path)]
indices_paths = [(index, chains_path, pairs_path) for index in chunks_indices]
executor = ProcessPoolExecutor(10)
start = time.time()
c = 0
for chunk_df in executor.map(pairs_chunks, indices_paths):
	#keep += chunk_keep
	c += 1
	print(c, chunk_df)
print('chunking duration=', time.time()-start)