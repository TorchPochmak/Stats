import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets

import urllib.parse
import urllib.request
import string
from distutils.dir_util import mkpath

import finam_parser.tti as tti
from finam_parser.query_classes import *
import finam_parser.http_queries as queries
from finam_parser.pyplot_classes import *
import finam_parser.calc_inds as calc_inds

import finam_parser.file_work as fw
from finam_parser.plot_table import *

import pandas_ta as ta
import plotly.subplots as sp
import plotly.graph_objects as go
import yfinance as yf

df = None
stock_data = None
def zoom(layout, xrange):
    global df, stock_data
    in_view = df.loc[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
    fig.layout.yaxis.range = [in_view.High.min() - 10, in_view.High.max() + 10]

async def draw() -> None:
    global stock_data, fig
    print(stock_data.head())
    #prices_ta = calc_inds.convert_to_pandas_ta(prices)
    stock_data.ta.atr(length=14, append=True)
    stock_data.ta.rsi(length=14, append=True)   
    print(stock_data.tail())

    
    # Create subplots in a separate plane with different row heights
    fig = sp.make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=[f'{stock_data[COL_NAMES.ticker][0]} Stock Prices', 'Technical Indicators'],
                        vertical_spacing=0.1,
                        row_heights=[0.7, 0.15, 0.15, 0.15])

    # Add Stock Prices subplot
    fig.add_trace(go.Candlestick(x=stock_data.index,
                    open=stock_data[COL_NAMES.open],
                    high=stock_data[COL_NAMES.high],
                    low=stock_data[COL_NAMES.low],
                    close=stock_data[COL_NAMES.close],
                    name='Stock Prices'), row=1, col=1)

    # Add ATR subplot
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['ATRr_14'],
                    mode='lines',
                    line=dict(color='blue'),  # Set the color to blue
                    name='ATR'), row=3, col=1)

    # Add RSI subplot
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['RSI_14'],
                    mode='lines',
                    name='RSI'), row=4, col=1)

    # Update layout to set   figure size
    fig.update_layout(xaxis_rangeslider_visible=True,
                    template='plotly_dark',
                    title_text=f'{stock_data[COL_NAMES.ticker][0]} Stock Analysis',
                    #xaxis=dict(type='category'),  # Set x-axis type to category which removes the sat and sun gap4
                    yaxis = dict(autorange = True, fixedrange= False),
                    xaxis_title_text='Date',
                    yaxis_title_text='Price',
                    yaxis2 = dict(autorange = True, fixedrange= False),
                    yaxis2_title_text='ATR',  # Add y-axis title for ATR subplot
                    yaxis3 = dict(autorange = True, fixedrange= False),
                    yaxis3_title_text='RSI',  # Add y-axis title for RSI subplot
                    height=800,  # Set the height of the figure
                    width=1200)  # Set the width of the figure
    fig.layout.on_change(zoom, 'xaxis.range')
    
    # Show the figure
    fig.show()
    pass


async def main():
    global stock_data
    download_path = './DATA/'
    mkpath(download_path)
    sber2 = MoexQuery('SBER', '2022-01-10', '2023-05-15', Period.day, download_path)
    stock_data = (await MoexQuery.multi_export_to_df([sber2]))[0]
    await draw()

    pass

asyncio.run(main())
