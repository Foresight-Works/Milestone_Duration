from joblib import Parallel, delayed
import time, math
def my_fun(i):
    return i**2
for i in range(10):
    print(my_fun(i))
a = Parallel(n_jobs=2)(delayed(my_fun)(i) for i in range(10))
print(a)