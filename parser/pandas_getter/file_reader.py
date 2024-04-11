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
    ticker = 'ticker', #str
    per = 'per', #str
    date = 'date', #str
    time = 'time', #str
    open = 'open', #float
    high = 'high', #float
    low = 'low', #float
    close = 'close', #float
    vol = 'vol', #float
    date_iso = 'date_iso' #str

COLUMNS = [COL_NAMES.ticker, COL_NAMES.per, COL_NAMES.date, COL_NAMES.time, 
    COL_NAMES.open, COL_NAMES.high, COL_NAMES.low, COL_NAMES.close, COL_NAMES.vol, COL_NAMES.date_iso]

def correct_date_iso_element(element: str) -> str:
    #1302231110
    #13-02-23T11:10
    return f'{element[0:2]}-{element[2:4]}-{element[4:6]}\n{element[6:8]}:{element[8:10]}'
# def date_iso_to_int(element: str) -> int:
#     return  int(f'{element[0:2]}9{element[3:5]}9{element[6:8]}9{element[10:12]}9{element[13:15]}')

def correct_date_iso_series(frame: pd.DataFrame):
    #13-02-23T11:10
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date] + frame[COL_NAMES.time]
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date_iso].apply(correct_date_iso_element)
    return frame

def compare_date_iso(el1: str, el2: str) -> int:
    #13-02-23T11:10
    #0  3  6  9
    if(el1[6:9] == el2[6:9]):
        if(el1[3:6] == el2[3:6]):
            if(el1[0:3] == el2[0:3]):
                if(el1[9:] == el2[9:]):
                    return 0
                else:
                    return 1 if el1[9:] > el2[9:] else -1
            else:
                return 1 if el1[0:3] > el2[0:3] else -1
        else:
            return 1 if el1[3:6] > el2[3:6] else -1
    else:
        return 1 if el1[6:9] > el2[6:9] else -1

def get_dataframe(filepath: str, sep: str = ',') -> pd.DataFrame:
    if(os.path.isfile(filepath) == False):
        return pd.DataFrame([])
    frame = pd.read_csv(filepath, sep=sep, dtype={'<TICKER>': str, '<PER>': str, '<DATE>': str, '<TIME>': str,
                                                  '"<OPEN>"': float, '<HIGH>': float, '<LOW>': float, '<CLOSE>': float, '<VOL>': float})
    
    frame.insert(len(frame.columns), COL_NAMES.date_iso, None)
    frame.columns = COLUMNS
    print(frame.head())
    return correct_date_iso_series(frame)


# prices_main = get_dataframe('./DATA/' + 'stocks_GAZP_13022022_13022023' + '.txt')