import datetime as dt
import importlib
import numpy as np
import weakref
import logging
from .exceptions import *
from .constants import *

extra_modules = dict()


def extra_module(module_name):
    global extra_modules

    module = extra_modules.get(module_name)
    if module is None:
        module = importlib.import_module(module_name, package=__package__)
        extra_modules[module_name] = module

    return module


class TimeframeData:

    def __init__(self, data_dict):

        self.data = data_dict
        self.__read_only = False

        assert 'time' in data_dict.keys()

        if len(data_dict['time']) == 0:
            raise LTIExceptionEmptyBarData()

        self.first_bar_time = self.data['time'][0]
        self.end_bar_time = self.data['time'][-1]

    @staticmethod
    def get_copied_keys():
        return set()

    def __len__(self):
        return len(self.data['time'])

    def __getitem__(self, item):

        if type(item) != slice:
            raise NotImplementedError()

        if item == slice(None, None, None):
            return self

        if type(item.start) == np.datetime64 and type(item.stop) == np.datetime64 and item.step is None:
            return self.slice_by_datetime64(item.start, item.stop)

        if type(item.start) == np.datetime64 and item.stop is None and item.step is None:
            return self.slice_by_datetime64(item.start, item.stop)

        if type(item.start) == int and type(item.stop) == int and item.step is None:
            return self.slice_by_int(item.start, item.stop)

        if type(item.start) == int and item.stop is None and item.step is None:
            return self.slice_by_int(item.start, item.stop)

        if item.start is None and type(item.stop) == int and item.step is None:
            return self.slice_by_int(0, item.stop)

        if item.start is None and type(item.stop) == np.datetime64 and item.step is None:
            return self.slice_by_datetime64(None, item.stop)

        if type(item.start) == dt.datetime and type(item.stop) == dt.datetime and item.step is None:
            return self.slice_by_datetime(item.start, item.stop)

        if type(item.start) == dt.datetime and item.stop is None and item.step is None:
            return self.slice_by_datetime(item.start, item.stop)

        raise NotImplementedError()

    def __getattr__(self, item):
        return self.data[item]

    @property
    def allowed_nan(self):
        return self.data.get('allowed_nan', False)

    @property
    def is_live(self):
        return self.data.get('is_live', False)

    def __deepcopy__(self, memodict={}):
        return self.copy()

    def __add__(self, other):

        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = np.hstack((value, other.data[key]))
            else:
                if key not in ('symbol', 'name', 'timeframe', 'source'):
                    continue
                if value != other.data[key]:
                    raise ValueError(f'Data types do not match ({value} != {other.data[key]})')

                new_data[key] = value

        new_data['is_live'] = other.is_live

        return self.__class__(new_data)

    def str_period(self):
        str_live = ', real time' if self.data.get('is_live') else ''
        return f'date: {self.time[0].astype("datetime64[m]")} - {self.time[-1].astype("datetime64[m]")} ' \
               f'(length: {len(self.time)}{str_live}) '

    def str_values(self):
        return f'Values: {", ".join(self.data_keys())}'

    def check_series(self, allowed_nan=False):

        n_bars = len(self.time)

        for key, value in self.data.items():
            if type(value) == np.ndarray:
                if len(value) != n_bars:
                    raise LTIException('Bad data length')
                if not allowed_nan and np.isnan(value).any():
                    raise LTIException('Bad data value (nan)')
                if np.isinf(value).any():
                    raise LTIException('Bad data value (inf)')

    def copy(self):

        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = value.copy()
            else:
                new_data[key] = value

        return self.__class__(new_data)

    def index_from_time(self, time):
        if time is None: return None
        return int((time - self.first_bar_time).total_seconds() / self.timeframe.value)

    def index_from_time64(self, time):
        assert type(time) == np.datetime64 and time.dtype.name == TIME_TYPE
        if time is None: return None
        return int((time - self.first_bar_time).astype(np.int64) // self.timeframe.value)

    def slice_by_datetime(self, time_start, time_stop):

        i_start = self.index_from_time(time_start)
        i_stop = self.index_from_time(time_stop)

        if i_start == 0 and i_stop == len(self):
            return self

        if i_start > i_stop: raise ValueError
        if i_start < 0 or i_stop < 0: raise ValueError

        return self.slice_by_int(i_start, i_stop)

    def slice_by_datetime64(self, time_start, time_stop):

        i_start = 0 if time_start is None else self.index_from_time64(time_start)
        i_stop = self.index_from_time64(time_stop) if time_stop is not None else len(self) + 1

        if i_start == 0 and i_stop == len(self):
            return self

        if i_start > i_stop:
            raise ValueError
        if i_start < 0 or i_stop < 0:
            raise ValueError

        return self.slice_by_int(i_start, i_stop)

    def slice_by_int(self, i_start, i_stop):

        slice_copied_keys = self.get_copied_keys()
        new_data = {}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                new_data[key] = value[i_start : i_stop]
            elif key in slice_copied_keys:
                new_data[key] = value

        new_indicator_data = self.__class__(new_data)
        if self.read_only:
            new_indicator_data.read_only = True

        return new_indicator_data

    def __eq__(self, other):

        if len(self) != len(other):
            raise ValueError(f'The length of data does not match: {len(self)} != {len(other)}')

        verifiable_keys_not_series = {'timeframe'}
        for key, value in self.data.items():
            if type(value) == np.ndarray:
                other_value = other.data.get(key)
                if type(other_value) != np.ndarray:
                    return False
                is_nan = np.isnan(value)
                if (np.isnan(other_value) != is_nan).any():
                    return False
                if (other_value[~is_nan] != value[~is_nan]).any():
                    return False
            else:
                if key in verifiable_keys_not_series and other.data.get(key) != value:
                    return False

        return True

    def __read_only_set(self, flag_value):

        if self.__read_only == flag_value: return

        for key, data_value in self.data.items():
            if type(data_value) == np.ndarray:
                data_value.setflags(write=not flag_value)

        self.__read_only = flag_value

    def __read_only_get(self):
        return self.__read_only

    read_only = property(__read_only_get, __read_only_set)

    def data_keys(self):
        return [key for key, value in self.data.items() if type(value) == np.ndarray]

    def pandas(self):

        pandas = extra_module('pandas')

        pandas_series_names = set(self.data_keys())
        return pandas.DataFrame({key: value for key, value in self.data.items() if key in pandas_series_names})


class OHLCV_data(TimeframeData):

    def __init__(self, data_dict):
        super().__init__(data_dict)
        assert not {'timeframe', 'symbol', 'source'} - set(data_dict.keys())

    @staticmethod
    def get_copied_keys():
        return {'symbol', 'timeframe', 'source'}

    def __str__(self):

        info = [f'(OHLCV data) source: {self.source}, symbol: {self.symbol}, timeframe: {self.timeframe}', self.str_period()]

        if self.data.get('empty_bars_count') is not None:
            info.append(
                f'empty bars: count {self.empty_bars_count} ({self.empty_bars_fraction*100:.2f} %), max consecutive {self.empty_bars_consecutive}')

        info.append(self.str_values())

        return '\n'.join(info)

    def __repr__(self):
        return self.__str__()

    def fix_time(self, time_need):

        if set(self.time) - set(time_need):
            return False

        if (self.time != np.sort(self.time)).any():
            return False

        logging.warning(f'fixing time for {self.symbol}, timeframe {self.timeframe!s}, date {self.time[0].astype("datetime64[D]")}')
        n_bars = len(time_need)
        tf_time = time_need
        tf_open = np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE)
        tf_high = np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE)
        tf_low = np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE)
        tf_close = np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE)
        tf_volume = np.full(n_bars, 0, dtype=PRICE_TYPE)

        ix_time = np.searchsorted(tf_time, self.time)
        tf_open[ix_time] = self.open
        tf_high[ix_time] = self.high
        tf_low[ix_time] = self.low
        tf_close[ix_time] = self.close
        tf_volume[ix_time] = self.volume

        self.data.update({
            'time': tf_time,
            'open': tf_open,
            'high': tf_high,
            'low': tf_low,
            'close': tf_close,
            'volume': tf_volume
        })

        return True

    def is_entire(self):
        return not np.isnan(self.close).any()

    def is_empty(self):
        return np.isnan(self.close).all()

    def suppliment(self, bar_data2):

        ix_for_restore = self.close == 0
        self.open[ix_for_restore] = bar_data2.open[ix_for_restore]
        self.high[ix_for_restore] = bar_data2.high[ix_for_restore]
        self.low[ix_for_restore] = bar_data2.low[ix_for_restore]
        self.close[ix_for_restore] = bar_data2.close[ix_for_restore]
        self.volume[ix_for_restore] = bar_data2.volume[ix_for_restore]

    def get_skips(self):

        n_bars = len(self.time)
        if n_bars == 0:
            raise LTIExceptionEmptyBarData()

        bx_empty_bars = np.isnan(self.close)
        n_empty_bars = bx_empty_bars.sum()

        empty_bars_fraction = n_empty_bars / n_bars

        ix_change = np.flatnonzero(np.diff(bx_empty_bars) != 0) + 1
        intervals = np.hstack((ix_change, n_bars)) - np.hstack((0, ix_change))

        empty_bars_cons_length = intervals[0 if bx_empty_bars[0] else 1 :: 2]
        empty_bars_consecutive = empty_bars_cons_length.max() if len(empty_bars_cons_length) > 0 else 0

        return n_empty_bars, empty_bars_fraction, empty_bars_consecutive

    def restore_bar_data(self):

        n_bars = len(self.time)

        bx_empty_bars = np.isnan(self.close)
        n_empty_bars = bx_empty_bars.sum()

        if n_empty_bars == 0:
            return

        if n_empty_bars == n_bars:
            raise LTIExceptionQuotationDataNotFound(self.symbol, self.first_bar_time)

        if n_bars < 2:
            raise LTIExceptionQuotationDataNotFound(self.symbol, self.first_bar_time)

        ix_change = np.hstack((
            np.zeros(1, dtype=int),
            np.flatnonzero(np.diff(bx_empty_bars)) + 1,
            np.array(n_bars)
        ))

        for i, point in enumerate(ix_change[:-1]):

            if not np.isnan(self.close[point]):
                continue

            if point == 0:
                #price = self.open[ix_change[i + 1]]
                price = np.nan
            else:
                price = self.close[point - 1]

            point_end = ix_change[i + 1]
            self.open[point: point_end] = price
            self.high[point: point_end] = price
            self.low[point: point_end] = price
            self.close[point: point_end] = price

    def plot(self):
        return extra_module('.plotting').indicator_data_plot(self)

    def show(self):
        fig = self.plot()
        fig.show()


class OHLCV_day(OHLCV_data):

    def __init__(self, data_dict):
        super().__init__(data_dict)

        if 'is_incomplete_day' not in self.data.keys():
            self.data['is_incomplete_day'] = False

    def check_day_data(self, symbol, timeframe, day_date):

        self.check_series(True)

        error = None
        first_time = self.time[0]
        n_bars = self.expected_bars_count()

        if len(self.time) != n_bars:
            error = 'bad data length'

        if first_time != np.datetime64(day_date).astype(TIME_TYPE):
            error = 'bad first bar time'

        if (first_time + np.arange(n_bars) * timeframe.value != self.time).any():
            error = 'bad bars time'

        if (self.high < self.low).any():
            error = 'bad high/low values'

        if (self.open > self.high).any() or (self.open < self.low).any():
            error = 'bad open values'

        if (self.close > self.high).any() or (self.close < self.low).any():
            error = 'bad close values'

        if (self.volume < 0).any():
            error = 'bad volume values'

        nonzero_volume = self.volume > 0

        if (nonzero_volume & (self.open <= 0)).any():
            error = 'bad open values'

        if (nonzero_volume & (self.close <= 0)).any():
            error = 'bad close values'

        if error:
            raise LTIException(f'Timeframe data error: {error}')

    def expected_bars_count(self):

        if self.is_incomplete_day:
            return (self.time[-1] - self.time[0]).astype(np.int64) // self.timeframe.value + 1

        return TIME_UNITS_IN_ONE_DAY // self.timeframe.value

    def fix_errors(self, date):

        assert type(date) == np.datetime64 and date.dtype.name == 'datetime64[D]'

        if len(self.time) == 0:
            self.clear_day(date)
            return

        first_bar_time = np.datetime64(date, TIME_TYPE_UNIT)
        time_need = first_bar_time + np.arange(self.expected_bars_count()) * self.timeframe.value

        if (len(self.time) != len(time_need) or (self.time != time_need).any()) and not self.fix_time(time_need):
            self.clear_day(date)
            return

        bx_bad_bars = \
            (self.open <= 0) | \
            (self.close <= 0) | \
            (self.high < self.open) | \
            (self.high < self.close) | \
            (self.low > self.open) | \
            (self.low > self.close) | \
            (self.volume < 0)

        if bx_bad_bars.sum():
            self.data['volume'][bx_bad_bars] = 0
            for value_name in ('open', 'high', 'low', 'close'):
                self.data[value_name][bx_bad_bars] = UNKNOWN_PRICE

        self.first_bar_time = self.data['time'][0]
        self.end_bar_time = self.data['time'][-1]

    @staticmethod
    def empty_day(symbol, timeframe, source, date, is_incomplete_day):
        assert type(date) == np.datetime64 and date.dtype.name == 'datetime64[D]'
        n_bars = TIME_UNITS_IN_ONE_DAY // timeframe.value
        first_bar_time = np.datetime64(date, TIME_TYPE_UNIT)

        return OHLCV_day({
            'symbol': symbol,
            'timeframe': timeframe,
            'source': source,
            'is_incomplete_day': is_incomplete_day,
            'time': np.array([first_bar_time + np.timedelta64(i, TIME_TYPE_UNIT) * timeframe.value for i in range(n_bars)]),
            'open': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'high': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'low': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'close': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'volume': np.full(n_bars, 0, dtype=VOLUME_TYPE)
        })

    def clear_day(self, date):

        assert type(date) == np.datetime64 and date.dtype.name == 'datetime64[D]'
        n_bars = TIME_UNITS_IN_ONE_DAY // self.timeframe.value
        self.first_bar_time = np.datetime64(date, TIME_TYPE_UNIT)

        self.data.update({
            'time': np.array([self.first_bar_time + self.timeframe.value * i for i in range(n_bars)]),
            'open': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'high': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'low': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'close': np.full(n_bars, UNKNOWN_PRICE, dtype=PRICE_TYPE),
            'volume': np.full(n_bars, 0, dtype=VOLUME_TYPE)
        })

        self.end_bar_time = self.data['time'][-1]


class IndicatorData(TimeframeData):

    def __init__(self, data_dict):
        data_dict_keys = set(data_dict.keys())
        assert not {'timeframe', 'name', 'indicators'} - data_dict_keys

        if not isinstance(data_dict['indicators'], weakref.ReferenceType):
            indicators = data_dict['indicators']
            data_dict['indicators'] = weakref.ref(indicators)
            if 'source' not in data_dict_keys:
                data_dict['source'] = indicators.datasource_id
        else:
            assert 'source' in data_dict_keys

        super().__init__(data_dict)

        self.check_series(self.allowed_nan)

    @staticmethod
    def get_copied_keys():
        return {'symbol', 'timeframe', 'name', 'allowed_nan', 'source', 'indicators', 'charts', 'parameters'}

    def __str__(self):

        symbol = self.data.get('symbol')
        symbol_info = f'symbol: {symbol}'
        nan_info = 'allowed nan' if self.allowed_nan else 'not allowed nan'

        info = [f'(IndicatorData) source: {self.source}, name: {self.name}, {symbol_info}, '
                f'timeframe: {self.timeframe!s}, {nan_info}',
                self.str_period(),
                self.str_values()]

        return '\n'.join(info)

    def __repr__(self):
        return self.__str__()

    def source_ohlcv(self):

        indicators = self.indicators()
        if indicators is None:
            raise LTIException('Can\'t get the prices. The Indicators object has been destroyed.')

        return indicators.OHLCV(self.symbol, self.timeframe, self.first_bar_time, self.end_bar_time)

    def plot(self):
        return extra_module('.plotting').indicator_data_plot(self)

    def show(self):
        fig = self.plot()
        fig.show()

