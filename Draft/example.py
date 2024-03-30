import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets

import random
import math

import itertools

#object oriented
class RandomWalker:
    def __init__(self):
        self.position = 0

    def walk(self, n): #15.6 ms per loop
        self.position = 0
        for i in range(n):
            yield self.position
            self.position += 2*random.randint(0, 1) - 1 #random.randint(min, max) => [min, max]

    def random_walk(self, n): #15.7 ms per loop
        position = 0
        walk = [position]
        for i in range(n):
            position += 2*random.randint(0, 1)-1
            walk.append(position)
        return walk
    
    def random_walk_fastest(self, n): #500x faster
    # No 's' in numpy choice (Python offers choice & choices)
        steps = np.random.choice([-1,+1], n)
        return np.cumsum(steps)
walker = RandomWalker()

#walk = [position for position in walker.walk(1000)]
walk = walker.random_walk_fastest(1000)
#procedure


print(walk)

#plt.show() # if not jupiter notebook