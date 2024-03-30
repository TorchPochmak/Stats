import numpy as np
# import scipy as sp
# import seaborn as sns
# import matplotlib.pyplot as plt
# import scipy.stats as sps
# import pandas as pd
# import ipywidgets as widgets

# import random
# import math

# import itertools

#numpy.ndarray
zeros = np.zeros(10, np.int64)
ones = np.ones(10, np.float32) # [1.,1.,1. and so on]
arr4 = np.arange(4) # [0 1 2 3]
array2x2 = arr4.reshape(2,2)# [[0 1] [2 3]]
arr4 = arr4.astype(np.float32) # [0. 1. 2. 3.]
(arr4[0], arr4[1]) = (arr4[1], arr4[0])
arr4.sort()

#вырез для детерминанта
arr3 = np.arange(9).reshape(3,3)
print(arr3)
v = arr3[::2, ::2]
print(v)
print(arr3.size)

Z = np.zeros(9)
index = [0,1,2]
Z[index] = 1
index = [i for i in range(0, 9)]
index = index[::2]
Z[index] += 10

print(Z)
