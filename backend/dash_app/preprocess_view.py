from collections import OrderedDict

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.dash_app.constants import CONTENT_STYLE, MAX_COLS, MAX_ROWS, PREPROCESS, SIDEBAR_STYLE
from backend.dash_app.preprocessors import add, calibration, diff, moving_average, mul, regression_line, shift, sub, thinning_out
from backend.elastic_manager.elastic_manager import ElasticManager
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from plotly.subplots import make_subplots

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

shot_df = pd.DataFrame(
    OrderedDict(
        [
            # ("sequential_number", [0, 1, 2, 3, 4, 5]),
            ("shot_number", [1, 1, 1, 2, 2, 2]),
            ("load01", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
            ("load02", [0.3, 0.5, 0.2, 0.1, 0.4, 0.8]),
        ]
    )
)

shot_df["sequential_number"] = shot_df.index

table_df = pd.DataFrame()


def get_data_source_dropdown_options():
    return [{"label": s, "value": s} for s in ElasticManager.show_indices(index="shots-*-data")["index"]]


def get_field_dropdown_options():
    # return [{"label": c, "value": c} for c in shot_df.columns]
    return []


def get_index_field_dropdown_options(index):
    query: dict = {"sort": {"shot_number": {"order": "asc"}}}
    result = ElasticManager.get_docs(index=index, query=query)
    shot_df = pd.DataFrame(result)
    options = [{"label": c, "value": c} for c in shot_df.columns]
    return options


def get_preprocess_dropdown_options():
    return [
        {"label": "", "value": ""},
        {"label": "微分", "value": PREPROCESS.DIFF.name},
        {"label": "加算", "value": PREPROCESS.ADD.name},
        {"label": "減算", "value": PREPROCESS.SUB.name},
        {"label": "係数乗算", "value": PREPROCESS.MUL.name},
        {"label": "シフト", "value": PREPROCESS.SHIFT.name},
        {"label": "校正", "value": PREPROCESS.CALIBRATION.name},
        {"label": "移動平均", "value": PREPROCESS.MOVING_AVERAGE.name},
        {"label": "回帰直線", "value": PREPROCESS.REGRESSION_LINE.name},
        {"label": "間引き", "value": PREPROCESS.THINNING_OUT.name},
    ]


def serve_layout():
    return html.Div(
        id="main",
        children=[
            html.Div(id="output"),
            dcc.Store(id="shot-data"),
            html.Div(
                id="sidebar",
                children=[
                    html.H2("Sidebar", className="display-4"),
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
                        id="csv-field",
                        children=[
                            html.Label("ファイル"),
                            dcc.Dropdown(id="csv-field-dropdown", options=[]),
                        ],
                        style={"display": "none"},
                    ),
                    html.Div(
                        id="index-field",
                        children=[
                            html.Label("インデックス"),
                            dcc.Dropdown(id="index-field-dropdown", options=get_data_source_dropdown_options()),
                        ],
                        style={"display": "none"},
                    ),
                    html.Div(
                        [
                            html.Label("フィールド"),
                            dcc.Dropdown(
                                id="field-dropdown",
                                options=get_field_dropdown_options(),
                            ),
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
                            dcc.Dropdown(id="add-field-dropdown", options=get_field_dropdown_options()),
                        ],
                        style={"display": "none"},
                    ),
                    html.Div(
                        id="sub-field",
                        children=[
                            html.Label("減算列"),
                            dcc.Dropdown(id="sub-field-dropdown", options=get_field_dropdown_options()),
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
                            dcc.Dropdown(id="regression-line-field-dropdown", options=get_field_dropdown_options()),
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
                    html.Button("追加", id="add-button", n_clicks=0),
                ],
                style=SIDEBAR_STYLE,
            ),
            html.Div(
                id="contents",
                children=[
                    dash_table.DataTable(
                        id="setting-table",
                        data=table_df.to_dict("records"),
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


@app.callback(
    Output("setting-table", "data"),
    Input("add-button", "n_clicks"),
    State("setting-table", "data"),
    State("field-dropdown", "value"),
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
)
def add_field_to_table(
    n_clicks,
    rows,
    field,
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
):
    if n_clicks <= 0:
        return rows

    new_row = {
        "field": field,
        "row_number": row_number,
        "col_number": col_number,
        "preprocess": preprocess,
        "detail": "",
    }

    if add_field:
        new_row["detail"] = f"加算行: {add_field}"
    elif sub_field:
        new_row["detail"] = f"減算行: {sub_field}"
    elif mul_field:
        new_row["detail"] = f"係数: {mul_field}"
    elif shift_field:
        new_row["detail"] = f"シフト幅: {shift_field}"
    elif calibration_field:
        new_row["detail"] = f"校正: 先頭{calibration_field}件"
    elif moving_average_field:
        new_row["detail"] = f"ウィンドウサイズ: {moving_average_field}"
    elif regression_line_field:
        new_row["detail"] = f"回帰直線: {regression_line_field}"
    elif thinning_out_field:
        new_row["detail"] = f"間引き幅: {thinning_out_field}"

    rows.append(new_row)
    return rows


@app.callback(
    Output("csv-field", "style"),
    Output("csv-field-dropdown", "value"),
    Input("data-source-type-dropdown", "value"),
)
def create_csv_field_dropdown(data_source):
    if data_source == "csv":
        return {}, ""
    else:
        return {"display": "none"}, ""


@app.callback(
    Output("index-field", "style"),
    Output("index-field-dropdown", "value"),
    Input("data-source-type-dropdown", "value"),
    prevent_initial_call=True,
)
def create_index_field_dropdown(data_source):
    if data_source == "elastic":
        return {}, ""
    else:
        return {"display": "none"}, ""


@app.callback(
    Output("add-field", "style"),
    Output("add-field-dropdown", "value"),
    Output("add-field-dropdown", "options"),
    Input("preprocess-dropdown", "value"),
    State("field-dropdown", "options"),
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
)
def create_thinning_out_field_input(preprocess):
    if preprocess == PREPROCESS.THINNING_OUT.name:
        return {}, ""
    else:
        return {"display": "none"}, ""


@app.callback(
    Output("shot-data", "data"),
    Input("add-button", "n_clicks"),
    Input("index-field-dropdown", "value"),
    State("shot-data", "data"),
    State("field-dropdown", "value"),
    State("preprocess-dropdown", "value"),
    State("add-field-dropdown", "value"),
    State("sub-field-dropdown", "value"),
    State("mul-field-input", "value"),
    State("shift-field-input", "value"),
    State("calibration-field-input", "value"),
    State("moving-average-field-input", "value"),
    State("regression-line-field-dropdown", "value"),
    State("thinning-out-field-input", "value"),
)
def set_data(
    n_clicks,
    index,
    shot_data,
    field,
    preprocess,
    add_field,
    sub_field,
    mul_field,
    shift_field,
    calibration_field,
    moving_average_field,
    regression_line_field,
    thinning_out_field,
):
    df = shot_df.copy()
    if ctx.triggered_id == "add-button":
        df = pd.read_json(shot_data, orient="split")
    elif ctx.triggered_id == "index-field-dropdown":
        query: dict = {"sort": {"shot_number": {"order": "asc"}}}
        result = ElasticManager.get_docs(index=index, query=query)
        df = pd.DataFrame(result)

    if preprocess is None or preprocess == "":
        return df.to_json(date_format="iso", orient="split")

    if preprocess == PREPROCESS.DIFF.name:
        preprocessed_field = diff(df, field)
    elif preprocess == PREPROCESS.ADD.name:
        preprocessed_field = add(df, field, add_field)
    elif preprocess == PREPROCESS.SUB.name:
        preprocessed_field = sub(df, field, sub_field)
    elif preprocess == PREPROCESS.MUL.name:
        preprocessed_field = mul(df, field, mul_field)
    elif preprocess == PREPROCESS.SHIFT.name:
        preprocessed_field = shift(df, field, shift_field)
    elif preprocess == PREPROCESS.CALIBRATION.name:
        preprocessed_field = calibration(df, field, calibration_field)
    elif preprocess == PREPROCESS.MOVING_AVERAGE.name:
        preprocessed_field = moving_average(df, field, moving_average_field)
    elif preprocess == PREPROCESS.REGRESSION_LINE.name:
        preprocessed_field = regression_line(df, field, regression_line_field)
        # TODO: モデルから切片と係数を取得してグラフ描写。実装箇所は要検討。
    elif preprocess == PREPROCESS.THINNING_OUT.name:
        preprocessed_field = thinning_out(df, field, thinning_out_field)
    else:
        preprocessed_field = df[field]

    df[field + preprocess] = preprocessed_field
    return df.to_json(date_format="iso", orient="split")


@app.callback(
    Output("graph", "figure"),
    Input("shot-data", "data"),
    Input("setting-table", "data_previous"),  # 行削除を監視
    State("setting-table", "data"),
    prevent_initial_call=True,
)
def add_field_to_graph(shot_data, previous_rows, rows):
    df = pd.read_json(shot_data, orient="split")
    # df = shot_df

    # TODO: M行N列は別のInputから取得
    M, N = (2, 2)

    fig = make_subplots(rows=M, cols=N)

    # TODO: サブプロットごとにDataFrameを作っているが非効率。もっと良い方法がないか？
    for m in range(1, M + 1):
        for n in range(1, N + 1):
            display_df = pd.DataFrame(df["sequential_number"])
            for row in rows:
                if row["field"] == "" or row["row_number"] == "" or row["col_number"] == "":
                    continue
                row_number = int(row["row_number"])
                col_number = int(row["col_number"])
                # 入力で指定した行列番号と一致する場合、その項目を表示するためにDataFrameに加える
                if row_number == m and col_number == n:
                    if row["preprocess"] is not None:
                        display_df[row["field"] + row["preprocess"]] = df[row["field"] + row["preprocess"]]
                    else:
                        display_df[row["field"]] = df[row["field"]]
            sub_fig = px.line(data_frame=display_df, x="sequential_number", y=display_df.columns)
            for d in sub_fig.data:
                fig.add_trace(go.Scatter(x=d["x"], y=d["y"], name=d["name"], connectgaps=True), row=m, col=n)

    fig.update_layout(height=500, width=700)

    return fig


@app.callback(
    Output("field-dropdown", "options"),
    Input("add-button", "n_clicks"),
    Input("index-field-dropdown", "value"),
    State("shot-data", "data"),
    State("field-dropdown", "value"),
    State("field-dropdown", "options"),
    State("preprocess-dropdown", "value"),
    prevent_initial_call=True,
)
def add_field_to_preprocess_dropdown(n_clicks, index, shot_data, field, options, preprocess):
    """
    データソースドロップダウンの変更を検知したときはフィールドオプションをセットする。
    追加ボタンが押下されたときはフィールドオプションに新しいフィールドを追加する。
    """
    shot_df = pd.read_json(shot_data, orient="split")
    if ctx.triggered_id == "index-field-dropdown":
        if index is not None:
            options = get_index_field_dropdown_options(index)
    elif ctx.triggered_id == "add-button":
        if field is not None and preprocess is not None:
            new_field = field + preprocess
            # 既存のフィールドは追加しない
            if new_field not in shot_df.columns:
                options.append({"label": new_field, "value": new_field})
    return options


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server(host="0.0.0.0", port=8049, debug=True)
