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
# emitent_list = queries.define_market_emitents(market)[1]


download_path = './DATA/'
mkpath(download_path)
print('Files will be in ' + download_path)
#----------------------------------------------------------------------------------------------------
portfolios = [
    SimpleQuery('undefined', 'XBTUSD', '15.03.2023', '14.04.2024', Period.day, download_path),
    SimpleQuery('1', 'GAZP', '15.05.2022', '15.05.2023', Period.day, download_path),
]
#----------------------------------------------------------------------------------------------------
print(f'Importing data to files({len(portfolios)})...')
for p in portfolios:
    fw.import_to_file(p)
print('Complete')

#----------------------------------------------------------------------------------------------------
prices_main = fw.import_from_file('./DATA/' + portfolios[1].file_format() + '.txt')
prices_second = fw.import_from_file('./DATA/' + portfolios[1].file_format() + '.txt')

main_figure = MainFigure()
shape_candle = Candle()
shape_line = Line()

parts = grid_type3(main_figure, 2, interval_x=6, interval_y=4)

main_figure.draw_subplot(shape_candle, prices_main, parts[0], count_x=16)
main_figure.draw_subplot(shape_candle, prices_second, parts[len(parts) - 1], count_x=5)
#------------------------------------------------------------------------------------------------
rsi_frame = calc_inds.insert_ind_column(tti.indicators.RelativeStrengthIndex, prices_main)
shape_line_ind = Line()
shape_line_ind.change_columns(fw.COL_NAMES.date_to_plot, rsi_frame.columns[len(rsi_frame.columns) - 1])
shape_line_ind.color = 'white'

main_figure.draw_subplot(shape_line, rsi_frame, parts[2], count_x=16)
# shape_line.color = 'yellow'
# main_figure.draw_subplot(shape_line, rsi_frame, parts[2], count_x=16)
#------------------------------------------------------------------------------------------------
stoch_frame = calc_inds.insert_ind_column(tti.indicators.StochasticOscillator, prices_main)

shape_line_ind = Line()
shape_line_ind.change_columns(fw.COL_NAMES.date_to_plot, stoch_frame.columns[len(stoch_frame.columns) - 1])
shape_line_ind.color = 'green'

main_figure.draw_subplot(shape_line_ind, stoch_frame, parts[3], count_x=16)
#------------------------------------------------------------------------------------------------
plt.show()