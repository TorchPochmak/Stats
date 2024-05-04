from typing import Type
import matplotlib as mpl
import matplotlib.patches as patches
from matplotlib import pyplot as plt
import pandas as pd

from finam_parser import calc_inds
from finam_parser.query_classes import *
from finam_parser import tti
from finam_parser import moex_info

data = {
    'teams': ['Real Madrid', 'Barcelona', 'Villarreal', 'Sevilla'],
    'goals_scored': [23, 15, 28, 12]
}
fig, ax = plt.subplots()

ncols = 2
nrows = 4

ax.set_xlim(0, ncols)
ax.set_ylim(0, nrows)
ax.set_axis_off()

for y in range(0, nrows):
    ax.annotate(
        xy=(0.5,y),
        text=data['teams'][y],
        ha='center'
    )
    ax.annotate(
        xy=(1.5,y),
        text=data['goals_scored'][y],
        ha='center'
    )

ax.annotate(
    xy=(0.5, nrows),
    text='TEAM',
    weight='bold',
    ha='center'
)
ax.annotate(
    xy=(1.5, nrows),
    text='GOALS\nSCORED',
    weight='bold',
    ha='center'
)

plt.show()