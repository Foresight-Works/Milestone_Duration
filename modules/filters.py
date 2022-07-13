from bisect import bisect_left

def binarySearchFilter(source, target):
	'''
	Filter one list of numeric values but the elements presents in a second list of numeric values
	:param source(list): The list to fliter
	:param target(list): The values to use in filtering
	:return: A filtered version of the source list
	'''
	target = sorted(target)
	filtered_source = []
	for q in source:
		i = bisect_left(target,  q)
		if i != len(target) and target[i] == q:
			filtered_source.append(q)
	return filtered_source