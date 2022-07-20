import random
import nltk
from sklearn.datasets import fetch_20newsgroups
corpus_size = 1000000
newsgroups_train = fetch_20newsgroups(subset='train')['data']
tokens = []
i = 0
while len(tokens) < corpus_size:
	text_tokens = list(set(nltk.word_tokenize(newsgroups_train[i])))
	text_tokens = [t for t in text_tokens if len(t) > 4]
	tokens += text_tokens
	i += 1
tokens = '\n'.join(tokens)
with open('tokens.txt', 'w') as f: f.write(tokens)
