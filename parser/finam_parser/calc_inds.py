import finam_parser.query_classes as queries
import finam_parser.pyplot_classes
import finam_parser.file_work as fw

from typing import Type

from distutils.dir_util import mkpath

import finam_parser.tti as tti

import numpy as np
import pandas as pd

def insert_ind_column(indicator_type: Type[tti.indicators._technical_indicator.TechnicalIndicator], frame: pd.DataFrame) -> pd.DataFrame: 
    frame_dates = frame.set_index(pd.DatetimeIndex(frame[fw.COL_NAMES.date_iso]))
    ind = indicator_type(input_data=frame_dates)
    res = ind.getTiData()
    merge_df = pd.merge(frame_dates, res, right_index=True, left_index=True)
    name = res.columns[0]
    merge_df[name] = merge_df[name].fillna(0)
    merge_df = merge_df.set_index(np.arange(len(merge_df)))
    return merge_df