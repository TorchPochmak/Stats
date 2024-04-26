from enum import IntEnum

#Энергетические и минеральные ресурсы
ENERGY_MINERALS = ['ROSN', 'LKOH', 'GAZP', 'NVTK', 'SIBN', 'SNGS', 'TATN', 'BANE', 'RASP',
              'VJGZ', 'RNFT', 'MFGS', 'UKUZ', 'BLNG', 'JNOS', 'KRKN', 'CHGZ']
#Несырьевые полезные ископаемые
NON_ENERGY_MINERALS = ['GMKN', 'PLZL', 'CHMF', 'NLMK', 'RUAL', 'MAGN', 'ALRS', 'VSMO',
                       'ENPG', 'TRMK', 'POLY', 'MLTR', 'SELG', 'ROLO', 'AMEZ', 'CHMK',
                       'LNZL', 'BRZL', 'URKZ', 'KOGK', 'IGST', 'UNKL']
#Финансы
FINANCE = ['SBER', 'VTBR', 'TCSG', 'MOEX', 'CBOM', 'SMLT', 'ROSB', 'POSI', 'SFIN', 'BSPB', 
           'RGSS', 'LSRG', 'USBN', 'AVAN', 'INGR', 'RENI', 'WTCM', 'SPBE', 'PRMB',
           'RDRB', 'ARSA', 'KUZB']
#Коммунальные услуги
UTILITIES = ['IRAO', 'HYDR', 'FEES', 'LSNG', 'MSNG', 'UPRO', 'KUBE', 'YAKG', 'MRKS',
             'MSRS', 'OGKB', 'DVEC', 'MRKK', 'TNSE', 'RTSB', 'KCHE', 'MRKU', 'MRKP',
             'VRSB', 'TGKA', 'MRKC', 'NNSB', 'ELFV', 'YRSB', 'LPSB', 'TGKN', 'TGKB', 
             'SAGO', 'KRSB', 'MRKY', 'MRKV', 'PMSB', 'MISB', 'KBSB', 'MRKZ', 'RZSB',
             'YKEN', 'KGKC', 'VGSB', 'SLEN', 'RTGZ', 'TASB', 'SARE', 'TORS', 'STSB', 
             'MAGE', 'KLSB', 'ASSB', 'MRSB']
#Обрабатывающая промышленность
PROCESS_INDUSTRIES = ['PHOR', 'AKRN', 'GCHE', 'NKNC', 'KAZT', 'AGRO', 'AQUA', 'SGZH', 'VLHZ']
#Электронные технологии
ELECTRONIC_TECHNOLOGY = ['IRKT', 'UNAC', 'RKKE', 'EELT', 'NAUK', 'LVHK']
#Технологии
TECHNOLOGY_SERVICES = ['YNDX', 'VKCO', 'QIWI', 'RBCM', 'CIAN', 'HHRU']
#Связь
COMMUNICATIONS = ['MTSS', 'RTKM', 'AFKS', 'MGTS', 'VEON-RX', 'TTLK', 'NSVZ', 'CNTL']
#Транспорт
TRANSPORTATION = ['FLOT', 'FESH', 'NMTP', 'AFLT', 'UTAR', 'GLTR', 'NKHP', 'GTRK', 'TUZA']
#Розничная торговля
RETAIL_TRADE = ['MGNT', 'FIXP', 'LENT', 'APTK', 'DSKY', 'OKEY', 'OZON'] #'FIVE', but inactive right now
#потребительские товары длительного пользования
CONSUMER_DURABLES = ['PIKK', 'SVAV', 'PAZA', 'ZILL', 'NFAZ', 'DZRD', 'ETLN']
#Промышленное производство
PRODUCER_MANUFACTURING = ['KZOS', 'UWGN', 'KMAZ', 'VSYD', 'GAZA', 'CHKZ', 'ZVEZ', 'KMEZ', 'PRFN', 'NKSH']
#Потребительские товары недлительного пользования
CONSUMER_NON_DURABLES = ['BELU', 'ABRD', 'KROT']
#Здравоохранение
HEALTH_SERVICES = ['GEMC', 'ABIO', 'MDMG']
#Производственно-технические услуги
INDUSTRIAL_SERVICES = ['MSTT']
#Дистрибуция
DISTRIBUTION_SERVICES = ['MVID']
#Рзаное
MISCELLANEOUS = ['RUSI', 'AMRH', 'ESGR', 'SBRS', 'GOLD', 'RCMB', 'TRUR', 'INFL', 'SUGB', 'AKMB',
                 'SBRB', 'EQMX', 'SBRI', 'SBWS', 'LQDT', 'TMOS', 'RSHU']
#Медицинские технологии
HEALTH_TECHNOLOGY = ['GEMA', 'LIFE', 'DIOD']
#Потребительские услуги
CONSUMER_SERVICES = ['ROST']
#Коммерческие услуги
COMMERCIAL_SERVICES = ['SVET']

STOCKS = [ENERGY_MINERALS, NON_ENERGY_MINERALS, FINANCE, UTILITIES, PROCESS_INDUSTRIES, ELECTRONIC_TECHNOLOGY, TECHNOLOGY_SERVICES, COMMUNICATIONS, TRANSPORTATION,
          RETAIL_TRADE, CONSUMER_DURABLES, PRODUCER_MANUFACTURING, CONSUMER_NON_DURABLES, HEALTH_SERVICES, INDUSTRIAL_SERVICES, DISTRIBUTION_SERVICES, MISCELLANEOUS, HEALTH_TECHNOLOGY,
          CONSUMER_SERVICES, COMMERCIAL_SERVICES]

class SectorEnum(IntEnum):
    ENERGY_MINERALS, NON_ENERGY_MINERALS, FINANCE, UTILITIES, PROCESS_INDUSTRIES, ELECTRONIC_TECHNOLOGY, TECHNOLOGY_SERVICES, COMMUNICATIONS, TRANSPORTATION, RETAIL_TRADE, CONSUMER_DURABLES, PRODUCER_MANUFACTURING, CONSUMER_NON_DURABLES, HEALTH_SERVICES, INDUSTRIAL_SERVICES, DISTRIBUTION_SERVICES, MISCELLANEOUS, HEALTH_TECHNOLOGY, CONSUMER_SERVICES, COMMERCIAL_SERVICES = range(20)
