import numpy as np

arr4 = np.arange(4) # [0 1 2 3]

arr3x3 = np.arange(9).reshape(3,3) 

print(arr3x3)

ar2 = arr3x3 * 2

ar3 = np.multiply(arr3x3, ar2, out=ar2) * 5 + 7
print(ar3)
