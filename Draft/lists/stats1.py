import numpy as np
data1 = [282, 226, 188, 327, 344, 304, 414, 224, 335, 270]
data2 = [417,  851,  742, 1217, 1160,  993,  864,  852, 1286,  988]
w1 = 0.4
w2 = 0.6
mean = np.mean(data1)*w1 + np.mean(data2)*w2
var1 = np.var(data1) 
#чтобы получить несмещенную, нужно ddof=1
#но здесь нужна смещенная, поэтому ddof=0 (по умолчанию)
var2 = np.var(data2)
s1 = w1*var1 + w2*var2
s2 = w1*((np.mean(data1) - mean)**2) + w2*((np.mean(data2)-mean)**2)
print(mean, s1+s2)

