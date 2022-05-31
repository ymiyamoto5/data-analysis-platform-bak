# -*- coding: utf-8 -*-
"""
 ==================================
  experiment_dsl_els.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""
"""
export APP_CONFIG_PATH=/Users/hao/notebooks/data-analysis-platform/app_config_dev.json
"""

# import json
import os
import sys

sys.path.append("/Users/hao/.ipython")

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from dsl_generator.fft_tools import *
from dsl_generator.plotly_utils import *

# from datetime import date, datetime, timedelta
# from textwrap import dedent as d


# ライブラリインポート
sys.path.append(os.path.join(os.getcwd(), "../"))
# sys.path.append("/Users/hao/notebooks/data-analysis-platform/")  # 分析基盤のパス
# from backend.analyzer.analyzer import Analyzer
# from backend.analyzer.h_one_extract_features import *

# from backend.cut_out_shot.cut_out_shot import CutOutShot
# from backend.common import common
# from backend.common.common_logger import logger
from backend.data_reader.data_reader import DataReader
from backend.elastic_manager.elastic_manager import ElasticManager

# from backend.utils.df_to_els import *

# print(ElasticManager.show_indices(index="shots-*-data"))

use_elastic = True

if use_elastic == True:
    dr = DataReader()
    # target = '20210327141514'
    # target = '20210709190000'
    target = "shots-unittest-machine-01-20220516101638"
    shots_data_index = target + "-data"
    shots_meta_index = target + "-meta"
    shot_number = 1
    sample_shots = []
    for shot_number in [1, 2, 3, 4, 5]:
        shot_df = dr.read_shot(shots_data_index, shot_number=shot_number)
        sample_shots.append(shot_df["load01"])
        # print(shot_df.head())


# DATA_ROOT = "/Users/hao/data"
# h0_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df0.csv")["(2)HA-V01"]
# h0_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df0.csv")["(2)HA-V02"]
# h0_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df0.csv")["(2)HA-V03"]
# h0_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df1.csv")["(2)HA-V04"]
# h1_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df1.csv")["(2)HA-V01"]
# h1_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df1.csv")["(2)HA-V02"]
# h1_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df1.csv")["(2)HA-V03"]
# h1_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df2.csv")["(2)HA-V04"]
# h2_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df2.csv")["(2)HA-V01"]
# h2_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df2.csv")["(2)HA-V02"]
# h2_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df2.csv")["(2)HA-V03"]
# h2_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df3.csv")["(2)HA-V04"]
# h3_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df3.csv")["(2)HA-V01"]
# h3_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df3.csv")["(2)HA-V02"]
# h3_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df3.csv")["(2)HA-V03"]
# h3_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df4.csv")["(2)HA-V04"]
# h4_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df4.csv")["(2)HA-V01"]
# h4_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df4.csv")["(2)HA-V02"]
# h4_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df4.csv")["(2)HA-V03"]
# h4_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df5.csv")["(2)HA-V04"]
# h5_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df5.csv")["(2)HA-V01"]
# h5_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df5.csv")["(2)HA-V02"]
# h5_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df5.csv")["(2)HA-V03"]
# h5_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df5.csv")["(2)HA-V04"]
# h6_1 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df6.csv")["(2)HA-V01"]
# h6_2 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df6.csv")["(2)HA-V02"]
# h6_3 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df6.csv")["(2)HA-V03"]
# h6_4 = pd.read_csv(DATA_ROOT + "/sample/inflections/h/df6.csv")["(2)HA-V04"]
# # mitbih_00 = pd.read_csv(DATA_ROOT + "/sample/inflections/mitbih_00.csv")["0"]
# # mitbih_01 = pd.read_csv(DATA_ROOT + "/sample/inflections/mitbih_01.csv")["0"]
# # mitbih_02 = pd.read_csv(DATA_ROOT + "/sample/inflections/mitbih_02.csv")["0"]
# # mitbih_03 = pd.read_csv(DATA_ROOT + "/sample/inflections/mitbih_03.csv")["0"]
# # mitbih_04 = pd.read_csv(DATA_ROOT + "/sample/inflections/mitbih_01.csv")["0"]
# p1 = pd.read_csv(DATA_ROOT + "/sample/inflections/1ch_01.csv")["(3)HA-V01"][6500:9000]
# im2a0 = np.load(DATA_ROOT + "/sample/inflections/all_sensors.npy")[1, 500:2000, 2]  # 圧A
# im2a32 = np.load(DATA_ROOT + "/sample/inflections/all_sensors.npy")[32, 500:2000, 2]
# im2d32 = np.load(DATA_ROOT + "/sample/inflections/all_sensors.npy")[32, 500:2000, 5]
# im2noise = pd.read_csv(DATA_ROOT + "/sample/inflections/im2noise.csv")["r2"]
# p2d = np.loadtxt(DATA_ROOT + "/sample/inflections/20200630SmartDie_hardDisp00001.csv", delimiter=",")[:, 14]
# p2u = np.loadtxt(DATA_ROOT + "/sample/inflections/20200630SmartDie_hardDisp00001.csv", delimiter=",")[:, 15]
# breakthrough = pd.read_csv(DATA_ROOT + "/sample/inflections/1908240029.CSV")["data"]


demo_data_dic = {}
# if use_elastic == True:
#    elastic_data_dic = {
#        "sample_0001": np.array(sample_shots[0]),  #
#        "sample_0002": np.array(sample_shots[1]),  #
#        "sample_0003": np.array(sample_shots[2]),  #
#        "sample_0004": np.array(sample_shots[3]),  #
#        "sample_0005": np.array(sample_shots[4]),  #
#        }
#    demo_data_dic.update(elastic_data_dic)

csv_data_dic = {
    #    "h0_ch1": np.array(h0_1),  #
    #    "h0_ch2": np.array(h0_2),  #
    #    "h0_ch3": np.array(h0_3),  #
    #    "h0_ch4": np.array(h0_4),  #
    #    "h1_ch1": np.array(h1_1),  #
    #    "h1_ch2": np.array(h1_2),  #
    #    "h1_ch3": np.array(h1_3),  #
    #    "h1_ch4": np.array(h1_4),  #
    #    "h2_ch1": np.array(h2_1),  #
    #    "h2_ch2": np.array(h2_2),  #
    #    "h2_ch3": np.array(h2_3),  #
    #    "h2_ch4": np.array(h2_4),  #
    #    "h3_ch1": np.array(h3_1),  #
    #    "h3_ch2": np.array(h3_2),  #
    #    "h3_ch3": np.array(h3_3),  #
    #    "h3_ch4": np.array(h3_4),  #
    #    "h4_ch1": np.array(h4_1),  #
    #    "h4_ch2": np.array(h4_2),  #
    #    "h4_ch3": np.array(h4_3),  #
    #    "h4_ch4": np.array(h4_4),  #
    #    "h5_ch1": np.array(h5_1),  #
    #    "h5_ch2": np.array(h5_2),  #
    #    "h5_ch3": np.array(h5_3),  #
    #    "h5_ch4": np.array(h5_4),  #
    #    "h6_ch1": np.array(h6_1),  #
    #    "h6_ch2": np.array(h6_2),  #
    #    "h6_ch3": np.array(h6_3),  #
    #    "h6_ch4": np.array(h6_4),  #
    #    "mitbih_00": np.array(mitbih_00),  #
    #    "mitbih_01": np.array(mitbih_01),  #
    #    "mitbih_02": np.array(mitbih_02),  #
    #    "mitbih_03": np.array(mitbih_03),  #
    #    "mitbih_04": np.array(mitbih_04),  #
    # "mold2-small (100Hz)": im2a0[::10],  # 10ポイントに1ポイント間引き、データ量は1/10に、SamplingRateは100Hzになる。
    # "mold2 (1000Hz)": np.array(im2a0),
    # "im2noise (1000Hz)": np.array(im2noise),
    # "H (100kHz)": np.array(p1),
    # "press1 (1000Hz)": p2d,
    # "press2 (1000Hz)": p2u,
    # "breakthrough (100kHz)": np.array(breakthrough),
}
# demo_data_dic.update(csv_data_dic)

## h-oneデータ追加
# from pathlib import Path
# p = Path(DATA_ROOT+'/H-One/20201127/shots/')
# flist = list(sorted(p.glob('shots_*.csv')))
# h_df = {}
# for f in flist:
#    df1 = pd.read_csv(f)
#    shot = os.path.basename(f)[0:9]
#    for ch in ['v1','v2','v3','v4']:
#        h_df['h-%s:%s'%(shot,ch)] = np.array(df1[ch])
# demo_data_dic.update(h_df)


def _idiff(x):
    # 必ずraw=Trueで呼ぶこと。
    # x は窓内の値が入った配列
    # x[0]が最も古い、x[-1]が最も新しい値
    # 集計後の値を return する
    i_width = int(len(x) / 2)
    return x[-i_width:].mean() - x[:i_width].mean()


def _rdiff(x):
    # 入力長は3固定。必ずraw=Trueで呼ぶこと。
    return x[1:].mean() - x[:1].mean()


def _make_df(d, fs=1000, low=0, high=10000, r_window=5, rolling_center=True):
    df = pd.DataFrame(d, columns=["original"])
    df["m"] = df.original.rolling(r_window, min_periods=1, center=rolling_center).mean()  # moving average;  center=Trueしないとピークが右にずれる
    if low == 0 and high == 0:  # 上下限とも0ならFFTスキップ
        df["d"] = df["m"]
    else:
        s, f, p = fft_spectrum(df.m, fs=fs)  # FFT
        df["d"] = bandpass_ifft(s, f, low, high).real  # バンドパスして逆FFT
    # d->v,v->aの操作は通常の階差(d[0]-d[-1])ではなく一つ先の点と一つ前の点の差分(d[1]-d[-1])を取っている。
    # d->v->a->diffの過程で検出したい現象が過去よりにずれていくのを防ぐため。

    df["v"] = (
        df.d.rolling(3, center=True).apply(_rdiff, raw=True).rolling(r_window, min_periods=1, center=rolling_center).mean()
    )  # moving averageに対して微分
    df["a"] = (
        df.v.rolling(3, center=True).apply(_rdiff, raw=True).rolling(r_window, min_periods=1, center=rolling_center).mean()
    )  # velocityに対してさらに微分

    return df


demo_data = demo_data_dic
g_df = pd.DataFrame({})

index_df = ElasticManager.show_indices(index="shots-*-data")
print(index_df)
index_df["docs.count"] = index_df["docs.count"].astype(int)
index_df = index_df[index_df["docs.count"] > 0]

# controls = dbc.FormGroup(
controls = dbc.Form(
    [
        "index",
        dcc.Dropdown(
            id="els_index",
            clearable=False,
            value=index_df["index"][0],
            options=[
                {"label": r["index"].replace("shots-", "").replace("-data", " (") + str(r["docs.count"]) + ")", "value": r["index"]}
                for i, r in index_df.iterrows()
            ]
            #            options=[
            #                    {'label': 'machine-01-20210709190000', 'value': 'shots-machine-01-20210709190000-data'},
            #                    {'label': 'machine-01-20220120152926', 'value': 'shots-machine-01-20220120152926-data'},
            #                    {'label': 'machine-01-20220120153958', 'value': 'shots-machine-01-20220120153958-data'},
            #            ]
        ),
        "shot number",
        dcc.Dropdown(
            id="data_source",
            clearable=False,
            # value=list(demo_data)[0],
            options=[{"label": d, "value": d} for d in demo_data],
            #            options=[
            #                {'label': 'H', 'value': 'H'},
            #                {'label': 'mold2', 'value': 'mold2'},
            #                {'label': 'mold2-small', 'value': 'mold2-small'},
            #                {'label': 'press1', 'value': 'press1'},
            #                {'label': 'press2', 'value': 'press2'},
            #            ]
        ),
        "サンプリングレート(Hz)",
        dcc.RadioItems(
            id="fs",
            value=100,
            options=[
                {"label": "100", "value": 100},
                {"label": "1000", "value": 1000},
                {"label": "10k", "value": 10000},
                {"label": "100k", "value": 100000},
            ],
        ),
        "マーカー",
        dcc.Checklist(
            id="r_marker",
            options=[
                {"label": "marker", "value": "marker"},
            ],
            value=[],
        ),
        html.Hr(),
        "検索範囲限定手法",
        dcc.RadioItems(
            id="search_selector",
            value="fixed",
            options=[
                {"label": "固定", "value": "fixed"},
                {"label": "値域による範囲限定", "value": "value"},
                {"label": "特徴点による範囲限定", "value": "feature"},
            ],
        ),
        "バンドパス下限(Hz)",
        # dcc.Slider(id='low',min=0,max=20,value=0,marks={0:'0',20:'20',40:'40',60:'60',80:'80',100:'100'},step=5,tooltip={'always_visible':False, 'placement':'bottom'}),
        dcc.Slider(
            id="low",
            min=0,
            max=20,
            value=0,
            marks={0: "0", 10000: "10k", 20000: "20k", 30000: "30k"},
            step=5,
            tooltip={"always_visible": False, "placement": "bottom"},
        ),
        "バンドパス上限(Hz)",
        dcc.Slider(
            id="high",
            min=0,
            max=200,
            value=0,
            marks={0: "0", 10000: "10k", 20000: "20k", 30000: "30k", 40000: "40k"},
            step=5,
            tooltip={"always_visible": False, "placement": "bottom"},
        ),
        "移動平均範囲",
        dcc.Slider(
            id="r_window",
            min=1,
            max=399,
            value=1,
            marks={1: "1", 399: "399"},
            step=2,
            tooltip={"always_visible": False, "placement": "bottom"},
        ),
        dcc.Checklist(
            id="r_center",
            options=[
                {"label": "center", "value": "rolling_center"},
            ],
            value=[],
        ),
        html.Hr(),
        "検出モード",
        dcc.RadioItems(
            id="mode_selector",
            value="a",
            options=[
                {"label": "displacement", "value": "d"},
                # {'label': 'velocity', 'value': 'v'},
                {"label": "acceleration", "value": "a"},
            ],
        ),
        dcc.RadioItems(
            id="maxmin_selector",
            value="max",
            options=[
                {"label": "max", "value": "max"},
                {"label": "min", "value": "min"},
            ],
        ),
        "検索範囲下限",
        html.Br(),
        # dcc.Input(id='customf',size='50',value='df["custom"] = df.original.rolling(5, center=True).apply(lambda x : x)'),
        dcc.Input(id="search_min", size="30", value="0", debounce=True),
        html.Br(),
        "検索範囲上限",
        html.Br(),
        # dcc.Input(id='customf',size='50',value='df["custom"] = df.original.rolling(5, center=True).apply(lambda x : x)'),
        dcc.Input(id="search_max", size="30", value="10", debounce=True),
        # debounce=Trueで、1文字ごとのイベント発生を抑制。リターン or フォーカス外れたタイミングでcallbackが動く
        # ToDo: ここを手入力のままとするなら、入力のチェックは必須。
        #       そのままevalなので、実は"df.v.idxmax()"とか入力してもちゃんと動く。これはこれで魅力的。
        html.Br(),
        "DSL",
        dcc.Textarea(id="dsl", value="xxxxx", readOnly=True, style={"width": "100%", "height": "10vh", "font-size": "70%"}),
    ]
)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

sidebar = html.Div([controls], style={"margin-top": 15, "margin-left": 20})
content = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="raw_data",
                        style={
                            "height": "30vh",
                        },
                    ),
                    # style={'backgroundColor': '#eeeeee'},
                    width=6,
                ),
                dbc.Col(
                    dcc.Graph(
                        id="spectrum",
                        style={
                            "height": "30vh",
                        },
                    ),
                    # style={'backgroundColor': '#eeeeee'},
                    width=6,
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id="timescale"),
                    # style={'backgroundColor': '#eeeeee',},
                )
            ],
            style={
                "height": "60vh",
                #'backgroundColor': '#eeeeee'
            },
        ),
    ],
    style={"margin-top": 15, "backgroundColor": "#ffffff"},
)
"""
     画面レイアウト上の位置関係

     sidebar ----------+   content --------------------+
     | controls -----+ |   |                           |
     | | index       | |   |   raw_data    spectrum    |
     | | data_source | |   |                           |
     | | fs          | |   |                           |
     | | low         | |   |                           |
     | | high        | |   |                           |
     | | r_window    | |   |                           |
     | |             | |   |       timescale           |
     | |             | |   |                           |
     | |             | |   |                           |
     | +-------------+ |   |                           |
     +-----------------+   +---------------------------+
"""
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className="bg-light"),
                dbc.Col(content, width=9),
            ],
        ),
    ],
    fluid=True,
)


@app.callback(
    Output("data_source", "options"),
    [
        Input("els_index", "value"),
    ],
)
def update_data_source_options(els_index):
    # print(els_index)
    shots_meta_df = dr.read_shots_meta(els_index.replace("-data", "-meta"))
    # print(shots_meta_df.shape)
    return [{"label": d, "value": d} for d in shots_meta_df.shot_number]


@app.callback(
    Output("data_source", "value"),
    [
        Input("data_source", "options"),
    ],
)
def update_data_source_value(options):
    # print(options)
    return options[0]["value"]


# Define callback to update graph
# サンプリングレートが更新されたらバンドパス下限のmaxを書き換え
@app.callback(Output("low", "max"), [Input("fs", "value")])
def update_low_max(fs):
    if fs == 100000:
        return 30000
    elif fs == 10000:
        return 3000
    elif fs == 1000:
        return 300
    else:
        return 100


# バンドパス下限のmaxが更新されたらmarksを書き換え
@app.callback(Output("low", "marks"), [Input("low", "max")])
def update_low_marks(fs):
    return {
        0: "0",
        fs: str(fs),
    }


# サンプリングレートが更新されたらバンドパス上限のmaxを書き換え
@app.callback(Output("high", "max"), [Input("fs", "value")])
def update_high_max(fs):
    if fs == 100000:
        return 40000
    elif fs == 10000:
        return 4000
    elif fs == 1000:
        return 400
    else:
        return 200


# バンドパス上限のmaxが更新されたらmarksを書き換え
@app.callback(Output("high", "marks"), [Input("high", "max")])
def update_high_marks(fs):
    return {
        0: "0",
        fs: str(fs),
    }


# サンプリングレートが更新されたら移動平均範囲のmaxを書き換え
@app.callback(Output("r_window", "max"), [Input("fs", "value")])
def update_rwin_max(fs):
    if fs == 100000:
        return 399
    elif fs == 10000:
        return 199
    else:
        return 29


# サンプリングレートが更新されたら移動平均範囲のmarksを書き換え
@app.callback(Output("r_window", "marks"), [Input("fs", "value")])
def update_rwin_marks(fs):
    if fs == 100000:
        return {
            1: "1",
            49: "49",
            99: "99",
            149: "149",
            199: "199",
            249: "249",
            299: "299",
            349: "349",
            399: "399",
        }
    elif fs == 10000:
        return {
            1: "1",
            49: "49",
            99: "99",
            149: "149",
            199: "199",
        }
    else:
        return {1: "1", 9: "9", 19: "19", 29: "29"}


# @app.callback(Output('peak_dir', 'style'), [Input("find_i", "value")])
# def update_peakdir(find_i):
#    if 'find_i' in find_i:
#        return {'display': 'block'}
#    else:
#        return {'display': 'none'}
#
# @app.callback(Output('tilt_width', 'disabled'), [Input("find_i", "value")])
# def update_tiltwidth(find_i):
#    if 'find_i' in find_i:
#        return False
#    else:
#        return True
#
# @app.callback(Output('peak_ratio', 'disabled'), [Input("find_i", "value")])
# def update_peak_ratio(find_i):
#    if 'find_i' in find_i:
#        return False
#    else:
#        return True

# FFT spectrum更新
@app.callback(
    Output("spectrum", "figure"),
    [
        Input("els_index", "value"),
        Input("data_source", "value"),
        Input("fs", "value"),
        Input("low", "value"),
        Input("high", "value"),
        Input("spectrum", "relayoutData"),
    ],
)
def update_spectrum(els_index, data_label, fs, low, high, relayoutData):
    #    d = demo_data[data_label]
    shot_df = read_shot_els(els_index, data_label)
    if type(shot_df) != pd.core.frame.DataFrame:
        return
    d = np.array(shot_df.load01)
    s, f, p = fft_spectrum(d, fs)
    xvalues = f[0 : int(len(s) / 2)]
    yvalues = np.abs(s[0 : int(len(s) / 2)]) / (len(s) / 2)
    fig = {
        "data": [
            # {'x':f[0:int(len(s)/2)] , 'y':np.abs(s[0:int(len(s)/2)])/(len(s)/2) , 'type': 'scatter', 'mode':'markers', 'marker_color':'#3498db'},
            {
                "x": xvalues,
                "y": yvalues,
                "yaxis": "y",
                "type": "line",
                "mode": "line",
                "marker_color": "#3498db",
            },
        ],
        "layout": {
            "title": "FFT spectrum",
            "shapes": [],
            "xaxis_title": "Hz",
            "margin": {"t": 30, "l": 70, "r": 70, "b": 50},
        }
        #'layout': { 'title': 'FFT spectrum', 'height': 140, 'shapes':[],'margin':{'t':30,'l':20,'r':20,'b':20}, 'xaxis_title':'Hz' }
    }
    if low != 0 or high != 0:
        fig["layout"]["shapes"].append(
            {
                "type": "rect",
                "x0": 0,
                "x1": low,
                "y0": 0,
                "y1": np.max(yvalues),
                "xref": "x",
                "yref": "y",
                "fillcolor": "gray",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            }
        )
        fig["layout"]["shapes"].append(
            {
                "type": "rect",
                "x0": high,
                "x1": xvalues[-1],
                "y0": 0,
                "y1": np.max(yvalues),
                "xref": "x",
                "yref": "y",
                "fillcolor": "gray",
                "opacity": 0.5,
                "layer": "below",
                "line_width": 0,
            }
        )
    if relayoutData is not None:
        if "yaxis.range[0]" in relayoutData:
            fig["layout"]["yaxis"] = dict(range=[relayoutData["yaxis.range[0]"], relayoutData["yaxis.range[1]"]])
        # X軸の操作をバンドパス調整とグラフの両方でやると混乱。
        # if 'xaxis.range[0]' in relayoutData:
        #    fig['layout']['xaxis'] = dict(range=[relayoutData['xaxis.range[0]'],relayoutData['xaxis.range[1]']])

    return fig


# Raw dataを更新
@app.callback(
    Output("raw_data", "figure"),
    [
        Input("els_index", "value"),
        Input("data_source", "value"),
        Input("fs", "value"),
        Input("low", "value"),
        Input("high", "value"),
        Input("raw_data", "relayoutData"),
    ],
)
def update_raw_data(els_index, data_label, fs, low, high, relayoutData):
    #    d = demo_data[data_label]
    shot_df = read_shot_els(els_index, data_label)
    d = np.array(shot_df.load01)
    xvalues = np.arange(len(d))
    yvalues = d
    fig = {
        "data": [
            # {'x':f[0:int(len(s)/2)] , 'y':np.abs(s[0:int(len(s)/2)])/(len(s)/2) , 'type': 'scatter', 'mode':'markers', 'marker_color':'#3498db'},
            {
                "x": xvalues,
                "y": yvalues,
                "yaxis": "y",
                "type": "line",
                "mode": "line",
                "marker_color": "#3498db",
            },
        ],
        "layout": {
            "title": "Raw data",
            "shapes": [],
            "xaxis_title": "Hz",
            "margin": {"t": 30, "l": 70, "r": 70, "b": 50},
        }
        #'layout': { 'title': 'Raw data', 'height': 140, 'shapes':[],'margin':{'t':30,'l':30,'r':30,'b':20}, 'xaxis_title':'Hz' }
    }
    #    if low != 0 or high != 0:
    #        fig['layout']['shapes'].append(
    #             {'type':'rect',
    #             'x0':0, 'x1':low,
    #             'y0':0, 'y1':np.max(yvalues),
    #             'xref': 'x', 'yref': 'y',
    #             'fillcolor':'gray',
    #             'opacity':0.5,
    #             'layer':'below',
    #             'line_width':0,}
    #        )
    #        fig['layout']['shapes'].append(
    #            {'type':'rect',
    #             'x0':high, 'x1':xvalues[-1],
    #             'y0':0, 'y1':np.max(yvalues),
    #             'xref': 'x', 'yref': 'y',
    #             'fillcolor':'gray',
    #             'opacity':0.5,
    #             'layer':'below',
    #             'line_width':0,}
    #        )
    # raw_dataへのzoom指示は、timescaleへ反映させる。raw_data自身はtimescaleの非表示範囲を自身の網掛けとして表現。
    # この動作は横方向のzoomのみ。縦方向のzoom指示は無視。
    if relayoutData is not None:
        if "xaxis.range[0]" in relayoutData:
            fig["layout"]["shapes"].append(
                {
                    "type": "rect",
                    "x0": 0,
                    "x1": relayoutData["xaxis.range[0]"],
                    "y0": np.min(yvalues),
                    "y1": np.max(yvalues),
                    "xref": "x",
                    "yref": "y",
                    "fillcolor": "gray",
                    "opacity": 0.5,
                    "layer": "below",
                    "line_width": 0,
                }
            )
        if "xaxis.range[1]" in relayoutData:
            fig["layout"]["shapes"].append(
                {
                    "type": "rect",
                    "x0": relayoutData["xaxis.range[1]"],
                    "x1": np.max(xvalues),
                    "y0": np.min(yvalues),
                    "y1": np.max(yvalues),
                    "xref": "x",
                    "yref": "y",
                    "fillcolor": "gray",
                    "opacity": 0.5,
                    "layer": "below",
                    "line_width": 0,
                }
            )
    return fig


@app.callback(
    Output("search_max", "value"),
    [
        Input("search_selector", "value"),
        Input("search_max", "value"),
        Input("timescale", "relayoutData"),
    ],
)
def update_searchmax(search_select, search_max, relayoutData):
    # return 100
    # print("update_searchmax:", relayoutData)
    # print("search_max@update_searchmax:", search_max)
    if search_select == "fixed":
        if relayoutData is not None and "xaxis.range[1]" in relayoutData:
            return relayoutData["xaxis.range[1]"]
        else:
            # print(search_max)
            return search_max
    elif search_select == "value":
        if relayoutData is not None and "yaxis.range[1]" in relayoutData:
            return relayoutData["yaxis.range[1]"]
        else:
            # print(search_max)
            return search_max
    elif search_select == "feature":
        return search_max


@app.callback(
    Output("dsl", "value"),
    [
        Input("r_window", "value"),
        Input("search_selector", "value"),
        Input("mode_selector", "value"),
        Input("maxmin_selector", "value"),
        Input("search_min", "value"),
        Input("search_max", "value"),
    ],
)
def update_dsl(r_window, search_select, mode, maxmin, search_min, search_max):
    mode_list = {"d": "DST", "a": "ACC"}
    maxmin_list = {"max": "IDXMAX", "min": "IDXMIN"}
    target_str = "%s(%s)" % (maxmin_list[maxmin], mode_list[mode])

    if search_select in ["fixed", "feature"]:
        dsl_str = "ROLLING_WINDOW = %d;\\\nHORIZONTAL_LIMIT = [%s, %s];\\\nVERTICAL_LIMIT = [%s, %s];\\\nTARGET = %s;\\" % (
            r_window,
            search_min,
            search_max,
            "None",
            "None",
            target_str,
        )
    else:
        dsl_str = "ROLLING_WINDOW = %d;\\\nHORIZONTAL_LIMIT = [%s, %s];\\\nVERTICAL_LIMIT = [%s, %s];\\\nTARGET = %s;\\" % (
            r_window,
            "None",
            "None",
            search_min,
            search_max,
            target_str,
        )

    return dsl_str


@app.callback(
    Output("search_min", "value"),
    [
        Input("search_selector", "value"),
        Input("search_min", "value"),
        Input("timescale", "relayoutData"),
    ],
)
def update_searchmin(search_select, search_min, relayoutData):
    if search_select == "fixed":
        if relayoutData is not None and "xaxis.range[0]" in relayoutData:
            return relayoutData["xaxis.range[0]"]
        else:
            # print(search_min)
            return search_min
    elif search_select == "value":
        if relayoutData is not None and "yaxis.range[0]" in relayoutData:
            return relayoutData["yaxis.range[0]"]
        else:
            # print(search_min)
            return search_min
    elif search_select == "feature":
        return search_min


################ DSL #########################################
DST = "d"
VCT = "v"
ACC = "a"


# def IDXMAX(df, d):
#    # print('IDXMAX:',d)
#    #    _gendf()
#    #    if NARROW is True:
#    #        ndf = _narrowing()
#    #    else:
#    #        ndf = df
#    target = df[d].idxmax()
#    return target


def IDXMAX(d):
    target = g_df[d].idxmax()
    return target


# def IDXMIN(df, d):
#    #    _gendf()
#    #    if NARROW is True:
#    #        ndf = _narrowing()
#    #    else:
#    #        ndf = df
#    target = df[d].idxmin()
#    return target


def IDXMIN(df, d):
    target = g_df[d].idxmin()
    return target


# def eval_func(fstr):
#    print('fstr@eval_func:',fstr)
#    print('df@eval_func:',df.head())
#    return eval(fstr.replace('(','(df,'))
################ DSL #########################################


def read_shot_els(index, shot):
    shot_df = dr.read_shot(index, shot_number=shot)
    return shot_df


# メインウィンドウ(timescale)を更新
@app.callback(
    Output("timescale", "figure"),
    [
        Input("els_index", "value"),
        Input("data_source", "value"),
        Input("mode_selector", "value"),
        Input("fs", "value"),
        Input("search_selector", "value"),
        Input("search_min", "value"),
        Input("search_max", "value"),
        Input("maxmin_selector", "value"),
        Input("low", "value"),
        Input("high", "value"),
        Input("r_window", "value"),
        Input("r_marker", "value"),
        Input("raw_data", "relayoutData"),
        Input("timescale", "relayoutData"),
    ],
)
def update_timescale(
    els_index,
    data_label,
    mode,
    fs,
    search_way,
    search_min,
    search_max,
    maxmin,
    low,
    high,
    r_window,
    r_marker,
    raw_relayoutData,
    relayoutData,
):
    scatter_mode = "lines"
    # mode='marker'は高負荷のため、表示範囲を絞ったときだけに限定すべし。
    if "marker" in r_marker:
        scatter_mode = "markers"
    #    b_find_i = 'find_i' in find_i
    # print(b_find_i)
    # demo_dataはglobal変数でここから参照できてるということは、dfも同じ扱いにすれば行けるか?
    # d = demo_data[data_label]
    shot_df = read_shot_els(els_index, data_label)
    d = np.array(shot_df.load01)

    # df = _make_df(d, fs=fs, low=low, high=high, r_window=r_window)
    global g_df
    g_df = _make_df(d, fs=fs, low=low, high=high, r_window=r_window)

    if search_way == "fixed":
        if maxmin == "min":
            temp_df = g_df[(g_df.index >= int(search_min)) & (g_df.index <= int(search_max))]
            if len(temp_df) > 0:
                peak = temp_df[mode].idxmin()
        else:
            temp_df = g_df[(g_df.index >= int(search_min)) & (g_df.index <= int(search_max))]
            if len(temp_df) > 0:
                peak = temp_df[mode].idxmax()
    elif search_way == "value":
        #        print('peak@value:',peak)
        #        peak = 500
        search_df = g_df[(g_df.d >= float(search_min)) & (g_df.d <= float(search_max))]
        # print(search_df)
        # print(search_df.index[0],search_df.index[-1])
        if len(search_df) > 0:
            if maxmin == "min":
                peak = search_df[mode].idxmin()
            else:
                peak = search_df[mode].idxmax()

    if raw_relayoutData is not None:
        if "xaxis.range[0]" in raw_relayoutData:
            g_df = g_df[int(raw_relayoutData["xaxis.range[0]"]) : int(raw_relayoutData["xaxis.range[1]"])]

    # 分析対象は元波形からノイズ除去したd、それを階差処理したv,a。元波形は邪魔にならない程度に半透明にして重ねる。
    df1 = g_df[["d", "v", "a"]]
    df1_cols = ["displacement", "velo.", "acc."]  # このタイトルをDSLに併せてDST,VCT,ACCにした方が良いか?
    heights_list = [0.1 for c in df1.columns]
    heights_list[0] = 0.3
    fig = multi_col_figure(
        df1,
        title="",
        row_titles=df1_cols,
        mode=scatter_mode,
        margin={"t": 20, "l": 30, "r": 10, "b": 20},
        heights_list=heights_list,
    )
    fig.add_trace(
        go.Scatter(x=df1.index, y=g_df.original, marker_color="#444444", opacity=0.3),
        row=1,
        col=1,
    )  # 元波形重ね
    yref = "y3"  # y3:加速度

    # 検索範囲、検索結果表示
    if search_way == "fixed":  # 限定手法:固定
        hatch_max = min(int(search_max), df1.index[-1])  # 網掛け=検索範囲
        hatch_min = max(int(search_min), df1.index[0])  # 網掛け=検索範囲
        if int(search_max) > 10:  # とりあえず初期値10入れてある。初期値のままなら検索範囲表示しない
            plotly_vspan(fig, hatch_min, hatch_max, yref="y")
            plotly_vspan(fig, peak, peak, ftype="line", yref="y", fillcolor="red", alpha=1.0)
            if mode == "a":
                yref = "y3"
                plotly_vspan(fig, hatch_min, hatch_max, yref=yref)
                plotly_vspan(fig, peak, peak, ftype="line", yref=yref, fillcolor="red", alpha=1.0)
    elif search_way == "value":  # 限定手法:値域
        if len(search_df) > 0:
            hatch_max = min(search_df.index[-1], df1.index[-1])  # 網掛け=検索範囲
            hatch_min = max(search_df.index[0], df1.index[0])  # 網掛け=検索範囲
            # print(search_df)
            # print(search_max,search_min)
            # print(hatch_max,hatch_min)
            plotly_hspan(
                fig,
                float(search_min),
                float(search_max),
                ftype="rect",
                yref="y",
                fillcolor="gray",
                alpha=0.5,
            )
            #        plotly_vspan(fig, search_df.index[0], search_df.index[-1], yref="y")
            #        plotly_vspan(fig, search_df.index[0], search_df.index[-1], yref="y3")
            plotly_vspan(fig, hatch_min, hatch_max, yref="y")
            plotly_vspan(fig, hatch_min, hatch_max, yref="y3")
            plotly_vspan(fig, peak, peak, ftype="line", yref="y", fillcolor="red", alpha=1.0)
    #        plotly_vspan(fig,search_df[mode].idxmax(),search_df[mode].idxmax(),ftype='line',yref='y',fillcolor='red',alpha=1.0)
    #        plotly_vspan(fig,search_df[mode].idxmax(),search_df[mode].idxmax(),ftype='line',yref='y4',fillcolor='red',alpha=1.0)
    elif search_way == "feature":  # 限定手法:特徴点
        search_max = str(search_max)
        search_min = str(search_min)
        hatch_max = min(eval(search_max), df1.index[-1])  # 網掛け=検索範囲
        hatch_min = max(eval(search_min), df1.index[0])  # 網掛け=検索範囲
        # search_max,search_minに'検索範囲上限','検索範囲下限'に入力された文字列が入ってくるので、
        # それをそのままevalする。evalした結果IDXMAX()などの関数が呼ばれる。
        if type(search_min) != str:
            search_min = str(search_min)
        if type(search_max) != str:
            search_max = str(search_max)

        # plotly_vspan(fig, eval(search_min), eval(search_max), yref="y")
        # 検索対象網掛けはdのみ。v or aを特定するにはDSLをparseする必要あり。
        plotly_vspan(fig, hatch_min, hatch_max, yref="y")
        if maxmin == "min":
            peak = g_df[mode][(g_df.index >= eval(search_min)) & (g_df.index <= eval(search_max))].idxmin()
        else:
            peak = g_df[mode][(g_df.index >= eval(search_min)) & (g_df.index <= eval(search_max))].idxmax()
        plotly_vspan(fig, peak, peak, ftype="line", yref="y", fillcolor="red", alpha=1.0)

    fig.update_layout(
        margin={"t": 30, "l": 70, "r": 70, "b": 50},
        plot_bgcolor="white",
        # paper_bgcolor='#ffffff',
    )
    fig.update_xaxes(gridcolor="#eeeeee")
    fig.update_yaxes(gridcolor="#eeeeee")

    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8047)

"""
検索範囲上限に文字入力されると、316のupdate_timescale()に飛ぶ。
限定手法=特徴点の時は、577の分岐に来て、search_maxに入ってる文字列をそのままeval()。
callback関数であるupdate_timescale()と、evalした結果実行されるIDXMAX()の間で、
コンテキストが共有されてないのが問題であって、
参照したいdfはupdate_timescaleの中で作ってるので当たり前な気もするが、
普通に関数呼び出しした時はコンテキストは共有されるはず。
update_timescale()の中からdemo_dataは参照できてるので、手はある気がするが...?
"""
