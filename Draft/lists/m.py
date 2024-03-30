import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets
import matplotlib.style as mplstyle
mplstyle.use('fast')
import random
import math

import itertools

prices_main = pd.read_csv('C:/Users/TorchPochmak/Desktop/STATS/lists/VKCO_dec.csv', sep=';')
prices_main.columns = ['ticker', 'per', 'date', 'time', 'open', 'high', 'low',
       'close', 'vol']

#define width of candlestick elements

last = 200
prices = prices_main.tail(last)
width = 0.9
width2 = 0.3
print(prices['date'][667])
#define up and down prices
up = prices[prices['close'] >= prices['open'] ]
down = prices[prices['close'] < prices['open'] ]

#define colors to use
col1 = 'green'
col2 = 'red'
my_dpi = 96
plt.figure(figsize=(800/my_dpi, 800/my_dpi), dpi=my_dpi)
#plot up prices
plt.bar (up.index , up['close'] - up['open'] ,width,bottom=up['open'] ,color=col1)
plt.bar (up.index ,up['high'] -up['close'] ,width2,bottom=up['close'] ,color=col1)
plt.bar (up.index ,up['low'] -up['open'] ,width2,bottom=up['open'] ,color=col1)

#plot down prices
plt.bar (down.index ,down['close'] -down['open'] ,width,bottom=down['open'] ,color=col2)
plt.bar (down.index ,down['high'] -down['open'] ,width2,bottom=down['open'] ,color=col2)
plt.bar (down.index ,down['low'] -down['close'] ,width2,bottom=down['close'] ,color=col2)

#rotate x-axis tick labels
plt.xticks (rotation= 45 , ha='right')
#plt.figure(figsize=(8, 8))
#plt.subplot(2, 1, 1)

prices['EWMA30'] = prices['close'].ewm(span=30).mean()
prices['EWMA30'].plot()

def rma(x, n, y0):
    a = (n-1) / n
    ak = a**np.arange(len(x)-1, -1, -1)
    return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]
n = 14
prices['change'] = prices['close'].diff()
prices['gain'] = prices.change.mask(prices.change < 0, 0.0)
prices['loss'] = -prices.change.mask(prices.change > 0, -0.0)
prices['avg_gain'] = rma(prices.gain[n+1:].to_numpy(), n, np.nansum(prices.gain.to_numpy()[:n+1])/n)
prices['avg_loss'] = rma(prices.loss[n+1:].to_numpy(), n, np.nansum(prices.loss.to_numpy()[:n+1])/n)
prices['rs'] = prices.avg_gain / prices.avg_loss
prices['rsi_14'] = 100 - (100 / (1 + prices.rs))
#plt.subplot(2, 1, 2)
prices['rsi_14'].plot()


# mng = plt.get_current_fig_manager()
# mng.full_screen_toggle()
#display candlestick chart
plt.show() 