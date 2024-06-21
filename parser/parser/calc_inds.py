from enum import StrEnum
import parser.query_classes as queries
import parser.pyplot_classes 

from typing import Type

from distutils.dir_util import mkpath

import parser.tti as tti

import numpy as np
import pandas as pd
import pandas_ta as ta

class COL_TA(StrEnum):
    ticker = 'Ticker', #str
    per = 'Per', #str
    date = 'Date', #str
    time = 'Time', #str
    open = 'Open', #float
    high = 'High', #float
    low = 'Low', #float
    close = 'Close', #float
    vol = 'Volume', #float
    date_iso = 'Date_iso' #DateTime pandas
    date_to_plot = 'Date_to_plot'

COLUMNS_TA = [COL_TA.ticker, COL_TA.per, COL_TA.date, COL_TA.time, 
    COL_TA.open, COL_TA.high, COL_TA.low, COL_TA.close, COL_TA.vol, COL_TA.date_iso, COL_TA.date_to_plot]


def insert_ind_column(indicator_type: Type[tti.indicators._technical_indicator.TechnicalIndicator], frame: pd.DataFrame) -> pd.DataFrame: 
    frame_dates = frame.set_index(pd.DatetimeIndex(frame[queries.COL_NAMES.date_iso]))
    ind = indicator_type(input_data=frame_dates)
    res = ind.getTiData()
    merge_df = pd.merge(frame_dates, res, right_index=True, left_index=True)
    name = res.columns[0]
    merge_df[name] = merge_df[name].fillna(0)
    merge_df = merge_df.set_index(np.arange(len(merge_df)))
    return merge_df