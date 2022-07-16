import time
from filters import *
from encoders import *
# Data
tokens = open('tokens.txt').read().split('\n')
sample = open('sample.txt').read().split('\n')
queries = open('queries.txt').read().split('\n')

def lists_filter(objects, sample, queries):
	encoder = objects_encoder(objects)
	decoder = build_decoder(encoder)
	encoded_sample = [encoder[t] for t in sample]
	encoded_queries = [encoder[t] for t in queries]
	encoding_filtered = set(encoded_queries).difference(set(encoded_sample))
	filtered = [decoder[i] for i in encoding_filtered]
	return filtered

def lists_filter(sample, queries):
	objects = sample + queries
	encoder = objects_encoder(objects)
	decoder = build_decoder(encoder)
	encoded_sample = [encoder[t] for t in sample]
	encoded_queries = [encoder[t] for t in queries]
	encoding_filtered = set(encoded_queries).difference(set(encoded_sample))
	filtered = [decoder[i] for i in encoding_filtered]
	return filtered

start = time.time()
#filtered = set(queries).difference(set(sample))
filtered = lists_filter(sample, queries)
print('duration=', time.time()-start)