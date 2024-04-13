from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum

from matplotlib import pyplot as plt
from . import file_work as fr
import pandas as pd
import numpy as np

class ShapeType(IntEnum):
    Candle, Line = range(2)

class LineType(StrEnum):
    Open, Close, High, Low = fr.COL_NAMES.open, fr.COL_NAMES.close, fr.COL_NAMES.high, fr.COL_NAMES.low

class Shape(ABC):

    @abstractmethod
    def draw(self, frame: pd.DataFrame):
        pass
    
    @property
    @abstractmethod
    def get_shape_type(self) -> ShapeType:
        pass 

class Candle(Shape):
    def __init__(self, width_candle: int = 0.9, width_min_max: int = 0.1, 
                 color_up: str = (39/256,238/256,69/256,1), color_down: str = (238/256,39/256,69/256,1)) -> None:
        self.width_candle = width_candle
        self.width_min_max = width_min_max
        self.color_up  = color_up
        self.color_down = color_down
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Candle 
    
    def draw(self, prices: pd.DataFrame):
            #only draws a line, no clue about scaling, titles and axes stuff...
            col1 = self.color_up
            col2 = self.color_down
            colors = [col1 if prices[fr.COL_NAMES.close][x] >= prices[fr.COL_NAMES.open][x] else col2 for x in range(len(prices))]
            plt.bar (prices[fr.COL_NAMES.date_iso], prices[fr.COL_NAMES.high] - prices[fr.COL_NAMES.low], 
                    self.width_min_max, bottom=prices[fr.COL_NAMES.low], color=colors, edgecolor=(0,0,0,0))
            plt.bar (prices[fr.COL_NAMES.date_iso], prices[fr.COL_NAMES.open] - prices[fr.COL_NAMES.close], 
                    self.width_candle, bottom=prices[fr.COL_NAMES.close], color=colors, edgecolor=(0,0,0,0))

class Line(Shape):
    def __init__(self, format: str = '-', color: str = (1,1,1,0.5), 
                 linewidth: int = 1, frame_export_type: LineType = LineType.Close):
        self.format = format
        self.color = color
        self.linewidth = linewidth
        self.frame_export_type = frame_export_type
    
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Line
    
    def draw(self, prices: pd.DataFrame):
        plt.plot(prices[fr.COL_NAMES.date_iso], prices[self.frame_export_type], 
                 self.format, linewidth=self.linewidth, color=self.color)
    def draw_xy(self, x, y):
        plt.plot(x, y, self.format, linewidth=self.linewidth, color=self.color)



def create_figure(size_x: int, size_y: int, bg_color):
    
    pass

class MainFigure():
    def __init__(self, bg_color: str = '#090625', ticks_color: str = 'white', grid_color: str = 'gray',
                 interval_x: int = 8, interval_y: int = 2,
                 center_x: int = -1, center_y: int = -1,
                 size_x: int = 192, size_y: int = 108):
        if(center_x == -1):
            center_x = int(size_x) * 2/3
        if(center_y == -1):
            center_y = int(size_y) * 2/3
        #region INIT
        self.center_x = center_x
        self.center_y = center_y

        self.interval_x = interval_x
        self.interval_y = interval_y

        self.size_x = size_x
        self.size_y = size_y

        self.bg_color = bg_color
        self.grid_color = grid_color
        self.ticks_color = ticks_color
        #endregion
        plt.rcParams["figure.figsize"] = [self.size_x * 10, self.size_y * 10]
        plt.rcParams["figure.autolayout"] = True
    
        fg = plt.figure(facecolor=bg_color)
        self.fg = fg
        self.grid_spec = fg.add_gridspec(size_x, size_y)
    #TODO axis_y counter 
    def create_plot(self, count_ticks_x: int, count_ticks_y: int = 0) -> None:
        
        pass

    def set_xtick(freq: int, frame: pd.DataFrame, fontsize: int = 7):
        plt.xticks(np.arange(0, len(frame), len(frame) / freq), fontsize = fontsize)

    def set_ytick(freq: int, frame: pd.DataFrame, fontsize: int = 7):
        plt.yticks(np.arange(0, len(frame), len(frame) / freq), fontsize = fontsize)

    def set_axes_theme(self, ax: plt.Axes): #mg is MainFigure

        ax.tick_params(axis='x', colors=self.ticks_color)
        ax.tick_params(axis='y', colors=self.ticks_color)

        ax.set_facecolor(self.bg_color)

        ax.grid(which='major', linestyle='--', color=self.grid_color,linewidth=0.5)
        ax.grid(which='minor', linestyle='--', color=self.grid_color, linewidth=0.2)

        ax.spines['bottom'].set_color(self.ticks_color)
        ax.spines['top'].set_color(self.ticks_color)
        ax.spines['left'].set_color(self.ticks_color)
        ax.spines['right'].set_color(self.ticks_color)

        ax.set_axisbelow(True)

    #?grid_spec is only for MainFigure, use mg.gs[a:b, c:d]
    #? for frame: typical, frame.index -> 0,1,2,3...............

    def draw_subplot(self, part_gs, count_x, count_y, shape: Shape, frame: pd.DataFrame): 
        fg_ax = self.fg.add_subplot(part_gs)
        self.set_axes_theme(fg_ax)
        self.set_xtick(count_x, frame)
        self.set_ytick(count_y, frame)
        shape.draw(frame)
        return fg_ax



# shape_candle = finam_plot.Candle()
# shape_line = finam_plot.Line()
# #----------------------------------------------------------------------------------------

# fg_ax1 = fg.add_subplot(gs[0:center_x, 0:center_y])
# finam_plot.set_axes_theme(fg_ax1)
# finam_plot.set_xtick_freq(16, prices_main)
# shape_candle.draw(prices_main)
# #-------------------------------------------------------------------------------

# fg_ax2 = fg.add_subplot(gs[center_x + interval_x:, center_y + interval_y:])
# finam_plot.set_axes_theme(fg_ax2)
# finam_plot.set_xtick_freq(5, prices_second)

# shape_candle.draw(prices_second)

# mn = min(prices_second[fw.COL_NAMES.low])
# mx = max(prices_second[fw.COL_NAMES.high])

# mask = [prices_second[fw.COL_NAMES.date_iso][x] > prices_main[fw.COL_NAMES.date_iso][0] for x in range(0, len(prices_second))]
# df = prices_second.loc[mask]
# fg_ax2.bar(df[fw.COL_NAMES.date_iso], mx, bottom=mn, color=(1,1,1,0.3), width=1)
# #-----------------------------------------------------------------------------------
# fg_ax3 = fg.add_subplot(gs[center_x+interval_x:, 0:center_y])
# finam_plot.set_axes_theme(fg_ax3)
# finam_plot.set_xtick_freq(16, prices_main)

# rsi = RelativeStrengthIndex(input_data=prices_main)
# merge_df = pd.merge(prices_main, rsi.getTiData(), right_index=True, left_index=True)
# merge_df['rsi'] = merge_df['rsi'].fillna(0)
# shape_line.draw_xy(merge_df[fw.COL_NAMES.date_iso], merge_df['rsi'])

# #------------------------------------------------------------------------------------
# fg_ax4 = fg.add_subplot(gs[0:center_x, center_y+interval_y: ])
# finam_plot.set_axes_theme(fg_ax4)
# plt.title('DAMN', fontsize=17, position=(0.5, 0.5), color='w')
