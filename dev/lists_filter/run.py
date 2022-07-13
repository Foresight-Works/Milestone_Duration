import time
from filters import *
from encoders import *
# Data
tokens = open('tokens.txt').read().split('\n')
sample = open('sample.txt').read().split('\n')
queries = open('queries.txt').read().split('\n')

# def lists_filter(tokens, sample, queries):
# 	tokens_encoder = objects_encoder(tokens)
# 	tokens_decoder = build_decoder(tokens_encoder)
# 	encoded_sample = [tokens_encoder[t] for t in sample]
# 	encoded_queries = [tokens_encoder[t] for t in queries]
start = time.time()
filtered = set(queries).difference(set(sample))
print('duration=', time.time()-start)
a = 0
