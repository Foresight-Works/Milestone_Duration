from bisect import bisect_left
from encoders import *

def binarySearchFilter(queries, target):
	'''
	Filter one list of numeric values but the elements presents in a second list of numeric values
	:param queries(list): The list to filter
	:param target(list): The values to use in filtering
	:return: A filtered version of the queries list
	'''
	target = sorted(target)
	filtered = []
	for q in queries:
		i = bisect_left(target,  q)
		if i != len(target) and target[i] == q:
			filtered.append(q)
	return filtered

def lists_filter(queries, target):
	objects = target + queries
	object_is_list = False
	if type(objects[0]) == list:
		object_is_list = True
		objects = [tuple(i) for i in objects]
	encoder = objects_encoder(objects)
	decoder = build_decoder(encoder)
	encoded_target = [encoder[t] for t in target]
	encoded_queries = [encoder[t] for t in queries]
	encoding_filtered = set(encoded_queries).difference(set(encoded_target))
	filtered = [decoder[i] for i in encoding_filtered]
	if object_is_list:
		filtered = [list(i) for i in filtered]
	return filtered