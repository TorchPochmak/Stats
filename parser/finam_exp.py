import urllib
import string
import urllib.parse
import urllib.request, time
import string
from enum import Enum
from datetime import datetime as dt, timedelta as td
from distutils.dir_util import mkpath
import random
import gzip
from datetime import datetime, timedelta
from enum import IntEnum

tm_to_code = {}
markts = {}
emitents = {}

# Ограничения
# Объем запрашиваемых данных в рамках одного запроса:

#     Сделки - не более чем за 1 день
#     Внутридневные свечи - не более чем за 4 месяца
#     Дневные свечи и выше - не более чем за 5 лет

class Period(IntEnum):
    tick, min1, min5, min10, min15, min30, hour, day, week, month = range(1, 11)
class Query_Parameter(IntEnum):
    market, code, date_begin, date_end, period, path = range(0,6)
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

def get_fin_data(market, code, ticker, from_date, to_date, period,
    dtf=3, tmf=2, msor=1, sep=1, sep2=1, datf=1, at=1, fsp=1):

    from_str = from_date.strftime("%d.%m.%Y")
    to_str = to_date.strftime("%d.%m.%Y")

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
                ('p', period.value),                #period type
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
    return content.split('\n')

#SimpleQuery
def gather_finam_data(query: SimpleQuery):
    
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
        dat_list = get_fin_data(market, code, ticker, from_date,
                           to_date, data[i][Query_Parameter.period])
        result += dat_list
        time.sleep(1)
    filename = query.file_format()
    full_path = data[0][Query_Parameter.path] + filename + '.txt'
    print('Loaded: ', full_path)
    with open(full_path, 'w') as f:
        for item in result:
            f.write("{}\n".format(item))

def load_finam_vars():

    #TODO how to create unique OK cookie every time I don't know
    #TODO хватает на 15 минут, как починить...
    cookie = 'spid=1698239062149_ffc1617857dd0549111a40a8d63c8291_kf7exqt56wn2q8uv; spsc=1712577807745_349d040f796ac44a9301d594053f85e9_f2d542cfcf981c77ce9ddd47fd2929671197ab0726285e57567f36c39ecf5bfc; _ga_P7V3S6WS35=GS1.1.1712577814.15.0.1712577814.0.0.0; _ga=GA1.1.528312804.1698239061; tmr_lvid=bb28d604036d7214ae3b51446d81667c; tmr_lvidTS=1698239061852; offfyUserId=1698239061531-0157-179f78c2c40d; _ym_uid=1706124916676408047; _ym_d=1706124916; _gcl_au=1.1.1816192709.1706124916; _pk_ref.19.2ab2=%5B%22%22%2C%22%22%2C1712577825%2C%22https%3A%2F%2Fwww.google.com%2F%22%5D; _pk_id.19.2ab2=08aa2af52c1a1b20.1712319279.; domain_sid=2LImXvAY5zxiGEr5nscH3%3A1712510666885; _ym_isad=2; tmr_detect=0%7C1712577825239; Reset=Reset; segmentsUserId=468b6795-8441-8c62-d056-4d4bb7472f24; ClientTimezoneOffset=180; NewsBeltSection=1; segmentsData=puid1=; adtech_uid=e06b9e16-bd3d-486e-93e8-4267233daa17%3Afinam.ru; top100_id=t1.35046.835818717.1712521345285; t3_sid_35046=s1.287532151.1712521345285.1712521345285.1.1; __utma=1.528312804.1698239061.1712521345.1712521345.1; __utmz=1.1712521345.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); last_visit=1712510545546%3A%3A1712521345546; srv_id=8d50819b9209f56df78bc3b60cac8d7e; spst=1712577661909_eaa246c3a6e38c6f99f6ddb12645f40f_25acb1919f2fbe6b528d4e83a474ead3; spsn=1712577807745_7b2276657273696f6e223a22332e342e32222c227369676e223a223165303663363934613231313262666432326430333230643863396633356130222c22706c6174666f726d223a2257696e3332222c2262726f7773657273223a5b5d2c2273636f7265223a302e367d; _ym_visorc=b; _pk_ses.19.2ab2=1'
    req = urllib.request.Request(
        url='http://www.finam.ru/cache/icharts/icharts.js', 
        headers= {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': cookie,
        }
    )
    print('Loading markets and tickers...')
    response = urllib.request.urlopen(req)
    print('Complete')
    data = str(gzip.decompress(response.read()))
    data = bytes(data[2:], 'utf-8')
    finam_var_list = str(data,'utf-8')

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

def define_emitent_code(ticker, market):
    global tm_to_code
    if not tm_to_code:
        load_finam_vars()

    name = "{}".format(ticker)

    return tm_to_code[(name, market)]

def get_emitent_markets(ticker):
    global markts
    if not markts:
        load_finam_vars()

    name = "'{}'".format(ticker)

    return (ticker, sorted(markts[name]))

def get_market_emitents(market):
    global emitents
    if not emitents:
        load_finam_vars()

    return (market, sorted(emitents[market]))

#--------------------------------------------------------------------------------------------------------v
#  Markets:
#   MosBirzha = 1
#   MosBirzha top = 200
#   ? = 8
#   Bonds = 2
#   Indexes = 6
#   Currencies = 45
#   US(BATS) = 25, 517
#   bad markets = 91, 519
#
#  'emitents' = [(ticker, market, frame)]

# set of portfolios to iterate through looks like:

experiment_number = '0'

market = '1'
sample_number = 2
portfolio_size = 2
data_folder = ('C:/Users/TorchPochmak/Desktop/')
download_path = data_folder + 'input/finam_raw/'
mkpath(download_path)

print('Files will be in ' + download_path)


emitent_list = get_market_emitents(market)[1]

#SimpleQuery objects
portfolios = [
    SimpleQuery('1', 'LKOH', '13.02.2022', '13.02.2023', Period.hour, download_path), 
    SimpleQuery('1', 'SBER', '13.02.2022', '13.02.2023', Period.day, download_path)
]

print(f'Exporting data to files({len(portfolios)})...')
for p in portfolios:
    gather_finam_data(p)
print('Complete')
