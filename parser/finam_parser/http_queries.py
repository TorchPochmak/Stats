from io import StringIO
import urllib
import string
import urllib.parse
import urllib.request, time
import requests
import string
from datetime import datetime as dt, timedelta as td
from distutils.dir_util import mkpath
import gzip
from datetime import datetime, timedelta
from enum import IntEnum
import pandas as pd
import numpy as np

from importlib import resources as impresources
import templates

from . import query_classes

from importlib import resources as impresources
import templates


tm_to_code = {}
markts = {}
emitents = {}

def hour_to_hour4_str(content: str, sep: str) -> str:
    content = content[:len(content) - 1]
    lst = content.split('\n')
    for i in range(0, len(lst)):
        lst[i] = lst[i].split(sep)
    columns = lst[0]
    result = ''
    result += sep.join(columns)
    #<TICKER>,<PER>,<DATE>,<TIME>,<OPEN>,<HIGH>,<LOW>,<CLOSE>,<VOL>
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

#------------------------------------------------------------------------------------------------------

#HTTP Get export stocks
def http_get_fin_data(market, code, ticker, from_date, to_date, period,
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
    #print(url)
    response = urllib.request.urlopen(url)
    content = str(response.read(), 'utf-8')

    if(period == query_classes.Period.hour4):
        content = hour_to_hour4_str(content, ',')
    return content.split('\n')

#HTTP Get export base info
def http_get_finam_info():

    # #TODO how to create unique OK cookie every time I don't know
    # #TODO хватает на 15 минут, как починить...
    # cookie = 'spid=1698239062149_ffc1617857dd0549111a40a8d63c8291_kf7exqt56wn2q8uv; spsc=1712907371376_becd01ebf431a382a66ecdffee36e8e6_2dc4c47e5beb4aae25be080fa9d16c8093e7e989cef732b63b8bada59af3d7da; _ga_P7V3S6WS35=GS1.1.1712844018.23.0.1712844018.0.0.0; _ga=GA1.1.528312804.1698239061; tmr_lvid=bb28d604036d7214ae3b51446d81667c; tmr_lvidTS=1698239061852; offfyUserId=1698239061531-0157-179f78c2c40d; _ym_uid=1706124916676408047; _ym_d=1706124916; _gcl_au=1.1.1816192709.1706124916; _pk_ref.19.2ab2=%5B%22%22%2C%22%22%2C1712840101%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.19.2ab2=08aa2af52c1a1b20.1712319279.; domain_sid=2LImXvAY5zxiGEr5nscH3%3A1712510666885; Reset=Reset; segmentsUserId=468b6795-8441-8c62-d056-4d4bb7472f24; ClientTimezoneOffset=180; segmentsData=puid1=; adtech_uid=e06b9e16-bd3d-486e-93e8-4267233daa17%3Afinam.ru; top100_id=t1.35046.835818717.1712521345285; t3_sid_35046=s1.287532151.1712521345285.1712521345285.1.1; __utma=1.528312804.1698239061.1712521345.1712521345.1; __utmz=1.1712521345.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); last_visit=1712510545546%3A%3A1712521345546; refreshPage=true; selectedAgency=1; tmr_detect=0%7C1712840103181; _ym_isad=2; spst=1712907199137_1878b457965cec5ff06cc73bd2510c6f_25acb1919f2fbe6b528d4e83a474ead3'
    # req = urllib.request.Request(
    #     url='http://www.finam.ru/cache/icharts/icharts.js', 
    #     headers= {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    #         'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    #         'Accept-Encoding': 'gzip, deflate, br',
    #         'Cookie': cookie,
    #     }
    # )
    # print('Loading markets and tickers...')
    # response = urllib.request.urlopen(req)
    # print('Complete')
    # data = str(gzip.decompress(response.read()))
    # data = bytes(data[2:], 'utf-8')
    # finam_var_list = str(data,'utf-8')

    inp_file = impresources.files('finam_parser') / 'finam_info.txt'

    # with inp_file.open("w", encoding='utf-8') as f:
    #     f.write(str(data,'utf-8'))
    # print('Complete')
    
    with inp_file.open("rt", encoding='utf-8') as f:
        data = f.read()

    finam_var_list = data
    
    js_vars = {}
    
    splitter = finam_var_list.split(']')

    for key, v in iter({'codes': 0, 'tickers': 2, 'markets': 3}.items()):
        s = splitter[v]
        js_vars[key] = s[s.find('[') + 1 : ].split(',')
        js_vars[key] = [str(js_vars[key][i]) for i in range(len(js_vars[key]))]
        if(v == 2):
            for i in range(0, len(js_vars[key])):
                js_vars[key][i] = js_vars[key][i][2:len(js_vars[key][i])-2]


    global tm_to_code, markts, emitents
    for c,t,m in zip(js_vars['codes'],js_vars['tickers'],js_vars['markets']):
        tm_to_code[(t,m)] = c
        markts.setdefault(t, []).append(m)
        emitents.setdefault(m, []).append(t.strip('\''))

#--------------------------------------------------------------------------------------------------------

def define_emitent_code(ticker, market):
    global tm_to_code
    if not tm_to_code:
        http_get_finam_info()

    name = "{}".format(ticker)

    #finam is so cringe
    if(ticker == 'TCSG'):
        return '913710'
    if(ticker == 'XBTUSD'):
        return '1822580'
    if(ticker == 'ETHUSDT'):
        return '2449224'
    if(ticker == 'VKCO'):
        return '2901666'
    return tm_to_code[(name, market)]

def define_emitent_markets(ticker):
    global markts
    if markts:
        http_get_finam_info()

    name = "'{}'".format(ticker)

    return (ticker, sorted(markts[name]))

def define_market_emitents(market):
    global emitents
    if not emitents:
        http_get_finam_info()

    return (market, sorted(emitents[market]))
