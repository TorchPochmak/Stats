import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets
import os.path

import random
import math

import itertools
from enum import StrEnum
from enum import IntEnum

class COL_NAMES(StrEnum):
    ticker = 'ticker', 
    per = 'per', 
    date = 'date', 
    time = 'time', 
    open = 'open', 
    high = 'high', 
    low = 'low',
    close = 'close', 
    vol = 'vol',
    date_iso = 'date_iso'

COLUMNS = [COL_NAMES.ticker, COL_NAMES.per, COL_NAMES.date, COL_NAMES.time, 
    COL_NAMES.open, COL_NAMES.high, COL_NAMES.low, COL_NAMES.close, COL_NAMES.vol, COL_NAMES.date_iso]

def correct_date_iso_element(element: str) -> str:
    #1302231110
    #13-02-23T11:10
    return f'{element[0:2]}-{element[2:4]}-{element[4:6]}T{element[6:8]}:{element[8:10]}'

def correct_date_iso_series(frame: pd.DataFrame):
    #13-02-2023T11:10
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date] + frame[COL_NAMES.time]
    print(frame.head())
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date_iso].apply(correct_date_iso_element)
    return frame

def get_dataframe(filepath: str, sep: str = ',') -> pd.DataFrame:
    if(os.path.isfile(filepath) == False):
        return pd.DataFrame([])
    frame = pd.read_csv(filepath, sep=sep, dtype=str)
    
    frame.insert(len(frame.columns), COL_NAMES.date_iso, None)
    frame.columns = COLUMNS
    print(frame.head())
    return correct_date_iso_series(frame)


prices_main = get_dataframe('./DATA/' + 'stocks_GAZP_13022022_13022023' + '.txt')



