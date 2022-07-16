from modules.encoders import *
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