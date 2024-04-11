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

import matplotlib.gridspec as gridspec
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
AutoMinorLocator)
import urllib
import string
import urllib.parse
import urllib.request
import string
from distutils.dir_util import mkpath

import finam_parser
from finam_parser.classes import *
import finam_parser.http_queries as queries
import finam_parser.import_stocks as import_stocks

from pandas_getter.file_reader import *
import pandas_getter.file_reader as fr
from abc import ABC, abstractmethod

from tti.indicators import RelativeStrengthIndex

#--------------------------------------------------------------------------------------------------------v
#  Markets:
#   MosBirzha = 1
#   MosBirzha top = 200
#   ? = 8
#   Bonds = 2
#   Indexes = 6
#   Currencies = 45
#   US(BATS) = 25, 517
#   bad markets = 91, 519
#
#  'emitents' = [(ticker, market, frame)]

# set of portfolios to iterate through looks like:

experiment_number = '0'

market = '1'
sample_number = 2
portfolio_size = 2
data_folder = ('./')
download_path = data_folder + 'DATA/'
mkpath(download_path)

print('Files will be in ' + download_path)

emitent_list = queries.define_market_emitents(market)[1]

# #SimpleQuery objects
portfolios = [
    # SimpleQuery('1', 'NLMK', '13.02.2023', '13.02.2023', Period.tick, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '13.02.2023', Period.min1, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min5, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min10, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min15, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min30, download_path), 
    # SimpleQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.hour, download_path), 
    #SimpleQuery('1', 'NLMK', '13.02.2022', '13.02.2023', Period.day, download_path), 
    SimpleQuery('1', 'GAZP', '15.03.2023', '15.05.2023', Period.hour4, download_path),
    SimpleQuery('1', 'GAZP', '15.05.2022', '15.05.2023', Period.day, download_path),
    #SimpleQuery('1', 'TCSG', '13.02.2022', '13.02.2023', Period.month, download_path),
]

print(f'Exporting data to files({len(portfolios)})...')
for p in portfolios:
    import_stocks.import_to_file(p)
print('Complete')


#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
class ShapeType(IntEnum):
    Candle, Line = range(2)
class LineType(StrEnum):
    Open, Close, High, Low = fr.COL_NAMES.open, fr.COL_NAMES.close, fr.COL_NAMES.high, fr.COL_NAMES.low

class Shape(ABC):

    @abstractmethod
    def draw(self, frame: pd.DataFrame):
        pass
    
    @property
    @abstractmethod
    def get_shape_type(self) -> ShapeType:
        pass 
class Candle(Shape):
    def __init__(self, width_candle: int = 0.9, width_min_max: int = 0.1, 
                 color_up: str = (39/256,238/256,69/256,1), color_down: str = (238/256,39/256,69/256,1)) -> None:
        self.width_candle = width_candle
        self.width_min_max = width_min_max
        self.color_up  = color_up
        self.color_down = color_down
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Candle 
    
    def draw(self, prices: pd.DataFrame):
            #only draws a line, no clue about scaling, titles and axes stuff...
            col1 = self.color_up
            col2 = self.color_down
            colors = [col1 if prices[fr.COL_NAMES.close][x] >= prices[fr.COL_NAMES.open][x] else col2 for x in range(len(prices))]
            plt.bar (prices[fr.COL_NAMES.date_iso], prices[fr.COL_NAMES.high] - prices[fr.COL_NAMES.low], 
                    self.width_min_max, bottom=prices[fr.COL_NAMES.low], color=colors, edgecolor=(0,0,0,0))
            plt.bar (prices[fr.COL_NAMES.date_iso], prices[fr.COL_NAMES.open] - prices[fr.COL_NAMES.close], 
                    self.width_candle, bottom=prices[fr.COL_NAMES.close], color=colors, edgecolor=(0,0,0,0))
    
class Line(Shape):
    def __init__(self, format: str = '-', color: str = (1,1,1,0.5), 
                 linewidth: int = 1, frame_export_type: LineType = LineType.Close):
        self.format = format
        self.color = color
        self.linewidth = linewidth
        self.frame_export_type = frame_export_type
    
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Line
    
    def draw(self, prices: pd.DataFrame):
        plt.plot(prices[fr.COL_NAMES.date_iso], prices[self.frame_export_type], 
                 self.format, linewidth=self.linewidth, color=self.color)
    def draw_xy(self, x, y):
        plt.plot(x, y, self.format, linewidth=self.linewidth, color=self.color)

grid_color = 'gray'
ticks_color = 'white'
bg_color = "#090625"

def set_base_theme():
    plt.rcParams["figure.figsize"] = [1920, 1080]
    plt.rcParams["figure.autolayout"] = True

    fg = plt.figure(facecolor=bg_color)
    return fg

def set_axes_theme(ax: plt.Axes):

    plt.xticks(fontsize=7)
    plt.yticks(fontsize=7)
    ax.tick_params(axis='x', colors=ticks_color)
    ax.tick_params(axis='y', colors=ticks_color)

    ax.set_facecolor(bg_color)

    ax.grid(which='major', linestyle='--', color=grid_color,linewidth=0.5)
    ax.grid(which='minor', linestyle='--', color=grid_color, linewidth=0.2)

    ax.spines['bottom'].set_color(ticks_color)
    ax.spines['top'].set_color(ticks_color)
    ax.spines['left'].set_color(ticks_color)
    ax.spines['right'].set_color(ticks_color)

    ax.set_axisbelow(True)

def set_xtick_freq(freq: int, frame: pd.DataFrame):
    plt.xticks(np.arange(0, len(frame), len(frame) / freq))


# ax.tick_params(which='major', length=5, width=2) #жирность черточек справа и снизу
# ax.tick_params(which='minor', length=5, width=1)

fg = set_base_theme()
prices_main = fr.get_dataframe('./DATA/' + portfolios[0].file_format() + '.txt')
prices_second = fr.get_dataframe('./DATA/' + portfolios[1].file_format() + '.txt')

xsize = 192
ysize = 108
gs = fg.add_gridspec(xsize, ysize)
shape_candle = Candle()
shape_line = Line()

center_x = int(xsize/3) * 2
center_y = int(ysize/3) * 2

interval_x = 8
interval_y = 2

#----------------------------------------------------------------------------------------
fg_ax1 = fg.add_subplot(gs[0:center_x, 0:center_y])
set_axes_theme(fg_ax1)
set_xtick_freq(16, prices_main)
shape_candle.draw(prices_main)
#-------------------------------------------------------------------------------

fg_ax2 = fg.add_subplot(gs[center_x + interval_x:, center_y + interval_y:])
set_axes_theme(fg_ax2)
set_xtick_freq(5, prices_second)
shape_candle.draw(prices_second)

prices_main[fr.COL_NAMES.date_iso][0]
mx = max(prices_second[fr.COL_NAMES.high])
mask = [True if fr.compare_date_iso(prices_second[fr.COL_NAMES.date_iso][x], prices_main[fr.COL_NAMES.date_iso][0]) > -1 else False for x in range(0, len(prices_second))]
df = prices_second.loc[mask]
fg_ax2.bar(df[fr.COL_NAMES.date_iso], mx, bottom=0, color=(1,1,1,0.3), width=1)
#-----------------------------------------------------------------------------------
fg_ax3 = fg.add_subplot(gs[center_x+interval_x:, 0:center_y])
set_axes_theme(fg_ax3)
set_xtick_freq(16, prices_main)

prices_main_ind = prices_main
prices_main_ind.set_index(pd.DatetimeIndex(prices_main_ind[fr.COL_NAMES.date_iso]))
prices_main_ind['Datetime'] = pd.to_datetime(prices_main_ind[fr.COL_NAMES.date_iso], format=f'%d-%m-%y\n%H:%M')
prices_main_ind = prices_main_ind.set_index(prices_main_ind['Datetime'])
rsi = RelativeStrengthIndex(input_data=prices_main_ind)
merge_df = pd.merge(prices_main_ind, rsi.getTiData(), right_index=True, left_index=True)
merge_df['rsi'] = merge_df['rsi'].fillna(0)
shape_line.draw_xy(merge_df[fr.COL_NAMES.date_iso], merge_df['rsi'])

#------------------------------------------------------------------------------------
fg_ax4 = fg.add_subplot(gs[0:center_x, center_y+interval_y: ])
set_axes_theme(fg_ax4)
plt.title('DAMN', fontsize=17, position=(0.5,
    0.5), color='w')
plt.show()
# width_candle = 0.95
# width_min_max = 0.3
# #define up and down prices


# #define colors to use
# col1 = 'green'
# col2 = 'red'

# #rotate x-axis tick labels
# plt.xticks (rotation= 45 , ha='right')

# prices['EWMA30'] = prices['close'].ewm(span=30).mean()
# prices['EWMA30'].plot()
# my_dpi = 96
# plt.figure(figsize=(800/my_dpi * 10, 800/my_dpi * 10), dpi=my_dpi)


#display candlestick chart
# fg = plt.figure(figsize=(9, 9), constrained_layout=True)
# gs = fg.add_gridspec(5, 5)
# fig_ax_1 = fg.add_subplot(gs[0, :3])
# fig_ax_1.set_title('gs[0, :3]')
# fig_ax_2 = fg.add_subplot(gs[0, 3:])
# fig_ax_2.set_title('gs[0, 3:]')
# fig_ax_3 = fg.add_subplot(gs[1:, 0])
# fig_ax_3.set_title('gs[1:, 0]')
# 42
# fig_ax_4 = fg.add_subplot(gs[1:, 1])
# fig_ax_4.set_title('gs[1:, 1]')
# fig_ax_5 = fg.add_subplot(gs[1, 2:])
# fig_ax_5.set_title('gs[1, 2:]')
# fig_ax_6 = fg.add_subplot(gs[2:4, 2])
# fig_ax_6.set_title('gs[2:4, 2]')
# fig_ax_7 = fg.add_subplot(gs[2:4, 3:])
# fig_ax_7.set_title('gs[2:4, 3:]')
# fig_ax_8 = fg.add_subplot(gs[4, 3:])
# fig_ax_8.set_title('gs[4, 3:]')

