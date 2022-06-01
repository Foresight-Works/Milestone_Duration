# Split chains_successors_links to chunks
		# size = len(chains_successors_links)
		# mem_size = sys.getsizeof(chains_successors_links)
		# print('size of chains = {c}'.format(c=mem_size))
		# mem_threshold = 10485760
		# num_chunks = int(mem_size / mem_threshold) + 1
		# chunk_size = int(size / num_chunks)
		# Iterate input chunks
		# for num_chunk in range(num_chunks):
		# 	num_chunk1 = num_chunk + 1
		# 	chunk_index = num_chunk1 * chunk_size
		# 	chunk = chains_successors_links[:chunk_index]
		# 	chains_successors_links = chains_successors_links[chunk_index:]
		# 	mem_size = sys.getsizeof(chunk)
		# 	print('input chunk {i} of size {s}'.format(i=num_chunk1, s=mem_size))
		#for chain_successor_chains, chain_visited_edges in executor1.map(extend_chain, chains_successors_links):