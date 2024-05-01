from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum

import matplotlib
from matplotlib import pyplot as plt
import matplotlib.gridspec
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

    def get_min_y(self, prices: pd.DataFrame):
        pass
    def get_max_y(self, prices: pd.DataFrame):
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
        self.bar_bottom = fr.COL_NAMES.close
        self.bar_up = fr.COL_NAMES.open
        self.error_bar_bottom = fr.COL_NAMES.low
        self.error_bar_up = fr.COL_NAMES.high
        self.x_index = fr.COL_NAMES.date_to_plot
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Candle 
    
    def change_columns(self, bar_bottom: str = None, bar_up: str = None,
                        error_bar_up: str = None, error_bar_bottom: str = None,
                        x_index: str = None) -> None:
        if(bar_bottom != None):         self.bar_bottom = bar_bottom
        if(bar_up != None):             self.bar_up = bar_up
        if(error_bar_bottom != None):   self.error_bar_bottom = error_bar_bottom
        if(error_bar_up != None):       self.error_bar_up = error_bar_up
        if(x_index != None):            self.x_index = x_index
    
    def get_min_y(self, prices: pd.DataFrame):
        return min(prices[self.error_bar_bottom])
    def get_max_y(self, prices: pd.DataFrame):
        return max(prices[self.error_bar_up])

    def draw(self, prices: pd.DataFrame):
            #only draws a line, no clue about scaling, titles and axes stuff...
            col1 = self.color_up
            col2 = self.color_down
            colors = [col1 if prices[self.bar_bottom][x] >= prices[self.bar_up][x] else col2 for x in range(len(prices))]
            plt.bar (prices[self.x_index], prices[self.error_bar_up] - prices[self.error_bar_bottom], 
                    self.width_min_max, bottom=prices[self.error_bar_bottom], color=colors, edgecolor=(0,0,0,0))
            plt.bar (prices[self.x_index], prices[self.bar_up] - prices[self.bar_bottom], 
                    self.width_candle, bottom=prices[self.bar_bottom], color=colors, edgecolor=(0,0,0,0))

class Line(Shape):
    def __init__(self, format: str = '-', color: str = (1,1,1,0.5), 
                 linewidth: int = 1, frame_export_type: LineType = LineType.Close):
        self.format = format
        self.color = color
        self.linewidth = linewidth
        self.frame_export_type = frame_export_type
        self.column_x = fr.COL_NAMES.date_to_plot
        self.column_y = frame_export_type
    
    @property
    def get_shape_type(self) -> ShapeType:
        return ShapeType.Line
    
    def get_min_y(self, prices: pd.DataFrame):
        return min(prices[self.column_y])
    def get_max_y(self, prices: pd.DataFrame):
        return max(prices[self.column_y])

    def change_columns(self, new_x: str, new_y: str):
        self.column_x = new_x
        self.column_y = new_y

    def draw(self, prices: pd.DataFrame):
        plt.plot(prices[self.column_x], prices[self.column_y], 
                 self.format, linewidth=self.linewidth, color=self.color)

class Rect():
    def __init__(self, facecolor: str = (228/256, 223/256, 225/256, 0.3),
                 edgecolor: str = 'black'):
        self.facecolor = facecolor
        self.edgecolor = edgecolor
    
    def get_rect_absolute(self, frame:pd.DataFrame, 
                      min_y: int, max_y: int, 
                      min_x: int, max_x: int) -> plt.Rectangle:
        return plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, 
                             facecolor=self.facecolor, edgecolor=self.edgecolor)
    
    #region comments
    #?pivot has three types = {point_x, left, right}
    #?direction has two types = {left, right}
    #?percent use from 0 to 1
    #endregion
    def get_rect_percent(self, frame: pd.DataFrame, pivot: str, 
                     percent: float, direction: str, 
                     min_y: int, max_y: int, point_x: int = 0,) -> plt.Rectangle:
        total = len(frame)
        count_fact = int(percent * float(total))
        mn = -1 if direction == 'left' else 1
        right_point = 0
        left_point = 0
        if(pivot == 'point_x'):
            right_point = point_x
        elif(pivot == 'left'):
            right_point = len(frame) - 1
        elif(pivot == 'right'):
            right_point = 0
        left_point = right_point + (mn * count_fact)
        if(mn == -1): #then I should swap
            (right_point, left_point) = (left_point, right_point)
        #normalize
        if(right_point < 0):
            right_point = 0
        if(left_point > len(frame) - 1):
            left_point = len(frame) - 1

        return plt.Rectangle((right_point, min_y), left_point - right_point, max_y - min_y,
                             facecolor=self.facecolor, edgecolor=self.edgecolor)
        
    #? А вдруг забуду, что там нужен add_patch, пусть будет 
    def draw_rect(self, ax: plt.Axes, rect: plt.Rectangle):
        ax.add_patch(rect)


class MainFigure():
    def __init__(self, bg_color: str = '#090625', ticks_color: str = 'white', grid_color: str = 'gray',

                 size_x: int = 192, size_y: int = 108):
        #region INIT

        self.size_x = size_x
        self.size_y = size_y

        self.bg_color = bg_color
        self.grid_color = grid_color
        self.ticks_color = ticks_color
        #endregion
        self.fg = plt.figure(facecolor=bg_color, figsize=[(float(size_x))/10., (float(size_y))/10.])
        # plt.rcParams["figure.figsize"] = [(float(size_x))/10., (float(size_y))/10.]
        # plt.rcParams["figure.autolayout"] = True
        self.grid_spec = self.fg.add_gridspec(size_y, size_x)
        pass
    #TODO axis_y counter 

    #PRIVATE
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

    def draw_subplot(self,  shape: Shape, frame: pd.DataFrame, part_gs, count_x = 0, count_y = 0, 
                     x_min_int = 0, x_max_int = 0, y_min_int = 0, y_max_int = 0): 
        if(x_max_int == 0): x_max_int = len(frame)
        if(y_max_int == 0): y_max_int = len(frame)
        fg_ax = self.fg.add_subplot(part_gs)
        self.set_axes_theme(fg_ax)
        if(count_x > 0):
            plt.xticks(np.arange(x_min_int, x_max_int, x_max_int / count_x), fontsize = 7)
        if(count_y > 0):
            plt.yticks(np.arange(y_min_int, y_max_int, y_max_int / count_y), fontsize = 7)
        shape.draw(frame)
        return fg_ax

#INCLUSIVE
def get_gs_part(gs: matplotlib.gridspec.GridSpec,
                  begin_x: int = 0, end_x:int = 0,
                  begin_y: int = 0, end_y: int = 0):
    fig_width, fig_height = plt.gcf().get_size_inches()
    fig_width = int(fig_width*10)
    fig_height = int(fig_height*10)
    if(end_x == 0):
        end_x = int(fig_width - 1)
    if(end_y == 0):
        end_y = int(fig_height - 1)
    begin_x = int(begin_x)
    begin_y = int(begin_y)
    end_x = int(end_x)
    end_y = int(end_y)
    return gs[begin_y:end_y, begin_x:end_x]

#region grid_spec types 
#type 1
# -------------------------------------------------
# |                                               |
# |                                               |
# |                     0                         |
# |                                               |
# |                                               |
# |                                               |
# -------------------------------------------------

#type 2
# -------------------------------------------------  
# |                                               |  
# |                                               |  
# |                                               |  
# |                       0                       |  
# |                                               |  
# |                                               |  
# ------------------------------------------------- 

# -------------------------------------------------  
# |                         1...                  |  
# -------------------------------------------------  
# |                         count                 |  
# -------------------------------------------------  

#type 3
# -------------------------------------------------  -------------------------------------------------
# |                                               |  |                                               |
# |                                               |  |                                               |
# |                                               |  |                                               |
# |                      0                        |  |                       1                       |
# |                                               |  |                                               |
# |                                               |  |                                               |
# -------------------------------------------------  -------------------------------------------------

# -------------------------------------------------  -------------------------------------------------
# |                         2...                  |  |                                               |
# -------------------------------------------------  |                    len(self) - 1              |
# |                         count + 1             |  |                                               |
# -------------------------------------------------  -------------------------------------------------
#endregion

def grid_type1(mf: MainFigure) -> list:
    return [get_gs_part(mf.grid_spec)]

def grid_type2(mf: MainFigure, count: int, 
               interval_y: int = 2, center_y: int = -1) -> list:
    if(center_y == -1):
        center_y = int(mf.size_y * 2/3)
    res = []
    res.append(get_gs_part(mf.grid_spec,end_y=center_y))

    indicator_block_size_y = ((mf.size_y - 1) - (center_y + interval_y)) / count

    block_begin_y = center_y + interval_y
    for i in range(count):
        res.append(get_gs_part(mf.grid_spec,begin_y=block_begin_y, end_y=block_begin_y + indicator_block_size_y))
        block_begin_y += indicator_block_size_y
    return res

def grid_type3(mf: MainFigure, count: int, 
    interval_x: int = 8, interval_y: int = 2,
    center_x: int = -1, center_y: int = -1):

    if(center_x == -1):
            center_x = int(mf.size_x * 2/3)
    if(center_y == -1):
        center_y = int(mf.size_y * 2/3)
    
    res = []
    res.append(get_gs_part(mf.grid_spec, end_x=center_x, end_y=center_y))
    res.append(get_gs_part(mf.grid_spec,begin_x=center_x + interval_x, end_y=center_y))

    indicator_block_size_y = ((mf.size_y - 1) - (center_y + interval_y)) / count

    block_begin_y = center_y + interval_y
    for i in range(count):
        res.append(get_gs_part(mf.grid_spec,end_x=center_x, begin_y=block_begin_y, end_y=block_begin_y + indicator_block_size_y))
        block_begin_y += indicator_block_size_y
    res.append(get_gs_part(mf.grid_spec,begin_x=center_x + interval_x, begin_y=center_y + interval_y))
    return res

