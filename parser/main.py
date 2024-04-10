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

import urllib
import string
import urllib.parse
import urllib.request
import string
from distutils.dir_util import mkpath

import finam_parser
from finam_parser.classes import *
import finam_parser.http_queries as queries
import finam_parser.export as export

from pandas_getter.file_reader import *
import pandas_getter.file_reader as fr
from abc import ABC, abstractmethod
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

#SimpleQuery objects
portfolios = [
    SimpleQuery('1', 'NLMK', '13.02.2022', '13.02.2023', Period.hour, download_path), 
    SimpleQuery('1', 'GAZP', '13.02.2022', '13.02.2023', Period.day, download_path)
]

print(f'Exporting data to files({len(portfolios)})...')
for p in portfolios:
    export.export_to_file(p)
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
    def __init__(self, width_candle: int = 0.95, width_min_max: int = 0.3, 
                 color_up: str = 'green', color_down: str = 'red') -> None:
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

        up = prices[prices[fr.COL_NAMES.close] >= prices[fr.COL_NAMES.open]]
        down = prices[prices[fr.COL_NAMES.close] < prices[fr.COL_NAMES.open]]
        #plot up prices
        plt.bar (up[fr.COL_NAMES.date_iso], up[fr.COL_NAMES.close] - up[fr.COL_NAMES.open], self.width_candle, bottom=up[fr.COL_NAMES.open], color=col1)
        plt.bar (up[fr.COL_NAMES.date_iso], up[fr.COL_NAMES.high] - up[fr.COL_NAMES.close], self.width_min_max, bottom=up[fr.COL_NAMES.close], color=col1)
        plt.bar (up[fr.COL_NAMES.date_iso], up[fr.COL_NAMES.low] - up[fr.COL_NAMES.open], self.width_min_max, bottom=up[fr.COL_NAMES.open], color=col1)

        #plot down prices
        plt.bar (up[fr.COL_NAMES.date_iso], down[fr.COL_NAMES.close] - down[fr.COL_NAMES.open], self.width_candle, bottom=down[fr.COL_NAMES.open], color=col2)
        plt.bar (up[fr.COL_NAMES.date_iso], down[fr.COL_NAMES.high] - down[fr.COL_NAMES.open], self.width_min_max, bottom=down[fr.COL_NAMES.open], color=col2)
        plt.bar (up[fr.COL_NAMES.date_iso], down[fr.COL_NAMES.low] - down[fr.COL_NAMES.close], self.width_min_max, bottom=down[fr.COL_NAMES.close], color=col2)


class Line(Shape):
    def __init__(self, format: str = '-', color: str = 'black', 
                 linewidth: int = 1, frame_export_type: LineType = LineType.Close):
        self.format = format
        self.color = color
        self.linewidth = linewidth
        self.frame_export_type = frame_export_type
    
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Line
    
    @property
    def draw(self, prices: pd.DataFrame):
        plt.plot(prices[fr.COL_NAMES.date_iso], prices[self.frame_export_type], 
                 self.format, linewidth=self.linewidth, color=self.color)


prices_main = fr.get_dataframe('./DATA/' + portfolios[1].file_format() + '.txt')
shape_candle = Candle()
shape_candle.draw(prices_main)

shape_line = Line()
shape_line.draw(prices_main)

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

