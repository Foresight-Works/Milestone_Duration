def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

a = [1,2,3,4,5,6,7,8,9,10,11,12]
print(list(chunks(a, 5)))