import urllib
import string
import urllib.parse
import urllib.request
import string
from distutils.dir_util import mkpath

import finam_parser
from finam_parser.classes import *
import finam_parser.http_queries as queries
import finam_parser.export as export
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

emitent_list = queries.define_market_emitents(market)[1]

#SimpleQuery objects
portfolios = [
    SimpleQuery('1', 'LKOH', '13.02.2022', '13.02.2023', Period.hour, download_path), 
    SimpleQuery('1', 'SBER', '13.02.2022', '13.02.2023', Period.day, download_path)
]

print(f'Exporting data to files({len(portfolios)})...')
for p in portfolios:
    export.export_to_file(p)
print('Complete')
