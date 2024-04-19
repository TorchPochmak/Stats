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
#SimpleQuery writes into csv file
def import_to_file(query: SimpleQuery) -> None:
    
    result = []

    data = query.get_queries_list()
    for i in range(len(data)):
        ticker = data[i][Query_Parameter.code]
        market = data[i][Query_Parameter.market]
        code = define_emitent_code(ticker, market)

        #print(len(data[i][Query_Parameter.date_begin]))
        from_date = dt.strptime(data[i][Query_Parameter.date_begin], f"%d.%m.%Y").date()
        to_date = dt.strptime(data[i][Query_Parameter.date_end], f"%d.%m.%Y").date()
        #print(ticker, market, code)
        dat_list = http_get_fin_data(market, code, ticker, from_date,
                           to_date, data[i][Query_Parameter.period])
        dat_list[len(dat_list) - 1] += '\r'
        if(i != 0):
            result += dat_list[1:]
        else:
            result += dat_list
        time.sleep(1)
    filename = query.file_format()
    full_path = data[0][Query_Parameter.path] + filename + '.txt'
    print('Loaded: ', full_path)
    with open(full_path, 'w') as f:
        for item in result:
            f.write("{}".format(item))
