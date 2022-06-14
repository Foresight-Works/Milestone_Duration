log = open('log1.txt').read().split('\n')
chains = [i for i in log if '[' in i]
print(len(chains), len(set(chains)))
