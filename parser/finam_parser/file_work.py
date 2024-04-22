import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets
import os.path
from .query_classes import *
from .http_queries import *

from enum import StrEnum

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
    date_iso = 'date_iso' #DateTime pandas
    date_to_plot = 'date_to_plot'

COLUMNS = [COL_NAMES.ticker, COL_NAMES.per, COL_NAMES.date, COL_NAMES.time, 
    COL_NAMES.open, COL_NAMES.high, COL_NAMES.low, COL_NAMES.close, COL_NAMES.vol, COL_NAMES.date_iso, COL_NAMES.date_to_plot]

def correct_date_iso_element(element: str) -> str:
    #1302231110
    #13-02-23T11:10
    return f'{element[0:2]}-{element[2:4]}-{element[4:6]} {element[6:8]}:{element[8:10]}'

def correct_date_iso_series(frame: pd.DataFrame):
    #13-02-23T11:10
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date] + frame[COL_NAMES.time]
    frame[COL_NAMES.date_iso] = frame[COL_NAMES.date_iso].apply(correct_date_iso_element)
    frame[COL_NAMES.date_iso] = pd.to_datetime(frame[COL_NAMES.date_iso], format=f'%d-%m-%y %H:%M')

    return frame

#csv file -> pd.DataFrame
def import_from_file(filepath: str, sep: str = ',') -> pd.DataFrame:
    if(os.path.isfile(filepath) == False):
        return pd.DataFrame([])
    frame = pd.read_csv(filepath, sep=sep, dtype={'<TICKER>': str, '<PER>': str, '<DATE>': str, '<TIME>': str,
                                                  '"<OPEN>"': float, '<HIGH>': float, '<LOW>': float, '<CLOSE>': float, '<VOL>': float})
    
    frame.insert(len(frame.columns), COL_NAMES.date_iso, None)
    frame.insert(len(frame.columns), COL_NAMES.date_to_plot, None)
    frame.columns = COLUMNS
    frame = correct_date_iso_series(frame)
    frame[COL_NAMES.date_to_plot] = frame[COL_NAMES.date_iso].dt.strftime(f"%y-%m-%d\n%H-%m")
    return frame
#FinamQuery writes into csv file
