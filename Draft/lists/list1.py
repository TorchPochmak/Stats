import numpy as np
import pandas as pd


#?Cпособ задать np.array
#numpy "ndarray" (also has alias array, numpy.array)
a = np.arange(5) # [0 1 2 3 4]
a = np.zeros(5) # [0 0 0 0 0], float64
a = np.ones(5) # [1 1 1 1 1], float64

#?Конвертация
std_a = [1,2,3,4,5]
a = np.array(std_a) #convert to np.ndarray
set_a = set(a)
lst_a = list(a)
tuple_a = tuple(a)


#?Свойства (attributes)
a = np.arange(12).reshape(2,3)


#?Half-useless
a = np.arange(6).reshape(2,3) + 10
#array([[10, 11, 12],
#       [13, 14, 15]])

#?Useless
a = np.array([1,2,3,4,1,0]) #Проверка на (exist)False/0
print(np.ndarray.all(a)) #False
#--------
a = np.array([1,2,3,4,1,0]) #Проверка на (exist)True/0
print(np.ndarray.any(a)) #True
#--------