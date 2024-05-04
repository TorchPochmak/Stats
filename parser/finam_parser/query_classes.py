from abc import ABC, abstractmethod
import os
import urllib
import string
import urllib.parse
import urllib.request, time
from datetime import datetime as dt, timedelta as td
from distutils.dir_util import mkpath
import gzip
from datetime import datetime, timedelta
from enum import IntEnum, StrEnum
import aiomoex
import pandas as pd
from io import StringIO
from typing import List
import requests
import string
import numpy as np

from . import query_classes
from . import http_queries

from importlib import resources as impresources
import templates
import aiohttp
import asyncio


class Period(IntEnum):
    tick, min1, min5, min10, min15, min30, hour, day, week, month, hour4 = range(1, 12)
class Query_Parameter(IntEnum):
    market, code, date_begin, date_end, period, path = range(0,6)
class Query_Type(IntEnum):
    FinamQuery, MoexQuery = range(0,2)

DICT_PERIOD_NAMES = {
    Period.tick :   '0',#!didn't analyze lol
    Period.min1 :   '1', 
    Period.min5 :   '5',
    Period.min10 :  '10', 
    Period.min15 :  '15',
    Period.min30 :  '30',
    Period.hour :   '60',
    Period.hour4 :  '240', 
    Period.day :    'D', 
    Period.week :   'W', 
    Period.month:   'M',
}
    
DICT_HIGHER_TIMEFRAME = {
    Period.tick :   [Period.min1, 5.],#!didn't analyze lol
    Period.min1 :   [Period.min5, 5.], #*5
    Period.min5 :   [Period.min15, 3.],#*3
    Period.min10 :  [Period.min30, 3.], #*3
    Period.min15 :  [Period.hour,  4.],#*4
    Period.min30 :  [Period.hour, 2.],#*2
    Period.hour :   [Period.hour4, 4.],#*4
    Period.hour4 :  [Period.day, 4.], #*6
    Period.day :    [Period.week, 7.], #*7
    Period.week :   [Period.month, 4.], #*4
}

GLOBAL_HIGHER_TF_PERCENTAGE = 0.4

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

def hour_to_hour4_str(content: str, sep: str) -> str:
    content = content[:len(content) - 1]
    lst = content.split('\n')
    for i in range(0, len(lst)):
        lst[i] = lst[i].split(sep)
    columns = lst[0]
    result = ''
    result += sep.join(columns)
    #<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
    #ticker, per, date, time, open, high, low, close, vol
    i = 1
    while(i < len(lst)):
        result += '\r\n'
        plus = 4
        if(lst[i][3] == '2300'):
            plus = 2
        high = float(lst[i][5])
        low = float(lst[i][6])
        close = float(lst[i][7])
        vol = float(lst[i][8])
        for j in range(i + 1, min(len(lst), i + plus)):
            high = np.fmax(high, float(lst[j][5]))
            low = np.fmin(low, float(lst[j][6]))
            close = float(lst[j][7])
            vol += float(lst[j][8])
        result += sep.join([lst[i][0], '240', lst[i][2], lst[i][3], lst[i][4], str(high), str(low), str(close), str(vol)])
        i += plus
    return result

def hour_to_hour4_frame(content: pd.DataFrame, sep: str) -> pd.DataFrame:
    result = ''
    for col in content.columns:
        result += col + sep
    result += '\n'
    for index, element in content.iterrows():
        for col in content.columns:
            result += str(element[col]) + sep
        result += '\n'
    result = hour_to_hour4_str(result, sep)
    lst = result.split('\n')
                
    df = [x.split(',') for x in lst if x]
    df = pd.DataFrame(df[1:], columns=COLUMNS[:-2])
    df = df.astype(dtype={'ticker': str, 'per': str, 'date': str, 'time': str,
                                        'open': float, 'high': float, 'low': float, 'close': float, 'vol': float})
    return df

def swap_columns (df, col1, col2):
    col_list = list(df.columns)
    x, y = col_list. index (col1), col_list. index (col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df
class Query(ABC):

    @staticmethod
    def multi_export_to_df(list_queries) -> List[pd.DataFrame]:
        raise SyntaxError

    @staticmethod
    def multi_export_to_file(list_queries) -> None:
        raise SyntaxError

    def file_format(self) -> str:
        raise SyntaxError

    def create_higher_TF_query(self): #same subtype as self
        raise SyntaxError

    @staticmethod
    def import_from_file(filepath: str, sep: str = ',') -> pd.DataFrame:
        if(os.path.isfile(filepath) == False):
            return pd.DataFrame([])
        frame = pd.read_csv(filepath, sep=sep, dtype={'ticker': str, 'per': str, 'date': str, 'time': str,
                                                    'open': float, 'high': float, 'low': float, 'close': float, 'vol': float})
        return frame
        
    @staticmethod
    def correct_frame(frame: pd.DataFrame) -> pd.DataFrame:
        frame.insert(len(frame.columns), COL_NAMES.date_iso, None)
        frame.insert(len(frame.columns), COL_NAMES.date_to_plot, None)
        frame.columns = COLUMNS
        frame = correct_date_iso_series(frame)
        frame[COL_NAMES.date_to_plot] = frame[COL_NAMES.date_iso].dt.strftime(f"%y-%m-%d\n%H-%m")
        return frame
class FinamQuery(Query):
#private:
    #queries = [[market, code, date_begin1, date_end1, period, path], [market, code, date_begin2, date_end2, period, path]]
    def __init__(self, market: string, code: string, date_begin: string, date_end: string, period: Period, path: string):
        dates = self.split_date_interval(date_begin, date_end, period)
        self.queries = []
        for i in range(len(dates)):
            self.queries.append([market, code, dates[i][0], dates[i][1], period, path])
        
    def split_date_interval(self, start_date_str, end_date_str, period):
        interval_delta_days = 0
        if(period < int(Period.day) or period == int(Period.hour4)):
            interval_delta_days = 120 # 4 месяца это приблизительно 120 дней 
        else:
            interval_delta_days = 1800 #5 лет прблизительно 1800

        date_format = f"%Y-%m-%d"
        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)
        
        result = []
        if(start_date == end_date):
            return [(start_date.strftime(date_format), end_date.strftime(date_format))]
        while start_date < end_date:
            next_date = start_date + timedelta(days=interval_delta_days) 
            if next_date > end_date:  # Если следующая дата выходит за пределы интервала, приводим её к конечной дате
                next_date = end_date
            result.append((start_date.strftime(date_format), next_date.strftime(date_format)))
            start_date = next_date  # Переходим к следующему периоду
        return result

    #------------------------------------------------------------------------------------------------------
    @staticmethod
    def get_url(market, code, ticker, from_date, to_date, period,
                dtf=3, tmf=2, msor=1, sep=1, sep2=1, datf=1, at=1, fsp=1):
        from_str = from_date.strftime("%d.%m.%Y")
        to_str = to_date.strftime("%d.%m.%Y")

        period_new = period
        if(period_new == query_classes.Period.hour4):
            period_new = query_classes.Period.hour
        params  = [ ('market', market),                 #market code
                    ('em', code),                       #instrument code
                    ('code', ticker),                   #instrument ticker
                    ('apply', 0),                       #?
                    ('df', from_date.day),              #period start, day
                    ('mf', from_date.month-1),          #period start, month
                    ('yf', from_date.year),             #period start, year
                    ('from', from_str),                 #period start
                    ('dt', to_date.day),                #period end, day
                    ('mt', to_date.month-1),            #period end, month
                    ('yt', to_date.year),               #period end, year
                    ('to', to_str),                     #period end
                    ('p', period_new.value),                #period type
                    ('f', 'data'),                      #file name
                    ('e', '.txt'),                      #file type
                    ('cn', ticker),                     #contract name
                    ('dtf',  dtf),                      #date format
                    ('tmf',  tmf),                      #time format
                    ('MSOR', msor),                     #candle time(0-open,1-close)
                    ('mstime', 'on'),                   #moscow time (optional)
                    ('mstimever', 1),                   #timezone correction
                    ('sep',  sep),                      #elements separator
                    ('sep2', sep2),                     #digits separator
                    ('datf', datf),                     #column selection
                    ('at',   at),                       #headers presence (optional)
                    ('fsp',  fsp),                      #fill periods w/o trades
        ]

        url = ('http://export.finam.ru/{}.txt?'.format(ticker)
            + urllib.parse.urlencode(params))
        return url

    @staticmethod
    async def fetch_FinamQuery(url, session, simple_query):
        async with session.get(url, ssl=False) as response:
            data = await response.text()
            if(simple_query.queries[0][query_classes.Query_Parameter.period] == query_classes.Period.hour4):
                data = hour_to_hour4_str(data, ',')
            return [data.split('\n'), simple_query]
        
    @staticmethod
    async def fetch_all(urls, list_Simplequeries):
        async with aiohttp.ClientSession() as session:
            tasks = [FinamQuery.fetch_FinamQuery(urls[i], session, list_Simplequeries[i])
                    for i in range(len(urls))]
            results = await asyncio.gather(*tasks)
            return results

    @staticmethod
    async def get_df_query_pair(list_queries):
    #------------------------------------------------------------------------------------------------------
        urls = []
        simple_queries = []
        for index in range(len(list_queries)):
            queries = list_queries[index].queries
            for j in range(len(queries)):
                ticker = queries[j][query_classes.Query_Parameter.code]
                market = queries[j][query_classes.Query_Parameter.market]
                code = http_queries.define_emitent_code(ticker, market)

                #print(len(data[i][Query_Parameter.date_begin]))
                from_date = dt.strptime(queries[j][query_classes.Query_Parameter.date_begin], f"%Y-%m-%d").date()
                to_date = dt.strptime(queries[j][query_classes.Query_Parameter.date_end], f"%Y-%m-%d").date()
                #print(ticker, market, code)
                url = FinamQuery.get_url(market, code, ticker, from_date, to_date, queries[j][query_classes.Query_Parameter.period])
                urls.append(url)
                simple_queries.append(list_queries[index])
        
        #-----------
        results = await FinamQuery.fetch_all(urls, simple_queries)
        #------------

        last_query = results[0][1]
        ind = 0

        RES = []
        while(ind < len(results)):
            res_data = []
            dat_list = [results[i][0] for i in range(ind, ind + len(last_query.queries))]
            for j in range(len(last_query.queries)):
                if(j != 0):
                    res_data += dat_list[j][1:]
                else:
                    res_data += dat_list[j]
            
            df = [x.split(',') for x in res_data if x]
            df = pd.DataFrame(df[1:], columns=COLUMNS[:-2])
            df = df.astype(dtype={'ticker': str, 'per': str, 'date': str, 'time': str,
                                                    'open': float, 'high': float, 'low': float, 'close': float, 'vol': float})
            RES.append([Query.correct_frame(df), last_query])
            ind += len(last_query.queries)
            if(ind >= len(results)):
                break
            last_query = results[ind][1]
        return RES

#public ABSTRACT
    def file_format(self) -> str:
        #queries = [market, code, date_begin1, date_end1, period, path]
        filename = 'stocks_{}_{}_{}_{}'.format(self.queries[0][Query_Parameter.code],
                                            self.queries[0][Query_Parameter.period],
                                            self.queries[0][Query_Parameter.date_begin],
                                            self.queries[len(self.queries) - 1][Query_Parameter.date_end]).replace('.', '')
        return filename

    def create_higher_TF_query(self):
        check = DICT_HIGHER_TIMEFRAME[self.queries[0][Query_Parameter.period]]
        percent = 1. / check[1]
        start = self.queries[0][Query_Parameter.date_begin]
        end = self.queries[len(self.queries) - 1][Query_Parameter.date_end]
        # Данные
        date_format = f"%d.%m.%Y"

        start_date = datetime.strptime(start, date_format)
        end_date = datetime.strptime(end, date_format)

        duration = end_date - start_date
        duration /= percent
        duration = percent * duration / GLOBAL_HIGHER_TF_PERCENTAGE
        true_start_date = end_date - duration


        start_date_str = datetime.strftime(true_start_date, format=date_format)
        end_date_str = datetime.strftime(end_date, format=date_format)
        return FinamQuery(self.queries[0][Query_Parameter.market],
                           self.queries[0][Query_Parameter.code],
                           start_date_str, end_date_str, check[0],
                           self.queries[0][Query_Parameter.path])
    #List[query_classes.FinamQuery]
    @staticmethod
    async def multi_export_to_file(list_queries) -> None:
        res = await FinamQuery.get_df_query_pair(list_queries)
        for element in res:
            filename = element[1].file_format()
            full_path = element[1].queries[0][query_classes.Query_Parameter.path] + filename + '.txt'
            print('Loaded: ', full_path)
            element[0].to_csv(full_path, index=False)

    @staticmethod
    async def multi_export_to_df(list_queries)-> List[pd.DataFrame]:
            res = await FinamQuery.get_df_query_pair(list_queries)
            r = [x[0] for x in res]
            return r
class MoexQuery():
    def __init__(self, code: string, date_begin: string, date_end: string, period: Period, path: string):
        self.period = period
        self.code = code
        self.date_begin = date_begin
        self.date_end = date_end
        self.path = path
        self.interval = self.define_moex_interval(period)

    def normalize_df(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame.insert(0, COL_NAMES.ticker, self.code)
        frame.insert(1, COL_NAMES.per, DICT_PERIOD_NAMES[self.period])
        frame.insert(2, COL_NAMES.date, None)
        frame.insert(3, COL_NAMES.time, None)
        frame[COL_NAMES.date] = frame['begin']
        frame[COL_NAMES.date] = frame[COL_NAMES.date].apply(lambda x: x[8:10] + x[5:7] + x[2:4])
        frame[COL_NAMES.time] = frame['begin']
        frame[COL_NAMES.time] = frame[COL_NAMES.time].apply(lambda x: x[11:13] + x[14:16])


        frame = swap_columns(frame, COL_NAMES.close, 'value')
        frame = frame.drop(columns=['value', 'begin', 'end'])
        return frame

    def define_moex_interval(self, period: Period) -> int:
        if(period == Period.min1):
            return 1
        if(period == Period.min10):
            return 10
        if(period == Period.hour):
            return 60
        if(period == Period.hour4):
            return 240
        if(period == Period.day):
            return 24
        if(period == Period.week):
            return 7
        if(period == Period.month):
            return 31
        else:
            raise ValueError
    @staticmethod
    async def fetch_MoexQuery(query):
        async with aiohttp.ClientSession() as session:
            period = query.interval
            if(period == 240):
                period = 60
            data = await aiomoex.get_market_candles(session, query.code, interval=period, 
                                                    start=query.date_begin, 
                                                    end=query.date_end)
            data = pd.DataFrame(data)
            if(data.empty):
                print("ERROR: dataframe is empty")
                print("Code: " + str(query.code))
                print("Period: " + str(query.period))
                print("Start_date " + str(query.date_begin))
                print("End_date " + str(query.date_end))
                raise ValueError
            #TODO NORMALIZE DF
            data = query.normalize_df(data)
            if(query.interval == 240):
                data = hour_to_hour4_frame(data, ',')
            data = Query.correct_frame(data)
            return data

    @staticmethod
    async def fetch_all(list_queries):
        async with aiohttp.ClientSession() as session:
            tasks = [MoexQuery.fetch_MoexQuery(list_queries[i])
                    for i in range(len(list_queries))]
            results = await asyncio.gather(*tasks)
            return results

    @staticmethod
    async def multi_export_to_df(list_queries) -> List[pd.DataFrame]:
        results = await MoexQuery.fetch_all(list_queries)
        return results

    @staticmethod
    # list_queries: List[MoexQuery]
    async def multi_export_to_file(list_queries) -> None:
        results = await MoexQuery.fetch_all(list_queries)
        for i in range(len(list_queries)):
            filename = list_queries[i].file_format()
            full_path = list_queries[i].path + filename + '.txt'
            print('Loaded: ', full_path)
            results[i].to_csv(full_path, index=False)

    def file_format(self) -> str:
        filename = 'stocks_{}_{}_{}_{}'.format(self.code,
                                            self.period,
                                            self.date_begin,
                                            self.date_end).replace('.', '')
        return filename

    def create_higher_TF_query(self): #same subtype as self
        # print(check)
        check = DICT_HIGHER_TIMEFRAME[self.period]
        percent = 1. / check[1]
        start = self.date_begin
        end = self.date_end
        # Данные
        date_format = f"%Y-%m-%d"

        start_date = datetime.strptime(start, date_format)
        end_date = datetime.strptime(end, date_format)

        duration = end_date - start_date
        duration /= percent
        duration = percent * duration / GLOBAL_HIGHER_TF_PERCENTAGE
        true_start_date = end_date - duration


        start_date_str = datetime.strftime(true_start_date, format=date_format)
        end_date_str = datetime.strftime(end_date, format=date_format)
        return MoexQuery(self.code,
                        start_date_str, end_date_str, check[0],
                        self.path)