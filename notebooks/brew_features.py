import json
import os
from datetime import date, datetime, timedelta
from textwrap import dedent as d

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go

from fft_tools import *
from plotly_utils import *

gened_features = {}  # global!!!


def read_logger(f):
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
    df = pd.read_csv(
        f,
        encoding="cp932",
        skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],
    ).rename({"CH名称": "time"}, axis=1)
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

    return df, unit, offset, calibration, v_range, channel


# 項目の情報を取得するため1ファイルだけ先に読む。ToDo:前データ項目共通の前提
from pathlib import Path

# p = Path('/Users/hao/data/ADDQ/20211004ブレークスルー/')
p = Path("/customer_data/ymiyamoto5-aida_A39D/private/data/aida/")
flist = list(sorted(p.glob("*.CSV")))
f = flist[10]
df = read_logger(f)[0][:3000]

## "項目名" => 表示subplot-id のdictionary
# disp_col = {}
# disp_col['プレス荷重shift'] = 0
# disp_col['右垂直'] = 0
# disp_col['スライド変位右'] = 1
# disp_col['加速度左右_X_左+500G'] = 2
#
# yref = {0:'y', 1:'y2', 2:'y3'}

# "項目名" => 表示subplot-id のdictionary
# nrows = 3; ncols = 2;
# disp_col = {}
# disp_col['プレス荷重shift'] = [1,1]
# disp_col['右垂直'] = [1,1]
# disp_col['左垂直'] = [1,1]
# disp_col['スライド変位右'] = [2,1]
# disp_col['スライド変位左'] = [2,1]
# disp_col['M30ボルスタ右奥'] = [1,2]
# disp_col['加速度左右_X_左+500G'] = [3,1]
# disp_col['加速度上下_Y_下+500G'] = [3,1]
# disp_col['加速度前後_Z_前+500G'] = [3,1]
# disp_col['スライド＿金型隙間'] = [2,2]

xref = {1: "x", 2: "x2", 3: "x3", 4: "x4"}
yref = {1: "y", 2: "y2", 3: "y3", 4: "y4", 5: "y5", 6: "y6"}


class brewFeatures:
    def __init__(self):
        self.nrows = 2
        self.ncols = 1
        self.disp_col = {}
        self.disp_col["プレス荷重shift"] = [1, 1, None]
        self.disp_col["スライド変位右"] = [2, 1, None]

    def set_dispcol(self, disp_col):
        """
        disp_colは、項目名 => [表示位置row, 表示位置col] となるdictionary。
        """
        self.disp_col = disp_col
        """
        disp_colからnrows,ncolsを算出
        values()でdict_valuesを取り出してlistにcast、さらにnumpy.arrayにcast
        (2,x)のarrayになるので、[:,0]でrowだけ、[:,1]でcolだけ取り出す。
            disp_col.values()                        # dict_values([[1, 1], [1, 1], [2, 1], [2, 1], [2, 1]])
            list(disp_col.values())                  # [[1, 1], [1, 1], [2, 1], [2, 1], [2, 1]]
            np.array(list(disp_col.values()))        # array([[1, 1],
                                                              [1, 1],
                                                              [2, 1],
                                                              [2, 1],
                                                              [2, 1]])
            np.array(list(disp_col.values()))[:,0]   #   array([1, 1, 2, 2, 2])
        """
        self.nrows = int(np.array(list(disp_col.values()))[:, 0].max())  # intにcastしないとダメ、なんでだ?
        self.ncols = int(np.array(list(disp_col.values()))[:, 1].max())

    def get_dispcol(self):
        return self.disp_col

    # 特徴抽出操作指示のgridの1行を生成
    def gen_input_forms(self, row_id, fname="", sel_col="", rw=1, llim=0, ulim=0):
        return (
            dbc.Col(
                dcc.Input(id="feature_name%d" % row_id, value=fname),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="select_col%d" % row_id, value=sel_col, options=[{"label": str(s), "value": str(s)} for s in df.columns[1:]]
                ),
                width=2,
            ),
            dbc.Col(
                dcc.Input(id="rolling_width%d" % row_id, value=rw),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="low_find_type%d" % row_id,
                    value="固定",
                    options=[{"label": str(s), "value": str(s)} for s in ["固定", "値域>", "値域<", "特徴点"]],
                ),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(id="low_feature%d" % row_id, value="-", options=[{"label": "-", "value": "-"}]),
                width=1,
            ),
            dbc.Col(
                dcc.Input(id="low_lim%d" % row_id, value=llim),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="up_find_type%d" % row_id,
                    value="固定",
                    options=[{"label": str(s), "value": str(s)} for s in ["固定", "値域>", "値域<", "特徴点"]],
                ),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(id="up_feature%d" % row_id, value="-", options=[{"label": "-", "value": "-"}]),
                width=1,
            ),
            dbc.Col(
                dcc.Input(id="up_lim%d" % row_id, value=ulim),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="find_target%d" % row_id,
                    clearable=False,
                    value="DPT",
                    options=[{"label": "元波形", "value": "DPT"}, {"label": "速度", "value": "VCT"}, {"label": "加速度", "value": "ACC"}],
                ),
                width=1,
            ),
            dbc.Col(
                dcc.Dropdown(
                    id="find_dir%d" % row_id,
                    clearable=False,
                    value="MAX",
                    options=[{"label": "MAX", "value": "MAX"}, {"label": "MIN", "value": "MIN"}],
                ),
                width=1,
            ),
        )

    # 特徴抽出機能のコア部   ToDo: グラフ操作を分離して特徴抽出だけを呼べるように
    def locate_feature(
        self,
        df,
        fig,
        feature_name,
        select_col,
        rolling_width,
        low_find_type,
        low_feature,
        low_lim,
        up_find_type,
        up_feature,
        up_lim,
        find_target,
        find_dir,
    ):
        global gened_features
        # global disp_col
        target_i = None

        if feature_name == "":
            return fig

        x_lim = [0, 0]  # 初期値

        if low_find_type == "固定":
            x_lim[0] = int(low_lim)
        elif low_find_type == "値域>":  # 指定値より大きい範囲を検索して左端のindexを返す
            sdf = df[(df[select_col] >= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
        elif low_find_type == "値域<":  # 指定値より小さい範囲を検索して左端のindexを返す
            sdf = df[(df[select_col] <= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
            # print('value:',x_lim)
        elif low_find_type == "特徴点":
            try:
                x_lim[0] = gened_features[low_feature] + int(low_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

        if up_find_type == "固定":
            x_lim[1] = int(up_lim)
        elif up_find_type == "値域>":  # 指定値より大きい範囲を検索して右端のindexを返す
            sdf = df[(df[select_col] >= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
        elif up_find_type == "値域<":  # 指定値より小さい範囲を検索して右端のindexを返す
            sdf = df[(df[select_col] <= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
            # print('value:',x_lim)
        elif up_find_type == "特徴点":
            try:
                x_lim[1] = gened_features[up_feature] + int(up_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

        for d in fig.data:
            if d["name"] == select_col:
                target_fig = [d["yaxis"], d["xaxis"]]
                continue
        #     target_fig = [yref[disp_col[select_col][0]],xref[disp_col[select_col][1]]]
        #    print(fig.data)
        #    print(target_fig)

        ########3 ToDO!!! ###############
        if low_find_type == "値域>":
            plotly_hspan(fig, float(low_lim), float(low_lim) + 5, yref=target_fig[0], xref=target_fig[1], fillcolor="green", alpha=0.2)
        if low_find_type == "値域<":
            plotly_hspan(fig, float(low_lim), float(low_lim) - 5, yref=target_fig[0], xref=target_fig[1], fillcolor="green", alpha=0.2)
        if up_find_type == "値域>":
            plotly_hspan(fig, float(up_lim), float(up_lim) + 5, yref=target_fig[0], xref=target_fig[1], fillcolor="green", alpha=0.2)
        if up_find_type == "値域<":
            plotly_hspan(fig, float(up_lim), float(up_lim) - 5, yref=target_fig[0], xref=target_fig[1], fillcolor="green", alpha=0.2)

        #    print('x_lim:',x_lim)
        plotly_vspan(fig, x_lim[0], x_lim[1], yref=target_fig[0], xref=target_fig[1], alpha=0.2)
        # 検索対象時系列データの生成
        if find_target == "DPT":
            target = df[select_col]
        elif find_target == "VCT":
            target = df[select_col].rolling(int(rolling_width), center=True).mean().diff()
            # print('VCT:')
        elif find_target == "ACC":
            target = (
                df[select_col].rolling(int(rolling_width), center=True).mean().diff().rolling(int(rolling_width), center=True).mean().diff()
            )
            # print('ACC:')
        if x_lim[1] - x_lim[0] > 0:  # 検索範囲が適切に指定されてなければ何もしない  ToDo:「何もしない」ことのフィードバック? 範囲指定せずに検索したい時もある
            #     print('len:',len(target))
            # print('xlim:',x_lim)
            if find_dir == "MAX":
                target_i = target[x_lim[0] : x_lim[1]].idxmax()
            elif find_dir == "MIN":
                target_i = target[x_lim[0] : x_lim[1]].idxmin()
            plotly_vspan(
                fig,
                target_i,
                target_i,
                ftype="line",
                yref=target_fig[0],
                xref=target_fig[1],
                fillcolor="red",
                alpha=1.0,
                layer="above",
                line_width=2,
            )
        target_fig = [yref[self.disp_col[select_col][0]], xref[self.disp_col[select_col][1]]]
        # plotly_vspan(fig,x_lim[0],x_lim[1],yref=target_fig)
        # 検索対象時系列データの生成
        if find_target == "DPT":
            target = df[select_col]
        elif find_target == "VCT":
            target = df[select_col].rolling(int(rolling_width), center=True).mean().diff()
        elif find_target == "ACC":
            target = (
                df[select_col].rolling(int(rolling_width), center=True).mean().diff().rolling(int(rolling_width), center=True).mean().diff()
            )
        if x_lim[1] - x_lim[0] > 0:  # 検索範囲が適切に指定されてなければ何もしない  ToDo:「何もしない」ことのフィードバック? 範囲指定せずに検索したい時もある
            #     print('len:',len(target))
            print("xlim:", x_lim)
            if find_dir == "MAX":
                target_i = target[x_lim[0] : x_lim[1]].idxmax()
            elif find_dir == "MIN":
                target_i = target[x_lim[0] : x_lim[1]].idxmin()
            # plotly_vspan(fig,target_i,target_i,ftype='line',yref=target_fig[0],xref=target_fig[1],alpha=1.0)
            fig.add_vline(x=target_i, line_color="red", row=self.disp_col[select_col][0], col=self.disp_col[select_col][1])
            # span(fig,target_i,target_i,ftype='line',yref=target_fig[0],xref=target_fig[1],alpha=1.0)
            # fig.add_vline(x=2.5, line_width=3, line_dash="dash", line_color="green")

        if target_i is not None:
            gened_features[feature_name] = target_i

        return fig

    def make_app(self):

        import dash_bootstrap_components as dbc
        import dash_core_components as dcc
        import dash_html_components as html
        import plotly.express as px
        from dash.dependencies import Input, Output
        from jupyter_dash import JupyterDash

        #     app = JupyterDash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
        app = JupyterDash("brewFeatures", external_stylesheets=[dbc.themes.CERULEAN])

        # 画面全体のレイアウト
        app.layout = html.Div(
            [
                #     dcc.Dropdown(id='shot_select',options=[{'label':'a','value':'a'},{'label':'b','value':'b'},]),
                # ショット選択
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id="shot_select", value=str(flist[9]), options=[{"label": str(f), "value": str(f)} for f in flist[8:]]
                            ),
                            width=5,
                            style={"width": "50vw"}  # viewpoint height
                            #         style={'height': '20vh','width':'50vw'} # viewpoint height
                        ),
                        # dbc.Col( dcc.Dropdown(id='find_type1',value='固定',options=[{'label':str(s),'value':str(s)} for s in ['固定','値域','特徴点']]), width=1,),
                    ]
                ),
                #     dcc.Dropdown(id='shot_select',options=[{'label':str(f), 'value':str(f)} for f in flist[8:]]),
                # グラフ表示部
                dcc.Graph(id="graph"),
                # 特徴抽出操作指示: gen_input_forms()がInput,Dropdownを含むdbc.Colのリストを生成する
                dbc.Row(
                    [
                        dbc.Col(dbc.Label("特徴量名")),
                        dbc.Col(dbc.Label("対象項目"), width=2),
                        dbc.Col(dbc.Label("移動平均範囲")),
                        dbc.Col(dbc.Label("下限限定方法")),
                        dbc.Col(dbc.Label("下限特徴量")),
                        dbc.Col(dbc.Label("下限位置")),
                        dbc.Col(dbc.Label("上限限定方法")),
                        dbc.Col(dbc.Label("上限特徴量")),
                        dbc.Col(dbc.Label("上限位置")),
                        dbc.Col(dbc.Label("検索対象")),
                        dbc.Col(dbc.Label("検索方向")),
                    ]
                ),
                #         dbc.Row(gen_input_forms(0,fname='vct_min',sel_col='プレス荷重shift',rw=9,llim=1000,ulim=3000)),
                dbc.Row(self.gen_input_forms(0, fname="", sel_col="プレス荷重shift", rw=9, llim=1000, ulim=3000)),
                dbc.Row(self.gen_input_forms(1)),
                dbc.Row(self.gen_input_forms(2)),
                dbc.Row(self.gen_input_forms(3)),
            ]
        )

        # 特徴点セット2行目
        @app.callback(
            Output("low_feature1", "options"),
            [
                Input("low_find_type1", "value"),
                Input("feature_name0", "value"),
                Input("low_feature1", "options"),
            ],
        )
        def set_low_features1(find_type, fname0, options):
            if find_type == "特徴点":
                return [{"label": fname0, "value": fname0}]
            else:
                return options

        @app.callback(
            Output("up_feature1", "options"),
            [
                Input("up_find_type1", "value"),
                Input("feature_name0", "value"),
                Input("up_feature1", "options"),
            ],
        )
        def set_up_features1(find_type, fname0, options):
            if find_type == "特徴点":
                return [{"label": fname0, "value": fname0}]
            else:
                return options

        # 特徴点セット3行目 (1行目と2行目のfeature_nameをDropdownにセットする。このコーディングどうにかならんか....)
        @app.callback(
            Output("low_feature2", "options"),
            [
                Input("low_find_type2", "value"),
                Input("feature_name0", "value"),
                Input("feature_name1", "value"),
                Input("low_feature2", "options"),
            ],
        )
        def set_low_features2(find_type, fname0, fname1, options):
            if find_type == "特徴点":
                return [{"label": f, "value": f} for f in [fname0, fname1]]
            else:
                return options

        @app.callback(
            Output("up_feature2", "options"),
            [
                Input("up_find_type2", "value"),
                Input("feature_name0", "value"),
                Input("feature_name1", "value"),
                Input("up_feature2", "options"),
            ],
        )
        def set_up_features2(find_type, fname0, fname1, options):
            if find_type == "特徴点":
                return [{"label": f, "value": f} for f in [fname0, fname1]]
            else:
                return options

        # 特徴点セット4行目 (1行目と2行目のfeature_nameをDropdownにセットする。このコーディングどうにかならんか....)
        @app.callback(
            Output("low_feature3", "options"),
            [
                Input("low_find_type3", "value"),
                Input("feature_name0", "value"),
                Input("feature_name1", "value"),
                Input("feature_name2", "value"),
                Input("low_feature3", "options"),
            ],
        )
        def set_low_features3(find_type, fname0, fname1, fname2, options):
            if find_type == "特徴点":
                return [{"label": f, "value": f} for f in [fname0, fname1, fname2]]
            else:
                return options  # '特徴点'以外の場合は現状のまま...で良いのか?

        @app.callback(
            Output("up_feature3", "options"),
            [
                Input("up_find_type3", "value"),
                Input("feature_name0", "value"),
                Input("feature_name1", "value"),
                Input("feature_name2", "value"),
                Input("up_feature3", "options"),
            ],
        )
        def set_up_features3(find_type, fname0, fname1, fname2, options):
            if find_type == "特徴点":
                return [{"label": f, "value": f} for f in [fname0, fname1, fname2]]
            else:
                return options

        @app.callback(
            #     dash.dependencies.Output('graph', 'figure'),
            Output("graph", "figure"),
            [
                Input("shot_select", "value"),
                Input("feature_name0", "value"),
                Input("select_col0", "value"),
                Input("rolling_width0", "value"),
                Input("low_find_type0", "value"),
                Input("low_feature0", "value"),
                Input("low_lim0", "value"),
                Input("up_find_type0", "value"),
                Input("up_feature0", "value"),
                Input("up_lim0", "value"),
                Input("find_target0", "value"),
                Input("find_dir0", "value"),
                Input("feature_name1", "value"),
                Input("select_col1", "value"),
                Input("rolling_width1", "value"),
                Input("low_find_type1", "value"),
                Input("low_feature1", "value"),
                Input("low_lim1", "value"),
                Input("up_find_type1", "value"),
                Input("up_feature1", "value"),
                Input("up_lim1", "value"),
                Input("find_target1", "value"),
                Input("find_dir1", "value"),
                Input("feature_name2", "value"),
                Input("select_col2", "value"),
                Input("rolling_width2", "value"),
                Input("low_find_type2", "value"),
                Input("low_feature2", "value"),
                Input("low_lim2", "value"),
                Input("up_find_type2", "value"),
                Input("up_feature2", "value"),
                Input("up_lim2", "value"),
                Input("find_target2", "value"),
                Input("find_dir2", "value"),
                Input("feature_name3", "value"),
                Input("select_col3", "value"),
                Input("rolling_width3", "value"),
                Input("low_find_type3", "value"),
                Input("low_feature3", "value"),
                Input("low_lim3", "value"),
                Input("up_find_type3", "value"),
                Input("up_feature3", "value"),
                Input("up_lim3", "value"),
                Input("find_target3", "value"),
                Input("find_dir3", "value"),
            ],
        )
        def callback_figure(
            shot,
            feature_name0,
            select_col0,
            rolling_width0,
            low_find_type0,
            low_feature0,
            low_lim0,
            up_find_type0,
            up_feature0,
            up_lim0,
            find_target0,
            find_dir0,
            feature_name1,
            select_col1,
            rolling_width1,
            low_find_type1,
            low_feature1,
            low_lim1,
            up_find_type1,
            up_feature1,
            up_lim1,
            find_target1,
            find_dir1,
            feature_name2,
            select_col2,
            rolling_width2,
            low_find_type2,
            low_feature2,
            low_lim2,
            up_find_type2,
            up_feature2,
            up_lim2,
            find_target2,
            find_dir2,
            feature_name3,
            select_col3,
            rolling_width3,
            low_find_type3,
            low_feature3,
            low_lim3,
            up_find_type3,
            up_feature3,
            up_lim3,
            find_target3,
            find_dir3,
        ):
            gened_features = {}
            # global disp_col
            # print(shot)
            df = read_logger(shot)[0][:7000]
            for col in self.get_dispcol().keys():
                if not col in df.columns:
                    df[col] = eval(self.get_dispcol()[col][2])
                    """
                    execだとスタンドアローンではうまく行くが、jupyterからの実行でエラー。disp_colがnot fefined.
                    コンテキストが違う?  exec()にコンテキストを指定する方法があるようだが良くわからず。
                    恐らくeval()は、その構文がそこに書いてあるものとして評価するので、むしろeval()がふさわしい。
                    """
                    # exec_str = self.get_dispcol()[col][2]
                    # exec(exec_str)
                    # exec(self.disp_col[col][2])

            #         fig = multi_col_figure(df[['プレス荷重shift','スライド変位右','加速度左右_X_左+500G']])
            fig = go.FigureWidget(
                make_subplots(rows=self.nrows, cols=self.ncols, shared_xaxes=True, vertical_spacing=0.02, horizontal_spacing=0.05)
                #             make_subplots(rows=max(disp_col.values())+1, cols=1, shared_xaxes=True,vertical_spacing = 0.01,)
            )
            # disp_colで定義された項目を時系列グラフとして描画
            for col in self.disp_col:
                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=self.disp_col[col][0], col=self.disp_col[col][1])
            #             fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=disp_col[col]+1, col=1)

            fig.update_layout(showlegend=True, title_text="shot No.", width=1600, height=800)
            # ToDo: legendはsubplotのtitleで入れた方が見栄えが良いが、一つのsubplotに複数ある時の対応をどうするか?

            # ToDo: 今のところ、gridの1行ごとにlocate_featureが必要
            fig = self.locate_feature(
                df,
                fig,
                feature_name0,
                select_col0,
                rolling_width0,
                low_find_type0,
                low_feature0,
                low_lim0,
                up_find_type0,
                up_feature0,
                up_lim0,
                find_target0,
                find_dir0,
            )
            fig = self.locate_feature(
                df,
                fig,
                feature_name1,
                select_col1,
                rolling_width1,
                low_find_type1,
                low_feature1,
                low_lim1,
                up_find_type1,
                up_feature1,
                up_lim1,
                find_target1,
                find_dir1,
            )
            fig = self.locate_feature(
                df,
                fig,
                feature_name2,
                select_col2,
                rolling_width2,
                low_find_type2,
                low_feature2,
                low_lim2,
                up_find_type2,
                up_feature2,
                up_lim2,
                find_target2,
                find_dir2,
            )
            fig = self.locate_feature(
                df,
                fig,
                feature_name3,
                select_col3,
                rolling_width3,
                low_find_type3,
                low_feature3,
                low_lim3,
                up_find_type3,
                up_feature3,
                up_lim3,
                find_target3,
                find_dir3,
            )

            return fig

        return app


if __name__ == "__main__":
    brewFeatures = brewFeatures()
    disp_co = {}
    disp_co["プレス荷重shift"] = [1, 1, None]
    disp_co["右垂直"] = [1, 1, None]
    disp_co["スライド変位右"] = [2, 1, None]
    disp_co["スライド変位左"] = [2, 1, None]
    disp_co["F*dFdt"] = [3, 1, 'df["F*dFdt"] = df["プレス荷重shift"]*(df["プレス荷重shift"].diff() / df["time"].diff())']
    brewFeatures.set_dispcol(disp_co)
    app = brewFeatures.make_app()
    app.run_server(host="0.0.0.0", port=8048, debug=True)
