"""MACD(period_short=, period_long=, period_signal=, ma_type='ema', ma_type_signal='sma', value='close')
Moving Average Convergence/Divergence."""
from ..indicator_data import IndicatorData
from ..move_average import ma_calculate, MA_Type


def get_indicator_out(indicators, symbol, timeframe, out_for_grow, period_short, period_long, period_signal,
                      ma_type='ema', ma_type_signal='sma',
                      value='close'):

    ohlcv = indicators.OHLCV.full_data(symbol, timeframe)
    source_values = ohlcv.data[value]

    ma_type_enum = MA_Type.cast(ma_type)
    ema_short = ma_calculate(source_values, period_short, ma_type_enum)
    ema_long = ma_calculate(source_values, period_long, ma_type_enum)

    macd = ema_short - ema_long

    signal = ma_calculate(macd, period_signal, MA_Type.cast(ma_type_signal))

    macd_hist = macd - signal

    return IndicatorData({
        'indicators': indicators,
        'parameters': {'period_short': period_short, 'period_long': period_long, 'period_signal': period_signal,
                      'ma_type': ma_type, 'ma_type_signal': ma_type_signal,
                      'value': value},
        'name': 'MACD',
        'symbol': symbol,
        'timeframe': timeframe,
        'time': ohlcv.time,
        'macd': macd,
        'signal': signal,
        'hist': macd_hist,
        'charts': (None, 'macd, signal, hist:hist'),
        'allowed_nan': True
    })


