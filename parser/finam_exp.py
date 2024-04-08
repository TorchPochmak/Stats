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

tm_to_code = {}
markts = {}
emitents = {}

# Ограничения
# Объем запрашиваемых данных в рамках одного запроса:

#     Сделки - не более чем за 1 день
#     Внутридневные свечи - не более чем за 4 месяца
#     Дневные свечи и выше - не более чем за 5 лет

class Period(Enum):
    tick, min1, min5, min10, min15, min30, hour, day, week, month = range(1, 11)
class SimpleQuery():
#private:
    date_begin = ''
    date_end = ''
    #queries = [[market, code, date_begin1, date_end1, period, path], [market, code, date_begin2, date_end2, period, path]]
    queries = []
    def __init__(self, market, code, date_begin, date_end, period, path):
        dates = self.split_date_interval(date_begin, date_end, period)
        for i in range(len(dates)):
            self.queries.append([market, code, dates[i][0], dates[i][1], period, path])
#public:    
    def split_date_interval(start_date_str, end_date_str, period):
        interval_delta_days = 0
        if(period < Period.day):
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
    print(url)
    response = urllib.request.urlopen(url)
    content = str(response.read(), 'utf-8')
    return content.split('\n')

def gather_finam_data(emitents, from_str, to_str,
                      period = Period.day, path = './'):
    """Creates file with aggregated data from finam.ru for given parameters.

    Is able to bypass finam data size restriction by splitting query into
    several requests.

    Args:
        emitents : list of tuples (ticker : market)
        from_str : start date string in "dd.mm.yyyy" format
        to_str   : end date string in "dd.mm.yyyy" format
        period   : granularity of time series represented as Period Enum
    """
    result = []

    from_date = dt.strptime(from_str, "%d.%m.%y").date()
    to_date = dt.strptime(to_str, "%d.%m.%y").date()

    for i in range(len(emitents)):
        ticker = emitents[i][0]
        market = emitents[i][1]
        code = define_emitent_code(ticker, market)
        print(ticker, market, code)

        from_var = from_date
        to_var = to_date

        j = 0
        while(to_var >= from_var):
            print(from_var, min(from_var+td(days=364), to_var))
            data = get_fin_data(market, code, ticker, from_var,
                                min(from_var+td(days=364), to_var), period)
            from_var += td(days=365)
            result += data[(0 if (i or j) == 0 else 1):-1]
            j += 1
            time.sleep(1)

    em_str = '_'.join([em[0] for em in emitents])
    filename = 'stocks_{}_{}_{}'.format(em_str,
                                        from_str,
                                        to_str).replace('.', '')
    with open(path + filename + '.txt', 'w') as f:
        for item in result:
            f.write("{}\n".format(item))

def load_finam_vars():

    #TODO how to create unique cookie every timee I don't know
    cookie = 'spid=1698239062149_ffc1617857dd0549111a40a8d63c8291_kf7exqt56wn2q8uv; spsc=1712563438650_1564cd545e335ac229a286b39e0025ae_2dc4c47e5beb4aae25be080fa9d16c8093e7e989cef732b63b8bada59af3d7da; _ga_P7V3S6WS35=GS1.1.1712519349.11.1.1712526142.0.0.0; _ga=GA1.1.528312804.1698239061; tmr_lvid=bb28d604036d7214ae3b51446d81667c; tmr_lvidTS=1698239061852; offfyUserId=1698239061531-0157-179f78c2c40d; _ym_uid=1706124916676408047; _ym_d=1706124916; _gcl_au=1.1.1816192709.1706124916; _pk_ref.19.2ab2=%5B%22%22%2C%22%22%2C1712519351%2C%22https%3A%2F%2Fsmart-lab.ru%2F%22%5D; _pk_id.19.2ab2=08aa2af52c1a1b20.1712319279.; domain_sid=2LImXvAY5zxiGEr5nscH3%3A1712510666885; _ym_isad=2; tmr_detect=0%7C1712526156023; Reset=Reset; segmentsUserId=468b6795-8441-8c62-d056-4d4bb7472f24; ClientTimezoneOffset=180; NewsBeltSection=1; segmentsData=puid1=; adtech_uid=e06b9e16-bd3d-486e-93e8-4267233daa17%3Afinam.ru; top100_id=t1.35046.835818717.1712521345285; t3_sid_35046=s1.287532151.1712521345285.1712521345285.1.1; __utma=1.528312804.1698239061.1712521345.1712521345.1; __utmz=1.1712521345.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); last_visit=1712510545546%3A%3A1712521345546; srv_id=ae728f13e40892822b53df39694f66af; fb%5Faccess%5Ftoken=; ASPSESSIONIDSSBSCDCQ=EGJHPDKAIJBOILFLPDAOLBLA; __utmc=1';

    url = 'https://www.finam.ru/cache/icharts/icharts.js'
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

    response = urllib.request.urlopen(req)
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
# portfolios = [
#     {'emitents' : [('LKOH', '1'), ('SIBN', '1')]}, 
#     {'emitents' : [('AFLT', '1'), ('BANE', '1')]}
# ]


experiment_number = '0'

market = '1'
sample_number = 2
portfolio_size = 2
data_folder = ('C:/Users/TorchPochmak/Desktop/')
download_path = data_folder + 'input/finam_raw/'
mkpath(download_path)
mkpath(data_folder + 'results/plot_data/')

print('result files will be in ' + download_path)


emitent_list = get_market_emitents(market)[1]

#SimpleQuery objects

portfolios = [
    {'emitents' : [[('LKOH', '1'), ('SIBN', '1')]]}, 
    {'emitents' : [('AFLT', '1'), ('BANE', '1')]}    
]

portfolios2 = [
    {'emitents': [SimpleQuery('1', 'LKOH', '13.02.2022', '13.02.2023', Period.hour, download_path), SimpleQuery]}
]
print(emitent_list)
for i in range(sample_number):
    random_emitent_sample = random.sample(emitent_list, portfolio_size)
    random_emitents = [(ticker, market) for ticker in random_emitent_sample]
    random_portfolio = {'emitents' : random_emitents}
    portfolios.append(random_portfolio)

for p in portfolios:
    print(p['emitents'])
    gather_finam_data(period = Period.day,
                                   from_str = '08.01.18',
                                   to_str = '08.07.18',
                                   path = download_path,
                                   **p)
