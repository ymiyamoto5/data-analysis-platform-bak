"""
 ==================================
  data_accessor.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

# import json
# import os
# from textwrap import dedent as d
import pandas as pd

# import numpy as np
# from datetime import date, datetime,timedelta
# from fft_tools import *
# from plotly_utils import *
# import plotly.graph_objs as go
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_bootstrap_components as dbc
# import numpy as np

import os, sys

sys.path.append(os.path.join(os.getcwd(), "../../"))
# from backend.common import common
# from backend.common.common_logger import logger
from backend.elastic_manager.elastic_manager import ElasticManager

# from backend.data_reader.data_reader import DataReader
# from backend.analyzer.analyzer import Analyzer


class DataAccessor:
    def __init__(self):
        # 抽出済み特徴量の "名前=>値(index)" となるdictionary。
        from pathlib import Path

        p = Path("/Users/hao/data/ADDQ/20211004ブレークスルー/")
        self.flist = list(sorted(p.glob("*.CSV")))

    def get_shot_list(self):
        return self.flist

    def get_shot(self, num):
        return self.flist[num]

    def read_logger(self, f):
        # 9行目以降のメタ情報を読み込むために一旦8行目以降を読み込み
        df = pd.read_csv(f, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7])
        unit = df.iloc[4]
        offset = df.iloc[3]
        calibration = df.iloc[2]
        v_range = df.iloc[1]
        channel = df.iloc[0]
        # 改めて8行目をヘッダにして読み込む
        # df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1).set_index('time')
        # floatのindex作っちゃダメ!!!
        df = pd.read_csv(f, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],).rename({"CH名称": "time"}, axis=1)
        try:
            df["プレス荷重shift"] = df["プレス荷重"].shift(-640)
            df["dF/dt"] = df["プレス荷重shift"].diff()
            df["F*dF/dt"] = df["プレス荷重shift"] * df["dF/dt"]
            if "加速度左右_X_左+" in df.columns:
                df = df.rename({"加速度左右_X_左+": "加速度左右_X_左+500G"}, axis=1)
            if "加速度上下_Y_下+" in df.columns:
                df = df.rename({"加速度上下_Y_下+": "加速度上下_Y_下+500G"}, axis=1)
            if "加速度前後_Z_前+" in df.columns:
                df = df.rename({"加速度前後_Z_前+": "加速度前後_Z_前+500G"}, axis=1)
        except KeyError:
            print("プレス荷重　無し")

        # return df,unit,offset,calibration,v_range,channel
        return df


class DataAccessorELS:
    def __init__(self):
        index_df = ElasticManager.show_indices(index="shots-*-data")
        print(index_df)
        index_df["docs.count"] = index_df["docs.count"].astype(int)
        index_df = index_df[index_df["docs.count"] > 0]

        # 抽出済み特徴量の "名前=>値(index)" となるdictionary。
        # dr = DataReader()
        # p = Path('/Users/hao/data/ADDQ/20211004ブレークスルー/')
        # self.flist = list(sorted(p.glob('*.CSV')))

    def get_shot_list(self):
        return self.flist

    def get_shot(self, num):
        return self.flist[num]

    def read_logger(self, f):
        # 9行目以降のメタ情報を読み込むために一旦8行目以降を読み込み
        df = pd.read_csv(f, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7])
        unit = df.iloc[4]
        offset = df.iloc[3]
        calibration = df.iloc[2]
        v_range = df.iloc[1]
        channel = df.iloc[0]
        # 改めて8行目をヘッダにして読み込む
        # df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1).set_index('time')
        # floatのindex作っちゃダメ!!!
        df = pd.read_csv(f, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],).rename({"CH名称": "time"}, axis=1)
        try:
            df["プレス荷重shift"] = df["プレス荷重"].shift(-640)
            df["dF/dt"] = df["プレス荷重shift"].diff()
            df["F*dF/dt"] = df["プレス荷重shift"] * df["dF/dt"]
            if "加速度左右_X_左+" in df.columns:
                df = df.rename({"加速度左右_X_左+": "加速度左右_X_左+500G"}, axis=1)
            if "加速度上下_Y_下+" in df.columns:
                df = df.rename({"加速度上下_Y_下+": "加速度上下_Y_下+500G"}, axis=1)
            if "加速度前後_Z_前+" in df.columns:
                df = df.rename({"加速度前後_Z_前+": "加速度前後_Z_前+500G"}, axis=1)
        except KeyError:
            print("プレス荷重　無し")

        # return df,unit,offset,calibration,v_range,channel
        return df


if __name__ == "__main__":
    da = DataAccessorELS()

#    da = DataAccessor()
#    flist = da.get_shot_list()
#    df = da.read_logger(flist[0])
#    print(df.head())
