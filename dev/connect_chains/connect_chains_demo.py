m = ['A', 'B', 'N', 'C', 'D', 'M']
n = ['E', 'F', 'C', 'G', 'H']
c = ['A', 'B', 'N', 'C', 'D', 'M']
d = ['M', 'F', 'Q', 'G', 'H']
e = ['H', 'B', 'N', 'C', 'D', 'M']
f = ['E', 'F', 'Q', 'G', 'H']

lists_pairs = [(m, n), (c, d), (e,f)]

def extend_chains(a, b):
	intersections_extensions = {}
	interecting_nodes = set(a).intersection(set(b))
	for n in interecting_nodes:
		print('intersection:', n)
		extension1, extension2 = [], []
		aindex, bindex = (a.index(n), b.index(n))
		# If an intersecting node is a chains' start node
		if aindex == 0:
			a = a[1:]
			extension1 = b + a
		elif bindex == 0:
			b = b[1:]
			extension1 = a + b
		# If an intersecting node is a chains' end node
		elif aindex == len(a) -1:
			a = a[:-1]
			extension1 = a + b
		elif bindex == len(b) -1:
			b = b[:-1]
			extension1 = b + a
		# If an intersecting node is inside a chain
		else:
			extension1 = a[:aindex] + b[bindex:]
			extension2 = b[:bindex] + a[aindex:]
		extensions = [e for e in [extension1, extension2] if e]
		intersections_extensions[n] = extensions

	return intersections_extensions

for a, b in lists_pairs:
	intersections_extensions = extend_chains(a, b)
	print(intersections_extensions)