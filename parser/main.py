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
# widgets.Dropdown(
#     options=[('One', 1), ('Two', 2), ('Three', 3)],
#     value=2,
#     description='Number:',
# )
async def main():
    download_path = './DATA/'
    mkpath(download_path)
    print('Files will be in ' + download_path)
    #----------------------------------------------------------------------------------------------------s
    def go(a):
        print(a)
    widgets.interact(go, a=[1,2,3])

    gazp = FinamQuery('1', 'GAZP', '2023-04-10', '2023-05-15', Period.hour, download_path)
    sber = FinamQuery('1', 'SBER', '2023-04-10', '2023-05-15', Period.day, download_path)
    await FinamQuery.multi_export_to_file([gazp,sber])
    lqdt = MoexQuery("LQDT", '2023-01-10', '2023-05-15', Period.hour4, download_path)
    sber2 = MoexQuery('SBER', '2023-01-10', '2023-05-15', Period.day, download_path)

    prices = await MoexQuery.multi_export_to_df([lqdt, lqdt.create_higher_TF_query()])
    prices_main = prices[0]
    prices_second = prices[1]

    main_figure = MainFigure()
    shape_candle = Candle()
    shape_line = Line()

    parts = grid_type3(main_figure, 2, interval_x=6, interval_y=4)
    main_figure.draw_subplot(shape_candle, prices_main, parts[0], count_x=16)
    fg_ax_last = main_figure.draw_subplot(shape_candle, prices_second, parts[len(parts) - 1], count_x=5)
    #------------------------------------------------------------------------------------------------
    rsi_frame = calc_inds.insert_ind_column(tti.indicators.RelativeStrengthIndex, prices_main)
    shape_line_ind = Line()
    shape_line_ind.change_columns(fw.COL_NAMES.date_to_plot, rsi_frame.columns[len(rsi_frame.columns) - 1])
    shape_line_ind.color = 'white'

    main_figure.draw_subplot(shape_line_ind, rsi_frame, parts[2], count_x=16)
    # shape_line.color = 'yellow'
    # main_figure.draw_subplot(shape_line, rsi_frame, parts[2], count_x=16)
    #------------------------------------------------------------------------------------------------
    stoch_frame = calc_inds.insert_ind_column(tti.indicators.StochasticOscillator, prices_main)

    shape_line_ind = Line()
    shape_line_ind.change_columns(fw.COL_NAMES.date_to_plot, stoch_frame.columns[len(stoch_frame.columns) - 1])
    shape_line_ind.color = 'green'

    main_figure.draw_subplot(shape_line_ind, stoch_frame, parts[3], count_x=16)
    #------------------------------------------------------------------------------------------------
    #!ANOTHER FIGURES
    mn_y_second = shape_candle.get_min_y(prices_second)
    mx_y_second = shape_candle.get_max_y(prices_second)

    rect = Rect()
    real_rect = rect.get_rect_percent(prices_second, 'left', GLOBAL_HIGHER_TF_PERCENTAGE, 'left', mn_y_second, mx_y_second)
    rect.draw_rect(fg_ax_last, real_rect)
    plt.show()

asyncio.run(main())