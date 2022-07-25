from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from backend.dash_app.constants import CONTENT_STYLE, MAX_COLS, MAX_ROWS, PREPROCESS, SIDEBAR_STYLE
from backend.dash_app.preprocessors import add, calibration, diff, moving_average, mul, regression_line, shift, sub, thinning_out
from backend.elastic_manager.elastic_manager import ElasticManager
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from plotly.subplots import make_subplots

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])


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

    df = pd.read_csv(
        csv_file,
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


def serve_layout():
    """レイアウト定義を返す"""

    return html.Div(
        id="main",
        children=[
            dcc.Store(id="shot-data"),
            dcc.Store(id="preprocessed-shot-data"),
            html.Div(
                id="sidebar",
                children=[
                    html.H3("表示設定", className="display-4"),
                    html.Hr(),
                    html.Div(
                        [
                            html.Label("データソースタイプ"),
                            dcc.Dropdown(
                                id="data-source-type-dropdown",
                                options=[{"label": "CSV", "value": "csv"}, {"label": "Elasticsearch", "value": "elastic"}],
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
                        [
                            html.Label("フィールド"),
                            dcc.Dropdown(id="field-dropdown"),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("グラフ行番号"),
                            dcc.Dropdown(
                                id="row-number-dropdown",
                                options=[r for r in range(1, MAX_ROWS + 1)],
                            ),
                            html.Label("グラフ列番号"),
                            dcc.Dropdown(
                                id="col-number-dropdown",
                                options=[c for c in range(1, MAX_COLS + 1)],
                            ),
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
                        id="moving-average-field",
                        children=[
                            html.Label("ウィンドウサイズ", style={"width": "100%"}),
                            dcc.Input(id="moving-average-field-input", type="number", min=1, max=100, step=1),
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
                    dbc.Button("追加", id="add-button", n_clicks=0, style={"margin-top": "1rem"}),
                ],
                style=SIDEBAR_STYLE,
            ),
            html.Div(
                id="contents",
                children=[
                    dash_table.DataTable(
                        id="setting-table",
                        data=pd.DataFrame().to_dict("records"),
                        style_table={"width": "1000px"},
                        columns=[
                            {"id": "field", "name": "フィールド"},
                            {"id": "row_number", "name": "行番号"},
                            {"id": "col_number", "name": "列番号"},
                            {"id": "preprocess", "name": "前処理"},
                            {"id": "detail", "name": "詳細"},
                        ],
                        row_deletable=True,
                    ),
                    dcc.Graph(id="graph"),
                ],
                style=CONTENT_STYLE,
            ),
        ],
    )


app.layout = serve_layout()

# callbacks #


@app.callback(
    Output("csv-file", "style"),
    Output("csv-file-dropdown", "options"),
    Input("data-source-type-dropdown", "value"),
    prevent_initial_call=True,
)
def set_csv_file_options(data_source_type):
    """CSVファイル選択ドロップダウンのオプション設定"""

    if data_source_type == "csv":
        # TODO: CSVファイルのディレクトリパスが決め打ちのため、要修正
        path = Path("/customer_data/ymiyamoto5-aida_A39D/private/data/aida/")
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
    prevent_initial_call=True,
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


@app.callback(
    Output("graph", "figure"),
    Input("setting-table", "data_previous"),  # 行削除を監視
    Input("setting-table", "data"),
    State("shot-data", "data"),
    prevent_initial_call=True,
)
def add_field_to_graph(previous_rows, rows, shot_data):
    """テーブルの変更（フィールドの追加・削除）を検知し、グラフを描画する。
    グラフ領域はコールバックの度にテーブル内容を参照して再描画する。
    """

    if len(rows) == 0:
        fig = make_subplots()
        return fig

    df = pd.read_json(shot_data, orient="split")

    max_row_number = max([r["row_number"] for r in rows])
    max_col_number = max([r["col_number"] for r in rows])

    # M行N列のグラフ領域
    fig = make_subplots(rows=max_row_number, cols=max_col_number, shared_xaxes=True, vertical_spacing=0.02, horizontal_spacing=0.05)

    # グラフの数だけループ
    for m in range(1, max_row_number + 1):
        for n in range(1, max_col_number + 1):
            for row in rows:
                # 入力で指定した（テーブルに記録されている）行列番号と一致する場合、当該位置のグラフに追加表示
                if row["row_number"] == m and row["col_number"] == n:
                    display_row = row["field"] + row["preprocess"] if row["preprocess"] else row["field"]
                    fig.add_trace(go.Scatter(x=df.index, y=df[display_row], name=display_row), row=m, col=n)

    fig.update_layout(width=1300, height=600)

    return fig


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8053, debug=True)
