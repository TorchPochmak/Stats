import numpy as np
import scipy as sp
import seaborn as sns 
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets

import matplotlib.gridspec as gridspec
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
AutoMinorLocator)
import urllib.parse
import urllib.request
import string
from distutils.dir_util import mkpath

import finam_parser.tti as tti
from finam_parser.query_classes import *
import finam_parser.http_queries as queries
from finam_parser.plot_classes import *
import finam_parser.calc_inds as calc_inds

import finam_parser.file_work as fw

download_path = './DATA/'
mkpath(download_path)
print('Files will be in ' + download_path)
#----------------------------------------------------------------------------------------------------
portfolios = [
    SimpleQuery('undefined', 'ETHUSDT', '15.03.2019', '15.05.2023', Period.day, download_path),
]
#----------------------------------------------------------------------------------------------------
print(f'Importing data to files({len(portfolios)})...')
for p in portfolios:
    fw.import_to_file(p)
print('Complete')

#----------------------------------------------------------------------------------------------------
prices_main = fw.import_from_file('./DATA/' + portfolios[0].file_format() + '.txt')

distribution = pd.DataFrame(columns=['delta', 'count', 'null'])
distribution.assign()
# 'delta_range', 'count - bar_up', 'null1, 2, 3 - bar_bottom, error_bars...'
results = []
print(prices_main.head())
for i in range(1, len(prices_main)):
    results.append(
         (prices_main[fw.COL_NAMES.close][i] - prices_main[fw.COL_NAMES.open][i]) / prices_main[fw.COL_NAMES.open][i] * 100
    )

step = 0.1
left = -10
right = 10
lst = np.arange(left, right, step)
lst2 = [0 for x in range(len(lst))]
for element in results:
    if(element < lst[0] or element > lst[len(lst) - 1]):
        continue
    for i in range(0, len(lst)):
        if(element <= lst[i]):
            lst2[i] += 1
            break

distribution['delta'] = lst
distribution['count'] = lst2
distribution['null'] = np.zeros(len(lst))

print(distribution.head(100))
results_filt = []
for element in results:
    if(element > left and element < right):
        results_filt.append(element)


mf = MainFigure()

shape_candle = Line(color='grey')
shape_candle.change_columns('delta', 'count')

parts = grid_type1(mf)
mf.draw_subplot(shape_candle, distribution, parts[0], count_x=20,x_min_int=left, x_max_int=right, 
                count_y=20, y_min_int=0, y_max_int=max(distribution['count']))
mu = np.mean(results_filt)
plt.plot([mu, 0], [mu, max(distribution['count'])], linestyle='-', color='red')
sigma = np.std(results_filt)
x = np.linspace(left, right, 100)
plt.plot(x, sps.norm.pdf(x, mu, sigma)*150)
plt.text(0,max(distribution['count']), 'mean = ' + str(round(mu, 3)), color='white', fontsize=10)
plt.text(5,max(distribution['count']), 'std = ' + str(round(sigma, 3)), color='white', fontsize=10)

# prices_main['lst1'] = lst
# prices_main['lst2'] = lst2

# main_figure = MainFigure()
# shape_line = Line()

# parts = grid_type1(main_figure)

# shape_line_ind = Line()
# shape_line_ind.change_columns('lst1','lst2') 

# main_figure.draw_subplot(shape_line, prices_main, parts[0], count_x=100, count_y=50)
    # if(abs(element) > 2):
    #     continue
    # element = round(element, 2)
    # if(element not in dic):
    #     dic[element] = 1
    # else:
    #     dic[element] += 1



# sorted(dic.items())
# #fg = MainFigure()
# fg = plt.figure(figsize=(10,5))
# print(dic)
# plt.plot(lst, lst2)
plt.show()


