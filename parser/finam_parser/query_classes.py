import urllib
import string
import urllib.parse
import urllib.request, time
import string
from datetime import datetime as dt, timedelta as td
from distutils.dir_util import mkpath
import gzip
from datetime import datetime, timedelta
from enum import IntEnum, StrEnum
import pandas as pd


class Period(IntEnum):
    tick, min1, min5, min10, min15, min30, hour, day, week, month, hour4 = range(1, 12)
class Query_Parameter(IntEnum):
    market, code, date_begin, date_end, period, path = range(0,6)

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

# def calculate_high_tf_date_begin(datetime_end: pd.Timestamp) -> pd.Timestamp:
    
# Объем запрашиваемых данных в рамках одного запроса:

#     Сделки - не более чем за 1 день
#     Внутридневные свечи - не более чем за 4 месяца
#     Дневные свечи и выше - не более чем за 5 лет

#------------------------------------------------------------------------------------------------------

class SimpleQuery():
#private:
    #queries = [[market, code, date_begin1, date_end1, period, path], [market, code, date_begin2, date_end2, period, path]]
    def __init__(self, market: string, code: string, date_begin: string, date_end: string, period: Period, path: string):
        dates = self.split_date_interval(date_begin, date_end, period)
        self.queries = []
        for i in range(len(dates)):
            self.queries.append([market, code, dates[i][0], dates[i][1], period, path])
#public:    
    def split_date_interval(self, start_date_str, end_date_str, period):
        interval_delta_days = 0
        if(period < int(Period.day) or period == int(Period.hour4)):
            interval_delta_days = 120 # 4 месяца это приблизительно 120 дней 
        else:
            interval_delta_days = 1800 #5 лет прблизительно 1800

        date_format = f"%d.%m.%Y"
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

    def get_queries_list(self):
        return self.queries

    def file_format(self):
        #queries = [market, code, date_begin1, date_end1, period, path]
        filename = 'stocks_{}_{}_{}_{}'.format(self.queries[0][Query_Parameter.code],
                                            self.queries[0][Query_Parameter.period],
                                            self.queries[0][Query_Parameter.date_begin],
                                            self.queries[len(self.queries) - 1][Query_Parameter.date_end]).replace('.', '')
        return filename

    #?returns SimpleQuery
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
        return SimpleQuery(self.queries[0][Query_Parameter.market],
                           self.queries[0][Query_Parameter.code],
                           start_date_str, end_date_str, self.queries[0][Query_Parameter.period],
                           self.queries[0][Query_Parameter.path])

        