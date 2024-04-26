from typing import Type
import matplotlib as mpl
import matplotlib.patches as patches
from matplotlib import pyplot as plt
import pandas as pd

from finam_parser import calc_inds
from finam_parser.query_classes import *
from finam_parser import tti
from finam_parser import moex_info

TIME_DELTA_DAYS = {
    Period.tick :   1,#!didn't analyze lol
    Period.min1 :   1, 
    Period.min5 :   1,
    Period.min10 :  1, 
    Period.min15 :  1,
    Period.min30 :  10,
    Period.hour :   10,
    Period.hour4 :  20, 
    Period.day :    120, 
    Period.week :   720, 
    Period.month:   2800,
}
def get_indicators_current(ticker_list: List[str], indicators: List[Type[tti.indicators._technical_indicator.TechnicalIndicator]],
                           end_date: str, period: Period, sort_by) -> pd.DataFrame:
    
    date_format = f"%Y-%m-%d"
    end_date = datetime.strptime(end_date, date_format)
    begin_date = end_date - timedelta(days=TIME_DELTA_DAYS[period])

    moex_query_list = []
    for ticker in ticker_list:
        moex_query_list.append(MoexQuery(ticker, begin_date.strftime(date_format), end_date.strftime(date_format), period, './DATA/'))
    frames = query_classes.MoexQuery.multi_export_to_df(moex_query_list)
    results = []
    for frame in frames:
        for indicator in indicators:
            frame = calc_inds.insert_ind_column(indicator, frame)
        results.append(frame)
    last_rows = pd.concat([x.tail(1) for x in results])
    last_rows = last_rows.drop(columns=[COL_NAMES.date, COL_NAMES.open, COL_NAMES.high, COL_NAMES.low, COL_NAMES.time, COL_NAMES.date_to_plot, COL_NAMES.per, COL_NAMES.date_iso])
    last_rows = last_rows.sort_values(by=sort_by)
    return last_rows


res = get_indicators_current(moex_info.FINANCE, [tti.indicators.StochasticOscillator, tti.indicators.RelativeStrengthIndex], 
                             '2024-04-26', period=Period.hour, sort_by='rsi')

fig = plt.figure(figsize=(7,10), dpi=300)
ax = plt.subplot()

ax.set_xlim(0, len(res.axes[1])*10 + 1)
ax.set_ylim(0, len(res.axes[0])*10)

i = 0.25
positions = [x*5+i for x in range(len(res.axes[1]))]
columns = res.axes[1]

# Add table's main text
for i in range(len(res.axes[0])):
    for j, column in enumerate(columns):
        if j == 0:
            ha = 'left'
        else:
            ha = 'center'
        ax.annotate(
            xy=(positions[j], i),
            text=res[column].iloc[i],
            ha=ha,
            va='center'
        )

# Add column names
column_names = res.axes[1]
for index, c in enumerate(column_names):
        if index == 0:
            ha = 'left'
        else:
            ha = 'center'
        ax.annotate(
            xy=(positions[index], len(res.axes[0])),
            text=column_names[index],
            ha=ha,
            va='bottom',
            weight='bold'
        )
plt.show()
ax.set_axis_off()
print(res)