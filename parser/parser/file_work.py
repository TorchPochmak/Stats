import numpy as np
import scipy as sp
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as sps
import pandas as pd
import ipywidgets as widgets
import os.path
from .query_classes import *
from .http_queries import *

from enum import StrEnum

#!DEPRECATED
#csv file -> pd.DataFrame
def import_from_file(filepath: str, sep: str = ',') -> pd.DataFrame:
    if(os.path.isfile(filepath) == False):
        return pd.DataFrame([])
    frame = pd.read_csv(filepath, sep=sep, dtype={'<TICKER>': str, '<PER>': str, '<DATE>': str, '<TIME>': str,
                                                  '"<OPEN>"': float, '<HIGH>': float, '<LOW>': float, '<CLOSE>': float, '<VOL>': float})
    
    frame.insert(len(frame.columns), COL_NAMES.date_iso, None)
    frame.insert(len(frame.columns), COL_NAMES.date_to_plot, None)
    frame.columns = COLUMNS
    frame = correct_date_iso_series(frame)
    frame[COL_NAMES.date_to_plot] = frame[COL_NAMES.date_iso].dt.strftime(f"%y-%m-%d\n%H-%m")
    return frame
#FinamQuery writes into csv file
