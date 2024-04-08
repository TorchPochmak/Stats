import urllib
import string
import urllib.parse
import urllib.request, time
import string
from datetime import datetime as dt, timedelta as td
from distutils.dir_util import mkpath
import gzip
from datetime import datetime, timedelta
from enum import IntEnum


class Period(IntEnum):
    tick, min1, min5, min10, min15, min30, hour, day, week, month = range(1, 11)

class Query_Parameter(IntEnum):
    market, code, date_begin, date_end, period, path = range(0,6)

# Ограничения
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
        if(period < int(Period.day)):
            interval_delta_days = 120 # 4 месяца это приблизительно 120 дней 
        else:
            interval_delta_days = 1800 #5 лет прблизительно 1800

        date_format = "%d.%m.%Y"
        start_date = datetime.strptime(start_date_str, date_format)
        end_date = datetime.strptime(end_date_str, date_format)
        
        result = []
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
        filename = 'stocks_{}_{}_{}'.format(self.queries[0][Query_Parameter.code],
                                            self.queries[0][Query_Parameter.date_begin],
                                            self.queries[len(self.queries) - 1][Query_Parameter.date_end]).replace('.', '')
        return filename
