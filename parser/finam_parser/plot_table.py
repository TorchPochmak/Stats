from typing import Type
import matplotlib as mpl
import matplotlib.patches as patches
from matplotlib import pyplot as plt
import pandas as pd

from . import calc_inds
from .query_classes import *
from . import tti
from . import moex_info

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
async def get_indicators_current(ticker_list: List[str], indicators: List[Type[tti.indicators._technical_indicator.TechnicalIndicator]],
                           end_date: str, period: Period, sort_by) -> pd.DataFrame:
    
    date_format = f"%Y-%m-%d"
    end_date = datetime.strptime(end_date, date_format)
    begin_date = end_date - timedelta(days=TIME_DELTA_DAYS[period])

    moex_query_list = []
    for ticker in ticker_list:
        moex_query_list.append(MoexQuery(ticker, begin_date.strftime(date_format), end_date.strftime(date_format), period, './DATA/'))
    frames = await query_classes.MoexQuery.multi_export_to_df(moex_query_list)
    results = []
    for frame in frames:
        for indicator in indicators:
            frame = calc_inds.insert_ind_column(indicator, frame)
        results.append(frame)
    last_rows = pd.concat([x.tail(1) for x in results])
    last_rows = last_rows.drop(columns=[COL_NAMES.date, COL_NAMES.open, COL_NAMES.high, COL_NAMES.low, COL_NAMES.time, COL_NAMES.date_to_plot, COL_NAMES.per, COL_NAMES.date_iso])
    last_rows = last_rows.sort_values(by=sort_by)
    return last_rows

def draw_table(ax: plt.Axes, df: pd.DataFrame, width: float = 1.2, height: float = 2.) -> None:
    df = float_round_series(df, df.columns[2:], 4)
    cnt = len(df.columns)
    positions = [i*width for i in range(cnt)]
    nrows = df.shape[0]
    ncols = df.shape[1]
    ax.set_xlim(0, ncols)
    ax.set_ylim(0, nrows)
    ax.set_axis_off()
    # Add table's main text
    for i in range(nrows):
        for j, column in enumerate(df.columns):
            if j == 0:
                ha = 'left'
            else:
                ha = 'center'
            text_label = f'{df[column].iloc[i]}'
            weight = 'normal'
            if(column in ['rsi', f'%k', f'%d']):
                if(float(df[column].iloc[i]) > 70):
                    color = 'green'
                elif(float(df[column].iloc[i]) < 30):
                    color = 'red'
                else:
                    color = 'white'
            else:
                color = 'white'
            ax.annotate(
                xy=(positions[j], i),
                text=text_label,
                ha=ha,
                va='center',
                weight=weight,
                color=color
            )

    # Add column names

    for index, c in enumerate(df.columns):
            if index == 0:
                ha = 'left'
            else:
                ha = 'center'
            ax.annotate(
                xy=(positions[index], nrows),
                text=df.columns[index],
                ha=ha,
                va='bottom',
                weight='bold',
                color='white'
            )
    
    # Add dividing lines
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1] + width / 2], 
            [nrows, nrows], lw=1.5, color='white', marker='', zorder=4)
    ax.plot([ax.get_xlim()[0], ax.get_xlim()[1] + width / 2],
            [-0.5, -0.5], lw=1.5, color='white', marker='', zorder=4)

    ax.plot([positions[len(positions) - 1] + width / 2, positions[len(positions) - 1] + width / 2], 
            [ax.get_ylim()[0], ax.get_ylim()[1]], lw=1.5, color='white', marker='', zorder=4)
    ax.plot([-width / 2, -width / 2], 
            [ax.get_ylim()[0] + width / 2, ax.get_ylim()[1] + width / 2], lw=1.5, color='white', marker='', zorder=4)
    
    for x in range(0, nrows):
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], 
                [x - 0.5, x - 0.5], lw=1, color='white', ls=':', zorder=3 , marker='')
    for i in range(0, ncols):
        ax.plot([positions[i] + width / 2, positions[i] + width / 2], 
                [ax.get_ylim()[0], ax.get_ylim()[1]], lw=1, color='white', ls=':', zorder=3 , marker='')
    plt.show()

def float_round_series(df, list, roun):
    print(df.head())
    for el in list:
        df[el] = df[el].apply(lambda x: round(x, roun))
    return df

async def main():
    
    pass
asyncio.run(main())