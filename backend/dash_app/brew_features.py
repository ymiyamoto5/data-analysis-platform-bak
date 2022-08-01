"""
 ==================================
  brew_features.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""
"""
export DB_SQL_ECHO=0
export SQLALCHEMY_DATABASE_URI='sqlite:////mnt/datadrive/app.db'
#export ELASTIC_URL=10.25.175.39:9200
#export ELASTIC_URL=10.25.160.104:9200
#export ELASTIC_URL=10.25.163.156:9200
#export ELASTIC_USER=elastic
#export ELASTIC_PASSWORD=P@ssw0rd
export ELASTIC_URL=10.25.163.156:9200
#export ELASTIC_URL='http://10.25.163.156:9200'  # elasticsearch 8.3.1ではscheme必須
export ELASTIC_USER=elastic
export ELASTIC_PASSWORD=1qazZAQ!

python -m backend.dash_app.brew_features
"""
import numpy as np
import pandas as pd
import plotly.express as px
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
from backend.dash_app.constants import CONTENT_STYLE, MAX_COLS, MAX_ROWS, PREPROCESS, SIDEBAR_STYLE
from backend.dash_app.preprocessors import add, calibration, diff, moving_average, mul, regression_line, shift, sub, thinning_out
from backend.elastic_manager.elastic_manager import ElasticManager
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from dash import dash_table
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from collections import OrderedDict
from pathlib import Path


def get_shot_df_from_elastic(index, shot_number, size=10000):
    """elasticsearch indexからショットデータを取得し、DataFrameとして返す"""

    query: dict = {"query": {"term": {"shot_number": {"value": shot_number}}}, "sort": {"sequential_number": {"order": "asc"}}}

    result = ElasticManager.get_docs(index=index, query=query, size=size)
    shot_df = pd.DataFrame(result)
    return shot_df


def get_shot_df_from_csv(csv_file):
    """csvファイルを読み込み、DataFrameとして返す
    TODO: 特定のCSVファイルに特化されているため、汎用化が必要
    """

    df = pd.read_csv(csv_file, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13],).rename({"CH名称": "time"}, axis=1)
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

    return df


def get_preprocess_dropdown_options():
    """演算処理のドロップダウンリストオプションを返す"""

    return [
        {"label": "", "value": ""},
        {"label": PREPROCESS.DIFF.value, "value": PREPROCESS.DIFF.name},
        {"label": PREPROCESS.ADD.value, "value": PREPROCESS.ADD.name},
        {"label": PREPROCESS.SUB.value, "value": PREPROCESS.SUB.name},
        {"label": PREPROCESS.MUL.value, "value": PREPROCESS.MUL.name},
        {"label": PREPROCESS.SHIFT.value, "value": PREPROCESS.SHIFT.name},
        {"label": PREPROCESS.CALIBRATION.value, "value": PREPROCESS.CALIBRATION.name},
        {"label": PREPROCESS.MOVING_AVERAGE.value, "value": PREPROCESS.MOVING_AVERAGE.name},
        {"label": PREPROCESS.REGRESSION_LINE.value, "value": PREPROCESS.REGRESSION_LINE.name},
        {"label": PREPROCESS.THINNING_OUT.value, "value": PREPROCESS.THINNING_OUT.name},
    ]


class brewFeatures:
    def __init__(self):
        self.nrows = 2
        self.ncols = 1
        # disp_colのdefaultの初期値をここで設定
        self.disp_col = {}
        self.disp_col["プレス荷重shift"] = [1, 1, None]
        self.disp_col["スライド変位右"] = [2, 1, None]
        # 抽出済み特徴量の "名前=>値(index)" となるdictionary。
        self.dr = None
        self.gened_features = {}

    def set_DataAccessor(self, dr):
        self.dr = dr

    def set_dispcol(self, disp_col):
        """  ToDo:
        3項目目の禁則文字チェックが必要。コーテーションとか。
        """
        """  ToDo:
        disp_colの要素を[row,col,値の変換式:Noneだったら元の項目そのまま]のまま行くとしたら、
        ほとんどの場合意味のない3項目目のNoneをユーザが書き忘れる可能性が高い。
        書き忘れると、対応の難しいバグとして現れるので、
        ここでsetする時に足りないNoneを補うとかした方が良さそう。
        その前に、この変な形のまま行くかどうかを考えるべきだが。
        """
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

    """  locate_feature()を呼ぶために必要なパラメタ群をdictに """

    def params_to_dict(
        self,
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
        params = {}
        params["feature_name"] = feature_name
        params["select_col"] = select_col
        params["rolling_width"] = rolling_width
        params["low_find_type"] = low_find_type
        params["low_feature"] = low_feature
        params["low_lim"] = low_lim
        params["up_find_type"] = up_find_type
        params["up_feature"] = up_feature
        params["up_lim"] = up_lim
        params["find_target"] = find_target
        params["find_dir"] = find_dir

        return params

    """ locate_feature()の結果(検索範囲と検索結果)をfigに描き込む
        figは既に時系列データがplotされている前提
    """

    def draw_result(
        self, fig, result, row, col,  # figオブジェクト  # 検索結果(検索範囲、検索結果(index, value))
    ):
        if "target_i" in result:
            select_col = result["select_col"]
            #            row = self.disp_col[select_col][0]
            #            col = self.disp_col[select_col][1]

            # 値域 -> 水平方向(hrect)緑網掛け
            """ ToDo: add_hrect()はY軸方向の下限と上限を指定する。下限だけ指定して上限はグラフの上限まで、というような
                都合の良い機能は無さそう。
                dataから網掛けの上限下限を決めると上下に隙間ができる。1.2倍とかでいいのか?  """
            """ low_less_ylimだけ描けない、なんでだ? """
            for hrect_key in ["low_less_ylim", "low_more_ylim", "up_less_ylim", "up_more_ylim"]:
                if hrect_key in result:
                    y_lim = result[hrect_key]
                    fig.add_hrect(y0=y_lim[0], y1=y_lim[1], line_width=0, fillcolor="green", opacity=0.2, layer="below", row=row, col=col)

            # 検索範囲 -> 垂直方向(vrect)オレンジ網掛け
            x_lim = result["x_lim"]
            fig.add_vrect(x0=x_lim[0], x1=x_lim[1], line_width=0, fillcolor="LightSalmon", opacity=0.2, layer="below", row=row, col=col)

            # 検索結果 -> 赤縦線   ToDo: 特徴量ごとに色分けしたい
            fig.add_vline(x=result["target_i"], line_color="red", row=row, col=col)

    # 特徴抽出機能のコア部   ToDo: グラフ操作を分離して特徴抽出だけを呼べるように
    def locate_feature(
        self,
        df,  # 対象データ:pandas.DataFrame
        feature_name,  # 特徴量名:str
        select_col,  # 処理対象項目:str
        rolling_width,  # 検索下限限方法:'固定' or '値域>' or '値域<' or '特徴点'
        low_find_type,  # 検索下限限特徴量名:str
        low_feature,  # 検索下限限値:int
        low_lim,  # 検出下限対象:'DPT' or 'VCT' or 'ACC'
        up_find_type,  # 検索上限方法:'固定' or '値域>' or '値域<' or '特徴点'
        up_feature,  # 検索上限特徴量名:str
        up_lim,  # 検索上限値:int
        find_target,  # 検出上限対象:'DPT' or 'VCT' or 'ACC'
        find_dir,  # ピーク方向:'MAX' or 'MIN'
    ):
        target_i = None
        result = {}
        result["feature_name"] = feature_name

        if feature_name == "" or feature_name is None:
            return result
        if select_col == "":
            return result

        x_lim = [0, 0]  # 初期値

        # 検索範囲下限(左端)の決定
        if low_find_type == "固定":
            x_lim[0] = int(low_lim)
        elif low_find_type == "値域>":  # 指定値より大きい範囲を検索して左端のindexを返す
            result["low_more_ylim"] = [float(low_lim), df[select_col].max()]
            sdf = df[(df[select_col] >= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
        elif low_find_type == "値域<":  # 指定値より小さい範囲を検索して左端のindexを返す
            result["low_less_ylim"] = [df[select_col].min(), float(low_lim)]
            sdf = df[(df[select_col] <= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
            # print('value:',x_lim)
        elif low_find_type == "特徴点":
            try:
                x_lim[0] = self.gened_features[low_feature] + int(low_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

        # 検索範囲上限(右端)の決定
        if up_find_type == "固定":
            x_lim[1] = int(up_lim)
        elif up_find_type == "値域>":  # 指定値より大きい範囲を検索して右端のindexを返す
            result["up_more_ylim"] = [float(up_lim), df[select_col].max()]
            sdf = df[(df[select_col] >= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
        elif up_find_type == "値域<":  # 指定値より小さい範囲を検索して右端のindexを返す
            result["up_less_ylim"] = [df[select_col].min(), float(up_lim)]
            sdf = df[(df[select_col] <= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
            # print('value:',x_lim)
        elif up_find_type == "特徴点":
            try:
                x_lim[1] = self.gened_features[up_feature] + int(up_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

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
            if find_dir == "MAX":
                target_i = target[x_lim[0] : x_lim[1]].idxmax()
                target_v = df[select_col][target_i]  # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == "MIN":
                target_i = target[x_lim[0] : x_lim[1]].idxmin()
                target_v = df[select_col][target_i]  # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == "RMS":
                target_i = x_lim[0]
                target_v = np.sqrt((df[select_col][x_lim[0] : x_lim[1]] ** 2).mean())
            elif find_dir == "VAR":
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0] : x_lim[1]].var()
            elif find_dir == "AMP":
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0] : x_lim[1]].max() - df[select_col][x_lim[0] : x_lim[1]].max()

        result["select_col"] = select_col
        result["x_lim"] = x_lim

        if target_i is not None:
            self.gened_features[feature_name] = target_i
            result["target_i"] = target_i  # 検索結果 インデックス
            result["target_v"] = target_v  # 検索結果 値

        return result

    def make_app(self):
        # app = JupyterDash('brewFeatures')
        app = JupyterDash("brewFeatures", external_stylesheets=[dbc.themes.CERULEAN])

        flist = self.dr.get_shot_list()

        # 画面全体のレイアウト
        main_div = html.Div(
            [
                #     dcc.Dropdown(id='shot_select',options=[{'label':'a','value':'a'},{'label':'b','value':'b'},]),
                # ショット選択
                #            dbc.Row([
                #                dbc.Col(
                #                    dcc.Dropdown(id='shot_select',value=str(flist[9]),
                #                        options=[{'label':str(f), 'value':str(f)} for f in flist[8:]]),
                #                    width=5,
                #                    style={'width':'50vw'} # viewpoint height
                #                ),
                #            ]),
                dash_table.DataTable(
                    id="setting-table",
                    data=pd.DataFrame().to_dict("records"),
                    style_table={"width": "1000px"},
                    columns=[
                        {"id": "field", "name": "フィールド"},
                        {"id": "row_number", "name": "行番号"},
                        {"id": "col_number", "name": "列番号"},
                        {"id": "rolling_width", "name": "移動平均"},
                        {"id": "preprocess", "name": "前処理"},
                        {"id": "detail", "name": "詳細"},
                    ],
                    editable=True,
                    row_deletable=True,
                ),
                # グラフ表示部
                dcc.Graph(id="graph"),
                # ショット選択
                dash_table.DataTable(
                    id="feature-table",
                    # data=pd.DataFrame().to_dict("records"),
                    data=pd.DataFrame(
                        {
                            "feature_name": ["vct_min", "breaking", ""],
                            "select_col": ["", "", ""],
                            "rolling_width": [9, 1, 1],
                            "low_find_type": ["固定", "固定", "特徴点"],
                            "low_feature": ["", "", ""],
                            "low_lim": ["1000", "1000", "1000"],
                            "up_find_type": ["固定", "固定", "特徴点"],
                            "up_feature": ["", "", ""],
                            "up_lim": ["3000", "5000", "3000"],
                            "find_target": ["VCT", "ACC", "DPT"],
                            "find_dir": ["MIN", "MAX", "MIN"],
                        }
                    ).to_dict("records"),
                    columns=[
                        {"id": "feature_name", "name": "特徴量名"},
                        {"id": "select_col", "name": "対象項目", "presentation": "dropdown"},
                        {"id": "rolling_width", "name": "移動平均範囲"},
                        {"id": "low_find_type", "name": "検索方法下限", "presentation": "dropdown"},
                        {"id": "low_feature", "name": "検索特徴名下限"},
                        {"id": "low_lim", "name": "検索下限"},
                        {"id": "up_find_type", "name": "検索方法上限", "presentation": "dropdown"},
                        {"id": "up_feature", "name": "検索特徴名上限"},
                        {"id": "up_lim", "name": "検索上限"},
                        {"id": "find_target", "name": "検索対象", "presentation": "dropdown"},
                        {"id": "find_dir", "name": "検索方向", "presentation": "dropdown"},
                    ],
                    editable=True,
                    dropdown={
                        "select_col": {"options": [{"label": i, "value": i} for i in self.disp_col.keys()]},
                        "low_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                        "up_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                        "find_target": {"options": [{"label": i, "value": i} for i in ["DPT", "VCT", "ACC"]]},
                        "find_dir": {"options": [{"label": i, "value": i} for i in ["MAX", "MIN"]]},
                    },
                    style_table={"width": "90%", "overflowX": "auto"},  # これの効果不明?
                ),
            ],
            style=CONTENT_STYLE,
        )

        side_div = html.Div(
            id="sidebar",
            children=[
                html.H3("表示設定", className="display-4"),
                html.Hr(),
                html.Div(
                    [
                        html.Label("データソースタイプ"),
                        dcc.Dropdown(
                            value="csv",
                            id="data-source-type-dropdown",
                            options=[{"label": "CSV", "value": "csv"}, {"label": "Elasticsearch", "value": "elastic"}],
                        ),
                    ]
                ),
                html.Div(
                    id="csv-file",
                    children=[
                        html.Label("ファイル"),
                        # dcc.Dropdown(id="csv-file-dropdown"),
                        dcc.Dropdown(id="csv-file-dropdown", value="2110040017_A0000.CSV"),  # 暫定
                    ],
                    style={"display": "none"},  # 暫定コメントアウト
                ),
                html.Div(
                    id="elastic-index",
                    children=[html.Label("インデックス"), dcc.Dropdown(id="elastic-index-dropdown"),],
                    style={"display": "none"},
                ),
                html.Div(
                    id="shot-number", children=[html.Label("ショット番号"), dcc.Dropdown(id="shot-number-dropdown"),], style={"display": "none"},
                ),
                html.Div(id="field", children=[html.Label("フィールド"), dcc.Dropdown(id="field-dropdown"),]),
                html.Div(
                    [
                        html.Label("グラフ行番号"),
                        dcc.Dropdown(id="row-number-dropdown", value=1, options=[r for r in range(1, MAX_ROWS + 1)],),
                        html.Label("グラフ列番号"),
                        dcc.Dropdown(id="col-number-dropdown", value=1, options=[c for c in range(1, MAX_COLS + 1)],),
                    ]
                ),
                html.Div([html.Label("移動平均"), dcc.Input(id="pre-rolling-width", value=1),]),
                html.Div([html.Label("前処理"), dcc.Dropdown(id="preprocess-dropdown", options=get_preprocess_dropdown_options()),]),
                html.Div(id="add-field", children=[html.Label("加算列"), dcc.Dropdown(id="add-field-dropdown"),], style={"display": "none"},),
                html.Div(id="sub-field", children=[html.Label("減算列"), dcc.Dropdown(id="sub-field-dropdown"),], style={"display": "none"},),
                html.Div(
                    id="mul-field",
                    children=[
                        html.Label("係数", style={"width": "100%"}),
                        dcc.Input(id="mul-field-input", type="number", min=1, max=1000, step=1),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="shift-field",
                    children=[
                        html.Label("シフト幅", style={"width": "100%"}),
                        dcc.Input(id="shift-field-input", type="number", min=-1000, max=1000, step=1),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="calibration-field",
                    children=[
                        html.Label("先頭N件", style={"width": "100%"}),
                        dcc.Input(id="calibration-field-input", type="number", min=1, max=1000, step=1),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="moving-average-field",
                    children=[
                        html.Label("ウィンドウサイズ", style={"width": "100%"}),
                        dcc.Input(id="moving-average-field-input", type="number", min=1, max=100, step=1),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="regression-line-field",
                    children=[html.Label("フィールド"), dcc.Dropdown(id="regression-line-field-dropdown"),],
                    style={"display": "none"},
                ),
                html.Div(
                    id="thinning-out-field",
                    children=[
                        html.Label("間引き幅", style={"width": "100%"}),
                        dcc.Input(id="thinning-out-field-input", type="number", min=1, max=1000, step=1),
                    ],
                    style={"display": "none"},
                ),
                dbc.Button("追加", id="add-button", n_clicks=0, style={"margin-top": "1rem"}),
            ],
            style=SIDEBAR_STYLE,
        )

        app.layout = html.Div(children=[dcc.Store(id="shot-data"), side_div, main_div])

        # callbacks #
        @app.callback(
            Output("csv-file", "style"),
            Output("csv-file-dropdown", "options"),
            Input("data-source-type-dropdown", "value"),
            # prevent_initial_call=True,   # 暫定コメント
        )
        def set_csv_file_options(data_source_type):
            """CSVファイル選択ドロップダウンのオプション設定"""

            if data_source_type == "csv":
                # TODO: CSVファイルのディレクトリパスが決め打ちのため、要修正
                # path = Path("/customer_data/ymiyamoto5-aida_A39D/private/data/aida/")
                path = Path("/Users/hao/data/ADDQ/20211004ブレークスルー/")
                flist = list(sorted(path.glob("*.CSV")))
                options = [{"label": f.name, "value": str(f)} for f in flist]
                return {}, options
            else:
                return {"display": "none"}, []

        @app.callback(
            Output("elastic-index", "style"),
            Output("elastic-index-dropdown", "options"),
            Input("data-source-type-dropdown", "value"),
            prevent_initial_call=True,
        )
        def set_elastic_index_options(data_source_type):
            """Elasticsearch index選択ドロップダウンのオプション設定"""

            if data_source_type == "elastic":
                options = [{"label": s, "value": s} for s in ElasticManager.show_indices(index="shots-*-data")["index"]]
                return {}, options
            else:
                return {"display": "none"}, []

        # Start 演算用callbacks

        @app.callback(
            Output("shot-number", "style"),
            Output("shot-number-dropdown", "options"),
            Input("elastic-index-dropdown", "value"),
            prevent_initial_call=True,
        )
        def set_shot_number_options(elastic_index):
            """ショット番号選択ドロップダウンのオプション設定"""

            if not elastic_index:
                return {"display": "none"}, []

            query: dict = {
                "collapse": {"field": "shot_number"},
                "query": {"match_all": {}},
                "_source": ["shot_number"],
                "sort": {"shot_number": {"order": "asc"}},
            }

            docs = ElasticManager.get_docs(index=elastic_index, query=query, size=10000)
            shot_numbers = [d["shot_number"] for d in docs]

            return {}, shot_numbers

        # Start 演算用callbacks

        @app.callback(
            Output("add-field", "style"),
            Output("add-field-dropdown", "value"),
            Output("add-field-dropdown", "options"),
            Input("preprocess-dropdown", "value"),
            State("field-dropdown", "options"),
            prevent_initial_call=False,  ### 暫定
        )
        def create_add_field_dropdown(preprocess, options):
            if preprocess == PREPROCESS.ADD.name:
                return {}, "", options
            else:
                return {"display": "none"}, "", []

        @app.callback(
            Output("sub-field", "style"),
            Output("sub-field-dropdown", "value"),
            Output("sub-field-dropdown", "options"),
            Input("preprocess-dropdown", "value"),
            State("field-dropdown", "options"),
            prevent_initial_call=True,
        )
        def create_sub_field_dropdown(preprocess, options):
            if preprocess == PREPROCESS.SUB.name:
                return {}, "", options
            else:
                return {"display": "none"}, "", []

        @app.callback(
            Output("mul-field", "style"),
            Output("mul-field-input", "value"),
            Input("preprocess-dropdown", "value"),
            prevent_initial_call=True,
        )
        def create_mul_field_dropdown(preprocess):
            if preprocess == PREPROCESS.MUL.name:
                return {}, ""
            else:
                return {"display": "none"}, ""

        @app.callback(
            Output("shift-field", "style"),
            Output("shift-field-input", "value"),
            Input("preprocess-dropdown", "value"),
            prevent_initial_call=True,
        )
        def create_shift_field_input(preprocess):
            if preprocess == PREPROCESS.SHIFT.name:
                return {}, ""
            else:
                return {"display": "none"}, ""

        @app.callback(
            Output("calibration-field", "style"),
            Output("calibration-field-input", "value"),
            Input("preprocess-dropdown", "value"),
            prevent_initial_call=True,
        )
        def create_calibration_field_input(preprocess):
            if preprocess == PREPROCESS.CALIBRATION.name:
                return {}, ""
            else:
                return {"display": "none"}, ""

        @app.callback(
            Output("moving-average-field", "style"),
            Output("moving-average-field-input", "value"),
            Input("preprocess-dropdown", "value"),
            prevent_initial_call=True,
        )
        def create_moving_average_field_input(preprocess):
            if preprocess == PREPROCESS.MOVING_AVERAGE.name:
                return {}, ""
            else:
                return {"display": "none"}, ""

        @app.callback(
            Output("regression-line-field", "style"),
            Output("regression-line-field-dropdown", "value"),
            Output("regression-line-field-dropdown", "options"),
            Input("preprocess-dropdown", "value"),
            State("field-dropdown", "options"),
            prevent_initial_call=True,
        )
        def create_regression_line_field_dropdown(preprocess, options):
            if preprocess == PREPROCESS.REGRESSION_LINE.name:
                return {}, "", options
            else:
                return {"display": "none"}, "", []

        @app.callback(
            Output("thinning-out-field", "style"),
            Output("thinning-out-field-input", "value"),
            Input("preprocess-dropdown", "value"),
            prevent_initial_call=True,
        )
        def create_thinning_out_field_input(preprocess):
            if preprocess == PREPROCESS.THINNING_OUT.name:
                return {}, ""
            else:
                return {"display": "none"}, ""

        # End 演算用callbacks

        @app.callback(
            Output("setting-table", "data"),
            Output("field-dropdown", "options"),
            Output("shot-data", "data"),
            Input("add-button", "n_clicks"),
            Input("shot-number-dropdown", "value"),
            Input("csv-file-dropdown", "value"),
            State("elastic-index-dropdown", "value"),
            State("setting-table", "data"),
            State("field-dropdown", "value"),
            State("field-dropdown", "options"),
            State("row-number-dropdown", "value"),
            State("col-number-dropdown", "value"),
            State("pre-rolling-width", "value"),
            State("preprocess-dropdown", "value"),
            State("add-field-dropdown", "value"),
            State("sub-field-dropdown", "value"),
            State("mul-field-input", "value"),
            State("shift-field-input", "value"),
            State("calibration-field-input", "value"),
            State("moving-average-field-input", "value"),
            State("regression-line-field-dropdown", "value"),
            State("thinning-out-field-input", "value"),
            State("shot-data", "data"),
            prevent_initial_call=True,
        )
        def add_button_clicked(
            n_clicks,
            shot_number,
            csv_file,
            elastic_index,
            rows,
            field,
            field_options,
            row_number,
            col_number,
            rolling_width,
            preprocess,
            add_field,
            sub_field,
            mul_field,
            shift_field,
            calibration_field,
            moving_average_field,
            regression_line_field,
            thinning_out_field,
            shot_data,
        ):
            """追加ボタン押下時のコールバック
            演算処理、テーブル行の追加、およびショットデータのStoreへの格納を行う
            NOTE: 複数のコールバックから同じIDの要素へのOutputを指定することはできない。つまり、同じ要素へOutputしたい処理は
                  同じコールバック内にまとめる必要がある。ctx.triggerd_idでどのUIからトリガーされたかは判断できるが、コールバック内の
                  処理が煩雑になるのは致し方ない。
            """

            # elasticsearch index選択のドロップダウンが変更されたときはデータ再読み込み。テーブルは設定済みのフィールドを引き継ぐ。
            # NOTE: 変更後に同じフィールドが存在しない場合エラーとなるが、テーブルから手動削除することによる運用回避とする。
            if ctx.triggered_id == "shot-number-dropdown" and elastic_index:
                df = get_shot_df_from_elastic(elastic_index, shot_number, size=10000)
                options = [{"label": c, "value": c} for c in df.columns]
                return rows, options, df.to_json(date_format="iso", orient="split")

            # csvファイル選択のドロップダウンが変更されたときはデータ再読み込み。テーブルは設定済みのフィールドを引き継ぐ。
            if ctx.triggered_id == "csv-file-dropdown" and csv_file:
                df = get_shot_df_from_csv(csv_file)
                options = [{"label": c, "value": c} for c in df.columns]
                return rows, options, df.to_json(date_format="iso", orient="split")

            # 追加ボタン押下時はテーブルへの行追加とフィールドドロップダウンリストに演算結果のフィールド追加を行う
            if ctx.triggered_id == "add-button":
                if shot_data:
                    df = pd.read_json(shot_data, orient="split")
                elif elastic_index:
                    df = get_shot_df_from_elastic(elastic_index, size=1)
                elif csv_file:
                    df = get_shot_df_from_csv(csv_file)

                # テーブルに追加する行データ
                new_row = {
                    "field": field,
                    "row_number": row_number,
                    "col_number": col_number,
                    "rolling_width": rolling_width,
                    "preprocess": preprocess,
                    "detail": "",
                }

                # 演算がなければ、テーブルに新しい行を追加するだけ。
                if not preprocess:
                    rows.append(new_row)
                    return rows, field_options, df.to_json(date_format="iso", orient="split")

                # ショットデータへの演算処理
                if preprocess == PREPROCESS.DIFF.name:
                    preprocessed_field = diff(df, field)
                    new_row["detail"] = "微分"
                elif preprocess == PREPROCESS.ADD.name:
                    preprocessed_field = add(df, field, add_field)
                    new_row["detail"] = f"加算行: {add_field}"
                elif preprocess == PREPROCESS.SUB.name:
                    preprocessed_field = sub(df, field, sub_field)
                    new_row["detail"] = f"減算行: {sub_field}"
                elif preprocess == PREPROCESS.MUL.name:
                    preprocessed_field = mul(df, field, mul_field)
                    new_row["detail"] = f"係数: {mul_field}"
                elif preprocess == PREPROCESS.SHIFT.name:
                    preprocessed_field = shift(df, field, shift_field)
                    new_row["detail"] = f"シフト幅: {shift_field}"
                elif preprocess == PREPROCESS.CALIBRATION.name:
                    preprocessed_field = calibration(df, field, calibration_field)
                    new_row["detail"] = f"校正: 先頭{calibration_field}件"
                elif preprocess == PREPROCESS.MOVING_AVERAGE.name:
                    preprocessed_field = moving_average(df, field, moving_average_field)
                    new_row["detail"] = f"ウィンドウサイズ: {moving_average_field}"
                elif preprocess == PREPROCESS.REGRESSION_LINE.name:
                    # TODO: モデルから切片と係数を取得してグラフ描写。実装箇所は要検討。
                    preprocessed_field = regression_line(df, field, regression_line_field)
                    new_row["detail"] = f"回帰直線: {regression_line_field}"
                elif preprocess == PREPROCESS.THINNING_OUT.name:
                    preprocessed_field = thinning_out(df, field, thinning_out_field)
                    new_row["detail"] = f"間引き幅: {thinning_out_field}"
                else:
                    preprocessed_field = df[field]

                new_field = field + preprocess
                df[new_field] = preprocessed_field

                # フィールドドロップダウンオプションに演算結果列を追加。既存のフィールドは追加しない。
                if new_field not in field_options:
                    field_options.append({"label": new_field, "value": new_field})

                rows.append(new_row)

                return rows, field_options, df.to_json(date_format="iso", orient="split")

        @app.callback(Output("feature-table", "dropdown"), [Input("setting-table", "data")])
        def callback_update_select_col(setting_data):

            ### 暫定
            dropdown = {
                "select_col": {"options": [{"label": r["field"], "value": r["field"]} for r in setting_data]},
                "low_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                "up_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                "find_target": {"options": [{"label": i, "value": i} for i in ["DPT", "VCT", "ACC"]]},
                "find_dir": {"options": [{"label": i, "value": i} for i in ["MAX", "MIN"]]},
            }
            return dropdown

        # @app.callback(
        #    Output("graph", "figure"),
        #    Input("setting-table", "data_previous"),  # 行削除を監視
        #    Input("setting-table", "data"),
        #    Input("feature-table", "data"),
        #    State("shot-data", "data"),
        #    prevent_initial_call=True,
        # )
        # def add_field_to_graph(previous_rows, rows, feature_data, shot_data):
        #    """テーブルの変更（フィールドの追加・削除）を検知し、グラフを描画する。
        #    グラフ領域はコールバックの度にテーブル内容を参照して再描画する。
        #    """
        #    print('rows:',rows)
        #    print('feature_data:',feature_data)
        #
        #    if len(rows) == 0:
        #        fig = make_subplots()
        #        return fig
        #
        #    df = pd.read_json(shot_data, orient="split")
        #
        #    max_row_number = max([r["row_number"] for r in rows])
        #    max_col_number = max([r["col_number"] for r in rows])
        #
        #    # M行N列のグラフ領域
        #    fig = make_subplots(rows=max_row_number, cols=max_col_number, shared_xaxes=True, vertical_spacing=0.02, horizontal_spacing=0.05)
        #
        #    # グラフの数だけループ
        #    for m in range(1, max_row_number + 1):
        #        for n in range(1, max_col_number + 1):
        #            for row in rows:
        #                # 入力で指定した（テーブルに記録されている）行列番号と一致する場合、当該位置のグラフに追加表示
        #                if row["row_number"] == m and row["col_number"] == n:
        #                    display_row = row["field"] + row["preprocess"] if row["preprocess"] else row["field"]
        #                    fig.add_trace(go.Scatter(x=df.index, y=df[display_row], name=display_row), row=m, col=n)
        #
        #    fig.update_layout(width=1300, height=600)
        #
        #    for f in feature_data:
        #        for r in rows:
        #            if f['col'] == r['field']:
        #                x_lim = [int(f['low_lim']),int(f['up_lim'])]
        #                fig.add_vrect(x0=x_lim[0],x1=x_lim[1],line_width=0, fillcolor="LightSalmon", opacity=0.2,layer='below', row=r['row_number'],col=r['col_number'])
        #
        #
        #    return fig

        # 波形グラフ描画のためのcallback関数。ショット選択及び下部のgridに含まれる入力フォームを全てobserveしている。
        # つまり入力フォームのいずれかが書き変わると必ずfigオブジェクト全体を再生成して置き換えている。
        """ ToDo: 入力フォーム操作で再描画時にzoom/panがリセットされる; relayoutDataの維持 """

        @app.callback(
            #     dash.dependencies.Output('graph', 'figure'),
            Output("graph", "figure"),
            [Input("setting-table", "data"), Input("feature-table", "data"), Input("shot-data", "data"),],
        )
        def callback_figure(setting_data, feature_data, shot_data):
            if len(setting_data) == 0:
                return go.FigureWidget()
            #                return None
            df = pd.read_json(shot_data, orient="split")
            # print(df.columns)

            max_row_number = max([r["row_number"] for r in setting_data])
            max_col_number = max([r["col_number"] for r in setting_data])

            fig = go.FigureWidget(
                # make_subplots(rows=self.nrows, cols=self.ncols, shared_xaxes=True,vertical_spacing = 0.03,horizontal_spacing=0.05)
                make_subplots(rows=max_row_number, cols=max_col_number, vertical_spacing=0.02, horizontal_spacing=0.05)
            )
            fig.update_xaxes(matches="x")

            for r in setting_data:
                if r["preprocess"] is None:
                    col = r["field"]
                else:
                    col = r["field"] + r["preprocess"]
                rw = int(r["rolling_width"])
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[col].rolling(rw, center=True).mean(), name=col), row=r["row_number"], col=r["col_number"]
                )

            for f in feature_data:
                result = self.locate_feature(
                    df,
                    f["feature_name"],
                    f["select_col"],
                    f["rolling_width"],
                    f["low_find_type"],
                    f["low_feature"],
                    f["low_lim"],
                    f["up_find_type"],
                    f["up_feature"],
                    f["up_lim"],
                    f["find_target"],
                    f["find_dir"],
                )
                # print(result)
                for r in setting_data:
                    if f["select_col"] == r["field"]:
                        self.draw_result(fig, result, r["row_number"], r["col_number"])

            return fig

        #        @app.callback(
        #    #     dash.dependencies.Output('graph', 'figure'),
        #            Output('graph', 'figure'),
        #            [Input('shot_select', 'value'),Input('feature-table','data'),
        #            ])
        #        def callback_figure(shot,feature_data
        #                ):
        #            #print(feature_data)
        #            #print(shot)
        #            #df = read_logger(shot)[0][:7000]    ##############################
        #            df = self.dr.read_logger(shot)[:7000]   ##### こっちは[0]が無い　　!!!注意!!!  ######
        #            for col in self.get_dispcol().keys():
        #                if not col in df.columns:
        #                    df[col] = eval(self.get_dispcol()[col][2])
        #                    '''
        #                    execだとスタンドアローンではうまく行くが、jupyterからの実行でエラー。disp_colがnot fefined.
        #                    コンテキストが違う?  exec()にコンテキストを指定する方法があるようだが良くわからず。
        #                    恐らくeval()は、その構文がそこに書いてあるものとして評価するので、むしろeval()がふさわしい。
        #                    '''
        #                    #exec_str = self.get_dispcol()[col][2]
        #                    #exec(exec_str)
        #                    #exec(self.disp_col[col][2])
        #
        #    #         fig = multi_col_figure(df[['プレス荷重shift','スライド変位右','加速度左右_X_左+500G']])
        #            '''
        #            make_subplots(shared_xaxes=True)X軸連動の対象は同じcol同志のみ。複数colある場合は縦に並んだsubplotだけが連動する。
        #            update_xaxes(matches='x')で連動させた場合は全てのsubplotが連動。
        #            shared_xaxes=Trueとupdate_xaxes(matches='x')は同じ機能にアクセスするAPIだとの議論もあるが、
        #            試した範囲では動作が異なる。バグか?
        #            https://github.com/plotly/plotly.py/issues/775
        #            https://community.plotly.com/t/shared-x-axis-with-sub-and-side-by-side-plots-and-click-events-in-html-output-file/34613
        #            '''
        #            # make_subplots()はgo.Figureインスタンスを生成。go.FigureWidgetはgo.Figureの継承クラスで、
        #            # go.Figureインスタンスを引数にコンストラクタを呼ぶとsubplot化されたgo.FigureWidgetインスタンスになる。
        #            fig = go.FigureWidget(
        #                #make_subplots(rows=self.nrows, cols=self.ncols, shared_xaxes=True,vertical_spacing = 0.03,horizontal_spacing=0.05)
        #                make_subplots(rows=self.nrows, cols=self.ncols, vertical_spacing = 0.04,horizontal_spacing=0.05)
        #            )
        #            fig.update_xaxes(matches='x')
        #
        #            # disp_colで定義された項目を時系列グラフとして描画
        #            for col in self.disp_col:
        #                ''' ToDo: 要検討 このスコープのdfにはread_logger()で読んだ項目全て含まれてるので「表示しない項目」を考慮する必要無し? '''
        ##                if self.disp_col[col][0] == 0:  # disp_col['time'] = [0,0,None] と定義されてたら表示対象外
        ##                    continue
        #                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=self.disp_col[col][0], col=self.disp_col[col][1])
        #    #             fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=disp_col[col]+1, col=1)
        #
        #            '''
        #            matplotlibのsubplotでは、各subplotがそれぞれaxであるため、そのaxに対する操作が、
        #            非subplot環境、つまりfigure全体がaxである場合と同様に行えるようになっているのだが、
        #            そういった考え方がplotlyには無く、subplotはただ単にfigureを分割したものになっている。
        #            そのため、subplotごとにlegendを描く、という発想が無い。
        #            legendgroupという機能があり、複数データ系列のlegendをグルーピングすることができるが、
        #            これはsubplotとは無関係、あくまでlegend描画エリアの中でグルーピングし、
        #            そのグループ間のgapが指定可能(legend_tracegroupgap)になっているだけ。
        #            legend描画エリアはgo.Figureの中に一つだけだ。
        #            '''
        #            fig.update_layout(showlegend=True, title_text='shot No.', width=1600,height=800)
        #            # ToDo: legendはsubplotのtitleで入れた方が見栄えが良いが、一つのsubplotに複数ある時の対応をどうするか?
        #
        #            for f in feature_data:
        #                result = self.locate_feature(df,
        #                    f['feature_name'],f['select_col'], f['rolling_width'],
        #                    f['low_find_type'],f['low_feature'],f['low_lim'],
        #                    f['up_find_type'],f['up_feature'],f['up_lim'],
        #                    f['find_target'],f['find_dir'])
        #                #print(result)
        #                self.draw_result(fig,result)
        #
        #            return fig

        return app


if __name__ == "__main__":
    # from data_accessor import DataAccessor
    from backend.dash_app.data_accessor import DataAccessor

    # brewFeaturesインスタンスを生成
    brewFeatures = brewFeatures()
    # DataAccessorインスタンスを生成してbrewFeaturesにセット
    brewFeatures.set_DataAccessor(DataAccessor())
    # disp_colをoverrideすることで、グラフ表示をカスタマイズ
    # disp_colはDataAccessor側にあるべきか?
    disp_co = {}
    # "time"項目は表示対象外だが、微分する時に必要。DataAccessorで必ず"time"項目を作るという決まりにする?
    # disp_co['time'] = [0,0,None]    # plotlyのsubplotのrow,colは0 originではないので0,0は存在しない
    disp_co["プレス荷重shift"] = [1, 1, None]
    disp_co["右垂直"] = [1, 1, None]
    disp_co["スライド変位右"] = [2, 1, None]
    disp_co["スライド変位左"] = [1, 2, None]
    disp_co["F*dFdt"] = [3, 1, 'df["プレス荷重shift"]*(df["プレス荷重shift"].diff() / df["time"].diff())']
    brewFeatures.set_dispcol(disp_co)
    # サーバ実行
    app = brewFeatures.make_app()
    # JupyterDashでは今のところ0.0.0.0にbindできない
    app.run_server(host="0.0.0.0", port=8048, debug=True)
