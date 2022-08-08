"""
 ==================================
  brew_features.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

import os
from itertools import groupby
from typing import List

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.graph_objs as go
from backend.common.common_logger import logger
from backend.dash_app.constants import (
    CONTENT_STYLE,
    DATA_SOURCE_TYPE,
    FIND_DIR,
    FIND_TARGET,
    FIND_TYPE,
    MAX_COLS,
    MAX_ROWS,
    PREPROCESS,
    SIDEBAR_STYLE,
)
from backend.dash_app.data_accessor import CsvDataAccessor, ElasticDataAccessor
from backend.dash_app.preprocessors import add, calibration, diff, mul, regression_line, shift, sub, thinning_out
from dash import Input, Output, State, ctx, dash_table, dcc, html
from jupyter_dash import JupyterDash
from pandas.core.frame import DataFrame
from plotly.subplots import make_subplots


def get_data_source_type_dropdown_options():
    """データソースタイプのドロップダウンリストオプションを返す"""

    return [
        {"label": DATA_SOURCE_TYPE.CSV.name, "value": DATA_SOURCE_TYPE.CSV.name},
        {"label": DATA_SOURCE_TYPE.ELASTIC.name, "value": DATA_SOURCE_TYPE.ELASTIC.name},
    ]


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
        {"label": PREPROCESS.REGRESSION_LINE.value, "value": PREPROCESS.REGRESSION_LINE.name},
        {"label": PREPROCESS.THINNING_OUT.value, "value": PREPROCESS.THINNING_OUT.name},
    ]


class BrewFeatures:
    def __init__(self, csv_data_accessor: CsvDataAccessor):
        self.gened_features: dict = {}
        self.csv_data_accessor = csv_data_accessor

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
        """locate_feature()を呼ぶために必要なパラメタ群をdictに"""

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

    def draw_result(
        self,
        fig,
        result,
        row,
        col,  # figオブジェクト  # 検索結果(検索範囲、検索結果(index, value))
    ):
        """locate_feature()の結果(検索範囲と検索結果)をfigに描き込む
        figは既に時系列データがplotされている前提
        """

        if "target_i" in result:

            # 値域 -> 水平方向(hrect)緑網掛け
            """ToDo: add_hrect()はY軸方向の下限と上限を指定する。下限だけ指定して上限はグラフの上限まで、というような
            都合の良い機能は無さそう。
            dataから網掛けの上限下限を決めると上下に隙間ができる。1.2倍とかでいいのか?"""
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
        df: DataFrame,  # 対象データ
        feature_name: str,  # 特徴量名
        select_col: str,  # 処理対象項目
        rolling_width: str,  # 検索下限限方法:'固定' or '値域>' or '値域<' or '特徴点'
        low_find_type: str,  # 検索下限限特徴量名
        low_feature: int,  # 検索下限限値
        low_lim: str,  # 検出下限対象:'DPT' or 'VCT' or 'ACC'
        up_find_type: str,  # 検索上限方法:'固定' or '値域>' or '値域<' or '特徴点'
        up_feature: str,  # 検索上限特徴量名
        up_lim: int,  # 検索上限値
        find_target: str,  # 検出上限対象:'DPT' or 'VCT' or 'ACC'
        find_dir: str,  # ピーク方向:'MAX' or 'MIN'
    ):
        target_i = None
        result: dict = {}
        result["feature_name"] = feature_name

        # 特徴量名が空白 or 未入力、対象項目未選択の場合は空のresultを返す
        if feature_name == "" or feature_name is None:
            return result
        if select_col == "":
            return result

        x_lim = [0, 0]  # 初期値

        # 検索範囲下限(左端)の決定
        if low_find_type == FIND_TYPE.FIX.value:
            x_lim[0] = int(low_lim)
        elif low_find_type == FIND_TYPE.RANGE_MORE.value:  # 指定値より大きい範囲を検索して左端のindexを返す
            result["low_more_ylim"] = [float(low_lim), df[select_col].max()]
            sdf = df[(df[select_col] >= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
        elif low_find_type == FIND_TYPE.RANGE_LESS.value:  # 指定値より小さい範囲を検索して左端のindexを返す
            result["low_less_ylim"] = [df[select_col].min(), float(low_lim)]
            sdf = df[(df[select_col] <= float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
            # print('value:',x_lim)
        elif low_find_type == FIND_TYPE.FEATURE_POINT.value:
            try:
                x_lim[0] = self.gened_features[low_feature] + int(low_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

        # 検索範囲上限(右端)の決定
        if up_find_type == FIND_TYPE.FIX.value:
            x_lim[1] = int(up_lim)
        elif up_find_type == FIND_TYPE.RANGE_MORE.value:  # 指定値より大きい範囲を検索して右端のindexを返す
            result["up_more_ylim"] = [float(up_lim), df[select_col].max()]
            sdf = df[(df[select_col] >= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
        elif up_find_type == FIND_TYPE.RANGE_LESS.value:  # 指定値より小さい範囲を検索して右端のindexを返す
            result["up_less_ylim"] = [df[select_col].min(), float(up_lim)]
            sdf = df[(df[select_col] <= float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
            # print('value:',x_lim)
        elif up_find_type == FIND_TYPE.FEATURE_POINT.value:
            try:
                x_lim[1] = self.gened_features[up_feature] + int(up_lim)
                # , gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print("Error")

        # 検索対象時系列データの生成
        if find_target == FIND_TARGET.DPT.value:
            target = df[select_col]
        elif find_target == FIND_TARGET.VCT.value:
            target = df[select_col].rolling(int(rolling_width), center=True).mean().diff()
        elif find_target == FIND_TARGET.ACC.value:
            target = (
                df[select_col].rolling(int(rolling_width), center=True).mean().diff().rolling(int(rolling_width), center=True).mean().diff()
            )
        if x_lim[1] - x_lim[0] > 0:  # 検索範囲が適切に指定されてなければ何もしない  ToDo:「何もしない」ことのフィードバック? 範囲指定せずに検索したい時もある
            if find_dir == FIND_DIR.MAX.value:
                target_i = target[x_lim[0] : x_lim[1]].idxmax()
                target_v = df[select_col][target_i]  # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == FIND_DIR.MIN.value:
                target_i = target[x_lim[0] : x_lim[1]].idxmin()
                target_v = df[select_col][target_i]  # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == FIND_DIR.RMS.value:
                target_i = x_lim[0]
                target_v = np.sqrt((df[select_col][x_lim[0] : x_lim[1]] ** 2).mean())
            elif find_dir == FIND_DIR.VAR.value:
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0] : x_lim[1]].var()
            elif find_dir == FIND_DIR.AMP.value:
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0] : x_lim[1]].max() - df[select_col][x_lim[0] : x_lim[1]].max()

        result["select_col"] = select_col
        result["x_lim"] = x_lim

        if target_i is not None:
            self.gened_features[feature_name] = target_i
            result["target_i"] = target_i  # 検索結果 インデックス
            result["target_v"] = target_v  # 検索結果 値

        return result

    def get_flatten_features_list(self, features_list: List[dict]) -> List[dict]:
        """ショット毎に特徴量をフラットに持つ辞書のリストを返す"""

        # ショット毎・特徴量毎のリスト
        tmp = [
            {
                "condition_name": features["condition_name"],
                "shot_number": features["shot_number"],
                f"{feature['feature_name']}_index": feature["target_i"],
                f"{feature['feature_name']}_value": feature["target_v"],
            }
            for features in features_list
            for feature in features["features"]
            if feature["feature_name"] and ("target_i" in feature) and ("target_v" in feature)
        ]

        # ショット番号でグループ化
        res = []
        for k, g in groupby(tmp, lambda f: f["shot_number"]):  # type: ignore
            d = {}
            for i in g:
                d.update(i)
            res.append(d)

        return res

    def make_app(self):
        app = JupyterDash("BrewFeatures", external_stylesheets=[dbc.themes.BOOTSTRAP])

        # 画面全体のレイアウト
        main_div = html.Div(
            [
                dash_table.DataTable(
                    id="setting-table",
                    data=pd.DataFrame().to_dict("records"),
                    columns=[
                        {"id": "field", "name": "フィールド"},
                        {"id": "row_number", "name": "行番号"},
                        {"id": "col_number", "name": "列番号"},
                        {"id": "rolling_width", "name": "移動平均"},
                        {"id": "original_field", "name": "ソースフィールド"},
                        {"id": "preprocess", "name": "前処理"},
                        {"id": "detail", "name": "詳細"},
                    ],
                    editable=True,
                    row_deletable=True,
                    # NOTE: https://github.com/plotly/dash-table/issues/221
                    css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
                ),
                # グラフ表示部
                dcc.Graph(id="graph"),
                dash_table.DataTable(
                    id="feature-table",
                    data=pd.DataFrame(
                        {
                            "feature_name": ["vct_min", "breaking", "", "", ""],
                            "select_col": ["", "", "", "", ""],
                            "rolling_width": [9, 1, 1, 1, 1],
                            "low_find_type": ["固定", "特徴点", "特徴点", "", ""],
                            "low_feature": ["", "vct_min", "", "", ""],
                            "low_lim": ["1000", "-100", "1000", "0", "0"],
                            "up_find_type": ["固定", "特徴点", "特徴点", "", ""],
                            "up_feature": ["", "vct_min", "", "", ""],
                            "up_lim": ["3000", "0", "3000", "0", "0"],
                            "find_target": ["VCT", "ACC", "DPT", "DPT", "DPT"],
                            "find_dir": ["MIN", "MIN", "MIN", "MAX", "MAX"],
                        }
                    ).to_dict("records"),
                    columns=[
                        {"id": "feature_name", "name": "特徴量名"},
                        {"id": "select_col", "name": "対象項目", "presentation": "dropdown"},
                        {"id": "rolling_width", "name": "移動平均範囲"},
                        {"id": "low_find_type", "name": "検索方法下限", "presentation": "dropdown"},
                        {"id": "low_feature", "name": "検索特徴名下限", "presentation": "dropdown"},
                        {"id": "low_lim", "name": "検索下限"},
                        {"id": "up_find_type", "name": "検索方法上限", "presentation": "dropdown"},
                        {"id": "up_feature", "name": "検索特徴名上限", "presentation": "dropdown"},
                        {"id": "up_lim", "name": "検索上限"},
                        {"id": "find_target", "name": "検索対象", "presentation": "dropdown"},
                        {"id": "find_dir", "name": "検索方向", "presentation": "dropdown"},
                    ],
                    editable=True,
                    row_selectable="multi",
                    dropdown={
                        "select_col": {"options": [{"label": i, "value": i} for i in [""]]},
                        "low_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                        "up_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                        "find_target": {"options": [{"label": i, "value": i} for i in ["DPT", "VCT", "ACC"]]},
                        "find_dir": {"options": [{"label": i, "value": i} for i in ["MAX", "MIN"]]},
                    },
                    css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],
                ),
            ],
            style=CONTENT_STYLE,
        )

        side_div = html.Div(
            id="sidebar",
            children=[
                html.H4("表示設定", className="display-5"),
                html.Hr(),
                html.Div(
                    [
                        html.Label("データソースタイプ"),
                        dcc.Dropdown(
                            id="data-source-type-dropdown",
                            options=get_data_source_type_dropdown_options(),
                        ),
                    ]
                ),
                html.Div(
                    id="csv-file",
                    children=[
                        html.Label("ファイル"),
                        dcc.Dropdown(id="csv-file-dropdown"),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="elastic-index",
                    children=[
                        html.Label("インデックス"),
                        dcc.Dropdown(id="elastic-index-dropdown"),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="shot-number",
                    children=[
                        html.Label("ショット番号"),
                        dcc.Dropdown(id="shot-number-dropdown"),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="field",
                    children=[
                        html.Label("フィールド"),
                        dcc.Dropdown(id="field-dropdown"),
                    ],
                ),
                html.Div(
                    [
                        html.Label("グラフ行番号"),
                        dcc.Dropdown(
                            id="row-number-dropdown",
                            value=1,
                            options=[r for r in range(1, MAX_ROWS + 1)],
                        ),
                        html.Label("グラフ列番号"),
                        dcc.Dropdown(
                            id="col-number-dropdown",
                            value=1,
                            options=[c for c in range(1, MAX_COLS + 1)],
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("移動平均"),
                        dcc.Input(id="pre-rolling-width", value=1),
                    ]
                ),
                html.Div(
                    [
                        html.Label("前処理"),
                        dcc.Dropdown(id="preprocess-dropdown", options=get_preprocess_dropdown_options()),
                    ]
                ),
                html.Div(
                    id="add-field",
                    children=[
                        html.Label("加算列"),
                        dcc.Dropdown(id="add-field-dropdown"),
                    ],
                    style={"display": "none"},
                ),
                html.Div(
                    id="sub-field",
                    children=[
                        html.Label("減算列"),
                        dcc.Dropdown(id="sub-field-dropdown"),
                    ],
                    style={"display": "none"},
                ),
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
                    id="regression-line-field",
                    children=[
                        html.Label("フィールド"),
                        dcc.Dropdown(id="regression-line-field-dropdown"),
                    ],
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
                dbc.Button("追加", id="add-button", n_clicks=0, style={"margin-top": "1rem", "float": "right"}),
                html.Br(),
                html.H4("出力設定", className="display-5", style={"margin-top": "3rem"}),
                html.Hr(),
                html.Div(
                    id="export-setting",
                    children=[
                        html.Label("抽出条件名"),
                        dcc.Input(id="condition-name-input", type="text"),
                        dbc.Button(
                            "全ショット適用", id="apply-all-shot-button", n_clicks=0, style={"margin-top": "1rem", "float": "right"}, disabled=True
                        ),
                    ],
                ),
            ],
            style=SIDEBAR_STYLE,
        )

        other_div = html.Div(
            id="other",
            children=[
                dcc.Loading(id="loading", type="default", children=html.Div(id="loading-output"), fullscreen=True),
                dbc.Modal(
                    [
                        dbc.ModalFooter(dbc.Button("Close", id="close", className="ml-auto")),
                    ],
                    size="xl",
                    id="apply-result-modal",
                    is_open=False,
                ),
            ],
        )

        app.layout = html.Div(children=[side_div, main_div, other_div])

        @app.callback(
            Output("csv-file", "style"),
            Output("csv-file-dropdown", "options"),
            Input("data-source-type-dropdown", "value"),
            prevent_initial_call=True,
        )
        def set_csv_file_options(data_source_type):
            """CSVファイル選択ドロップダウンのオプション設定"""

            if data_source_type == DATA_SOURCE_TYPE.CSV.name:
                flist = self.csv_data_accessor.get_flist()
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

            if data_source_type == DATA_SOURCE_TYPE.ELASTIC.name:
                options = [{"label": i, "value": i} for i in ElasticDataAccessor.get_indices()]
                return {}, options
            else:
                return {"display": "none"}, []

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

            shot_numbers = ElasticDataAccessor.get_shot_list(elastic_index)

            return {}, shot_numbers

        # Start 演算用callbacks

        @app.callback(
            Output("add-field", "style"),
            Output("add-field-dropdown", "value"),
            Output("add-field-dropdown", "options"),
            Input("preprocess-dropdown", "value"),
            State("field-dropdown", "options"),
            prevent_initial_call=False,
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
            State("regression-line-field-dropdown", "value"),
            State("thinning-out-field-input", "value"),
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
            regression_line_field,
            thinning_out_field,
        ):
            """追加ボタン押下時のコールバック
            NOTE: 複数のコールバックから同じIDの要素へのOutputを指定することはできない。つまり、同じ要素へOutputしたい処理は
                  同じコールバック内にまとめる必要がある。ctx.triggerd_idでどのUIからトリガーされたかは判断できるが、コールバック内の
                  処理が煩雑になるのは致し方ない。
            """

            # TODO: データソースを変更した場合

            # ショット番号選択ドロップダウンが変更されたときはオプション再設定。テーブルは設定済みのフィールドを引き継ぐ。
            # NOTE: 変更後に同じフィールドが存在しない場合エラーとなるが、テーブルから手動削除することによる運用回避とする。
            if ctx.triggered_id == "shot-number-dropdown" and elastic_index:
                # TODO: フィールドのみ取得
                df = ElasticDataAccessor.get_shot_df(elastic_index, shot_number, size=1)
                options = [{"label": c, "value": c} for c in df.columns]
                return rows, options

            # csvファイル選択のドロップダウンが変更されたときはデータ再読み込み。テーブルは設定済みのフィールドを引き継ぐ。
            if ctx.triggered_id == "csv-file-dropdown" and csv_file:
                df = self.csv_data_accessor.get_shot_df(csv_file)
                options = [{"label": c, "value": c} for c in df.columns]
                return rows, options

            # 追加ボタン押下時はテーブルへの行追加とフィールドドロップダウンリストに演算結果のフィールド追加を行う
            if ctx.triggered_id == "add-button":
                if elastic_index:
                    # TODO: フィールドのみ取得
                    df = ElasticDataAccessor.get_shot_df(elastic_index, shot_number, size=1)
                elif csv_file:
                    df = self.csv_data_accessor.get_shot_df(csv_file)

                # テーブルに追加する行データ
                new_row = {
                    "field": field,
                    "row_number": row_number,
                    "col_number": col_number,
                    "rolling_width": rolling_width,
                    "original_field": field,
                    "preprocess": preprocess,
                    "detail": "",
                    "parameter": "",
                }

                # 演算がなければ、テーブルに新しい行を追加するだけ。
                if not preprocess:
                    rows.append(new_row)
                    return rows, field_options

                # ショットデータへの演算処理
                if preprocess == PREPROCESS.DIFF.name:
                    new_row["detail"] = "微分"
                    parameter = ""
                elif preprocess == PREPROCESS.ADD.name:
                    new_row["detail"] = f"加算行: {add_field}"
                    parameter = add_field
                elif preprocess == PREPROCESS.SUB.name:
                    new_row["detail"] = f"減算行: {sub_field}"
                    parameter = sub_field
                elif preprocess == PREPROCESS.MUL.name:
                    new_row["detail"] = f"係数: {mul_field}"
                    parameter = mul_field
                elif preprocess == PREPROCESS.SHIFT.name:
                    new_row["detail"] = f"シフト幅: {shift_field}"
                    parameter = shift_field
                elif preprocess == PREPROCESS.CALIBRATION.name:
                    new_row["detail"] = f"校正: 先頭{calibration_field}件"
                    parameter = calibration_field
                elif preprocess == PREPROCESS.REGRESSION_LINE.name:
                    # TODO: モデルから切片と係数を取得してグラフ描写。実装箇所は要検討。
                    new_row["detail"] = f"回帰直線: {regression_line_field}"
                    parameter = regression_line_field
                elif preprocess == PREPROCESS.THINNING_OUT.name:
                    new_row["detail"] = f"間引き幅: {thinning_out_field}"
                    parameter = thinning_out_field

                new_row["parameter"] = parameter
                new_field = f"{field}_{preprocess}_{parameter}" if parameter else f"{field}_{preprocess}"
                new_row["field"] = new_field

                # フィールドドロップダウンオプションに演算結果列を追加。既存のフィールドは追加しない。
                if new_field not in field_options:
                    field_options.append({"label": new_field, "value": new_field})

                rows.append(new_row)

                return rows, field_options

        @app.callback(
            Output("feature-table", "dropdown"),
            [
                Input("setting-table", "data"),
                Input("feature-table", "data"),
            ],
        )
        def callback_update_select_col(setting_data, feature_data):
            feature_opt = {"options": [{"label": f["feature_name"], "value": f["feature_name"]} for f in feature_data]}
            # 暫定
            dropdown = {
                "select_col": {"options": [{"label": r["field"], "value": r["field"]} for r in setting_data]},
                "low_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                "low_feature": feature_opt,
                "up_find_type": {"options": [{"label": i, "value": i} for i in ["固定", "値域<", "値域>", "特徴点"]]},
                "up_feature": feature_opt,
                "find_target": {"options": [{"label": i, "value": i} for i in ["DPT", "VCT", "ACC"]]},
                "find_dir": {"options": [{"label": i, "value": i} for i in ["MAX", "MIN"]]},
            }
            return dropdown

        def exec_preprocess(df, setting_data):
            """設定テーブルに指定された前処理を実行し、処理済みのDataFrameを返す"""
            for r in setting_data:
                field = r["field"]
                preprocess = r["preprocess"]
                if preprocess:
                    org_field = r["original_field"]
                    parameter = r["parameter"]

                    if preprocess == PREPROCESS.DIFF.name:
                        df[field] = diff(df, org_field)
                    elif preprocess == PREPROCESS.ADD.name:
                        df[field] = add(df, org_field, parameter)
                    elif preprocess == PREPROCESS.SUB.name:
                        df[field] = sub(df, org_field, parameter)
                    elif preprocess == PREPROCESS.MUL.name:
                        df[field] = mul(df, org_field, parameter)
                    elif preprocess == PREPROCESS.SHIFT.name:
                        df[field] = shift(df, org_field, int(parameter))
                    elif preprocess == PREPROCESS.CALIBRATION.name:
                        df[field] = calibration(df, org_field, parameter)
                    elif preprocess == PREPROCESS.REGRESSION_LINE.name:
                        df[field] = regression_line(df, org_field, parameter)
                    elif preprocess == PREPROCESS.THINNING_OUT.name:
                        df[field] = thinning_out(df, org_field, int(parameter))
                # 移動平均は前処理有無に関わらず適用する
                rw = int(r["rolling_width"])
                if rw > 1:
                    df[field] = df[field].rolling(rw, center=True).mean()
            return df

        def extract_features(df, feature_data):
            """特徴量検索"""
            # feature_rowsは特徴量記述テーブルの選択行番号であり、特徴量描画の有無を指定しており、
            # 特徴量抽出結果の len(result_data) と len(feature_data) は一致してなければならない。
            # ここで、空のresultを間引いたりするべからず。
            result_data = []
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
                result_data.append(result)
            return result_data

        @app.callback(
            Output("graph", "figure"),
            [
                Input("shot-number-dropdown", "value"),
                Input("csv-file-dropdown", "value"),
                State("elastic-index-dropdown", "value"),
                Input("setting-table", "data"),
                Input("feature-table", "data"),
                Input("feature-table", "selected_rows"),  # [2,0] チェックした順番が維持される
            ],
        )
        def callback_figure(shot_number, csv_file, elastic_index, setting_data, feature_data, feature_rows):
            """波形グラフ描画のためのcallback関数。ショット選択及び下部のgridに含まれる入力フォームを全てobserveしている。
            つまり入力フォームのいずれかが書き変わると必ずfigオブジェクト全体を再生成して置き換えている。
            ToDo: 入力フォーム操作で再描画時にzoom/panがリセットされる; relayoutDataの維持"""

            """表示位置設定が空なら空のfigureオブジェクトを返す"""
            if len(setting_data) == 0:
                return go.FigureWidget()

            """ 入力データ """
            if elastic_index:
                df = ElasticDataAccessor.get_shot_df(elastic_index, shot_number, size=10000)
            if csv_file:
                df = self.csv_data_accessor.get_shot_df(csv_file)

            # 前処理
            preprocessed_df = exec_preprocess(df, setting_data)
            # 特徴抽出
            features = extract_features(preprocessed_df, feature_data)

            """ subplot """
            max_row_number = max([int(r["row_number"]) for r in setting_data])
            max_col_number = max([int(r["col_number"]) for r in setting_data])

            fig = go.FigureWidget(make_subplots(rows=max_row_number, cols=max_col_number, vertical_spacing=0.02, horizontal_spacing=0.05))
            fig.update_xaxes(matches="x")

            """ 波形グラフ描画 """
            for r in setting_data:
                field = r["field"]
                fig.add_trace(
                    go.Scatter(x=df.index, y=df[field], name=field),
                    row=int(r["row_number"]),
                    col=int(r["col_number"]),
                )

            for feature in np.array(features)[feature_rows]:
                for r in setting_data:
                    if "select_col" in feature:
                        if feature["select_col"] == r["field"]:
                            self.draw_result(fig, feature, r["row_number"], r["col_number"])

            fig.update_layout(width=1300, height=600)  # TODO: 相対サイズ指定?
            return fig

        @app.callback(
            Output("apply-all-shot-button", "disabled"),
            Input("condition-name-input", "value"),
            prevent_initial_call=True,
        )
        def enalbe_apply_button(condition_name):
            """抽出条件名が入力されていれば、全ショット適用を有効化する"""
            if condition_name:
                return False
            return True

        @app.callback(
            Output("loading", "children"),
            Input("apply-all-shot-button", "n_clicks"),
            State("data-source-type-dropdown", "value"),
            State("elastic-index-dropdown", "value"),
            State("setting-table", "data"),
            State("feature-table", "data"),
            State("condition-name-input", "value"),
            prevent_initial_call=True,
        )
        def apply_all_shot(n_clicks, data_source_type, elastic_index, setting_data, feature_data, condition_name):
            """特徴量抽出の全ショット適用"""

            # 全ショット適用
            if data_source_type == DATA_SOURCE_TYPE.ELASTIC.name:
                shot_numbers = ElasticDataAccessor.get_shot_list(elastic_index)
                features_list = []
                logger.info("Begin feature extract.")
                for shot_number in shot_numbers:
                    logger.info(f"shot_number: {shot_number}")
                    df = ElasticDataAccessor.get_shot_df(elastic_index, shot_number, size=10000)
                    preprocessed_df = exec_preprocess(df, setting_data)
                    features = extract_features(preprocessed_df, feature_data)
                    features_dict = {"condition_name": condition_name, "shot_number": shot_number, "features": features}
                    features_list.append(features_dict)
                logger.info("End feature extract.")
                features_index = elastic_index.replace("data", "features")
                analysis_index = elastic_index.replace("data", "analysis")
            elif data_source_type == DATA_SOURCE_TYPE.CSV.name:
                flist = self.csv_data_accessor.get_flist()
                features_list = []
                logger.info("Begin feature extract.")
                # NOTE: 1CSVファイルにつき1ショット、1番からの連番が前提
                for shot_number, f in enumerate(flist, 1):
                    logger.info(f"file: {f}")
                    df = self.csv_data_accessor.get_shot_df(f)
                    # ショット取得に失敗したらdfはNoneとしている。
                    if df is None:
                        continue
                    preprocessed_df = exec_preprocess(df, setting_data)
                    features = extract_features(preprocessed_df, feature_data)
                    features_dict = {"condition_name": condition_name, "shot_number": shot_number, "features": features}
                    features_list.append(features_dict)
                logger.info("End feature extract.")
                features_index = f"{CSV_ELASTIC_INDEX}-features"
                analysis_index = f"{CSV_ELASTIC_INDEX}-analysis"

            # kibana表示用インデックス（フィールドをフラットに保持）を作成
            flatten_features_list = self.get_flatten_features_list(features_list)

            # elasticsearchに保存
            logger.info("Saving to elasticsearch.")
            ElasticDataAccessor.insert(features_list, features_index)
            ElasticDataAccessor.insert(flatten_features_list, analysis_index)
            logger.info("Save to elasticsearch completed.")
            return

        return app


if __name__ == "__main__":
    from backend.dash_app.data_accessor import AidaCsvDataAccessor

    # TODO: デフォルトパスを共通ディレクトリに変更
    CSV_DIR = os.getenv("CSV_DIR", default="/customer_data/ymiyamoto5-aida_A39D/private/data/aida")
    # TODO: デフォルトの出力先インデックス名変更
    CSV_ELASTIC_INDEX = os.getenv("CSV_ELASTIC_INDEX", default="aida")

    aida_csv_data_accessor: CsvDataAccessor = AidaCsvDataAccessor(dir=CSV_DIR)

    brew_features = BrewFeatures(csv_data_accessor=aida_csv_data_accessor)
    app = brew_features.make_app()
    # JupyterDashでは今のところ0.0.0.0にbindできない
    app.run_server(host="0.0.0.0", port=8048, debug=True)
