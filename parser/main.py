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

import finam_parser
from finam_parser.query_classes import *
import finam_parser.http_queries as queries
import finam_parser.plot_classes as finam_plot

import finam_parser.file_work as fw

from finam_parser.tti.indicators import RelativeStrengthIndex

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

market = '1'
download_path = './DATA/'
mkpath(download_path)
print('Files will be in ' + download_path)

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


#? FOR INDICATORS USE BELOW because 
#? frame_indicators = frame.set_index(pd.DatetimeIndex(frame[COL_NAMES.date_iso]))


# print(f'Importing data to files({len(portfolios)})...')
# for p in portfolios:
#     fw.import_to_file(p)
# print('Complete')

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------

# fg = finam_plot.set_base_theme()
prices_main = fw.import_from_file('./DATA/' + portfolios[0].file_format() + '.txt')
print(prices_main.head())


# prices_second = fw.import_from_file('./DATA/' + portfolios[1].file_format() + '.txt')

# xsize = 192
# ysize = 108
# gs = fg.add_gridspec(xsize, ysize)
# shape_candle = finam_plot.Candle()
# shape_line = finam_plot.Line()

# center_x = int(xsize/3) * 2
# center_y = int(ysize/3) * 2

# interval_x = 8
# interval_y = 2

# #----------------------------------------------------------------------------------------
# fg_ax1 = fg.add_subplot(gs[0:center_x, 0:center_y])
# finam_plot.set_axes_theme(fg_ax1)
# finam_plot.set_xtick_freq(16, prices_main)
# shape_candle.draw(prices_main)
# #-------------------------------------------------------------------------------

# fg_ax2 = fg.add_subplot(gs[center_x + interval_x:, center_y + interval_y:])
# finam_plot.set_axes_theme(fg_ax2)
# finam_plot.set_xtick_freq(5, prices_second)

# shape_candle.draw(prices_second)

# mn = min(prices_second[fw.COL_NAMES.low])
# mx = max(prices_second[fw.COL_NAMES.high])

# mask = [prices_second[fw.COL_NAMES.date_iso][x] > prices_main[fw.COL_NAMES.date_iso][0] for x in range(0, len(prices_second))]
# df = prices_second.loc[mask]
# fg_ax2.bar(df[fw.COL_NAMES.date_iso], mx, bottom=mn, color=(1,1,1,0.3), width=1)
# #-----------------------------------------------------------------------------------
# fg_ax3 = fg.add_subplot(gs[center_x+interval_x:, 0:center_y])
# finam_plot.set_axes_theme(fg_ax3)
# finam_plot.set_xtick_freq(16, prices_main)

# rsi = RelativeStrengthIndex(input_data=prices_main)
# merge_df = pd.merge(prices_main, rsi.getTiData(), right_index=True, left_index=True)
# merge_df['rsi'] = merge_df['rsi'].fillna(0)
# shape_line.draw_xy(merge_df[fw.COL_NAMES.date_iso], merge_df['rsi'])

# #------------------------------------------------------------------------------------
# fg_ax4 = fg.add_subplot(gs[0:center_x, center_y+interval_y: ])
# finam_plot.set_axes_theme(fg_ax4)
# plt.title('DAMN', fontsize=17, position=(0.5, 0.5), color='w')
# plt.show()