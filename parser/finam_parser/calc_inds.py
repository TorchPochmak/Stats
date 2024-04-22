import finam_parser.query_classes as queries
import finam_parser.plot_classes
import finam_parser.file_work as fw

from typing import Type

from distutils.dir_util import mkpath

import finam_parser.tti as tti

import numpy as np
import pandas as pd
#(center_y - 2ind_g )/ (count)

mf = finam_parser.plot_classes.MainFigure()

market = '1'
download_path = './DATA/'
mkpath(download_path)
print('Files will be in ' + download_path)


# portfolios = [
#     # FinamQuery('1', 'NLMK', '13.02.2023', '13.02.2023', Period.tick, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '13.02.2023', Period.min1, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min5, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min10, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min15, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.min30, download_path), 
#     # FinamQuery('1', 'NLMK', '13.02.2023', '14.02.2023', Period.hour, download_path), 
#     #FinamQuery('1', 'NLMK', '13.02.2022', '13.02.2023', Period.day, download_path), 
#     queries.FinamQuery('1', 'GAZP', '15.03.2023', '15.05.2023', queries.Period.hour4, download_path),
#     queries.FinamQuery('1', 'GAZP', '15.05.2022', '15.05.2023', queries.Period.day, download_path),
#     #FinamQuery('1', 'TCSG', '13.02.2022', '13.02.2023', Period.month, download_path),
# ]



def insert_ind_column(indicator_type: Type[tti.indicators._technical_indicator.TechnicalIndicator], frame: pd.DataFrame) -> pd.DataFrame: 
    frame_dates = frame.set_index(pd.DatetimeIndex(frame[fw.COL_NAMES.date_iso]))
    ind = indicator_type(input_data=frame_dates)
    res = ind.getTiData()
    merge_df = pd.merge(frame_dates, res, right_index=True, left_index=True)
    name = res.columns[0]
    merge_df[name] = merge_df[name].fillna(0)
    merge_df = merge_df.set_index(np.arange(len(merge_df)))
    return merge_df