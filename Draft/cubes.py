import numpy as np
import random

sums = np.zeros(10000)
cubes =[random.sample(range(1, 7), 10000) for i in range(0,3)]

for i in range(3):
    sums += cubes[i]

res = np.zeros(10000)
for i in range(10000):
    res[sums[i]] += 1
print(res)
print('ok')