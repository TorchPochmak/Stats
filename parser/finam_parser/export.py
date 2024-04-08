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

from .classes import *
from .http_queries import *

#SimpleQuery
def export_to_file(query: SimpleQuery):
    
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
