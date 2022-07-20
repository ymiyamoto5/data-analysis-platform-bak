from collections import OrderedDict
from tkinter.messagebox import NO

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend.dash_app.constants import CONTENT_STYLE, MAX_COLS, MAX_ROWS, PREPROCESS, SIDEBAR_STYLE
from backend.dash_app.preprocessors import add, diff
from backend.elastic_manager.elastic_manager import ElasticManager
from dash import Dash, Input, Output, State, ctx, dash_table, dcc, html
from dash.exceptions import PreventUpdate
from numpy import short, source
from plotly.subplots import make_subplots
from requests import get

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# shot_df = pd.DataFrame(
#     OrderedDict(
#         [
#             ("sequential_number", [0, 1, 2, 3, 4, 5]),
#             ("shot_number", [1, 1, 1, 2, 2, 2]),
#             ("load01", [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
#             ("load02", [0.3, 0.5, 0.2, 0.1, 0.4, 0.8]),
#         ]
#     )
# )

table_df = pd.DataFrame()


# def get_data_source_dropdown_options():
#     return [{"label": s, "value": s} for s in ElasticManager.show_indices(index="shots-*-data")["index"]]


def get_datatype_dropdown_options():
    return [
        {"label": "elastic", "value": "elastic"},
        {"label": "csv", "value": "csv"},
    ]


# def get_field_dropdown_options():
#     # return [{"label": c, "value": c} for c in shot_df.columns]
#     return [
#         {"label": "CH名称", "value": "CH名称"},
#         {"label": "右垂直", "value": "右垂直"},
#         {"label": "右45", "value": "右45"},
#         {"label": "右水平", "value": "右水平"},
#         {"label": "左垂直", "value": "左垂直"},
#         {"label": "左45", "value": "左45"},
#         {"label": "左水平", "value": "左水平"},
#         {"label": "M30ボルスタ右奥", "value": "M30ボルスタ右奥"},
#         {"label": "M20前左", "value": "M20前左"},
#         {"label": "M20前右", "value": "M20前右"},
#         {"label": "M20後左", "value": "M20後左"},
#         {"label": "M20後右", "value": "M20後右"},
#         {"label": "スライド＿金型隙間", "value": "スライド＿金型隙間"},
#         {"label": "プレス荷重", "value": "プレス荷重"},
#         {"label": "スライド変位", "value": "スライド変位"},
#     ]


def get_preprocess_dropdown_options():
    return [
        {"label": "", "value": ""},
        {"label": "微分", "value": PREPROCESS.DIFF.name},
        {"label": "加算", "value": PREPROCESS.ADD.name},
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
                            html.Label("データタイプ"),
                            dcc.Dropdown(
                                id="data-type-dropdown",
                                options=get_datatype_dropdown_options(),
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("データソース"),
                            dcc.Dropdown(
                                id="data-source-dropdown",
                                # options=get_data_source_dropdown_options()
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("フィールド"),
                            dcc.Dropdown(
                                id="field-dropdown",
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
                            dcc.Dropdown(id="add-field-dropdown"),
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
    Output("data-source-dropdown", "options"),
    Input("data-type-dropdown", "value"),
    prevent_initial_call=True,
)
def get_data_source_list(datatype):
    from pathlib import Path

    if datatype == "csv":
        path = Path("/customer_data/rfukudome2-aida_A39D/private/data/aida/")
        flist = list(sorted(path.glob("*.CSV")))
        options = [{"label": f.name, "value": str(f)} for f in flist]
        return options
    else:
        """elasticの処理"""

        return


@app.callback(
    Output("setting-table", "data"),
    Output("shot-data", "data"),
    Input("add-button", "n_clicks"),
    State("setting-table", "data"),
    State("field-dropdown", "value"),
    State("row-number-dropdown", "value"),
    State("col-number-dropdown", "value"),
    State("preprocess-dropdown", "value"),
    State("add-field-dropdown", "value"),
    State("data-source-dropdown", "value"),
    prevent_initial_call=True,
)
def add_button_clicked(n_clicks, rows, field, row_number, col_number, preprocess, add_field, data_source):
    if n_clicks <= 0:
        raise PreventUpdate

    df = get_data_source(data_source)

    new_row = {
        "field": field,
        "row_number": row_number,
        "col_number": col_number,
        "preprocess": preprocess,
        "detail": "",
    }

    if add_field:
        new_row["detail"] = f"加算行: {add_field}"

    rows.append(new_row)
    return rows, df.to_json(date_format="iso", orient="split")


@app.callback(
    Output("add-field", "style"),
    Output("add-field-dropdown", "value"),
    Input("preprocess-dropdown", "value"),
)
def create_preprocess_detail_dropdown(preprocess):
    if preprocess == PREPROCESS.ADD.name:
        return {}, ""
    else:
        return {"display": "none"}, ""


@app.callback(
    Output("graph", "figure"),
    Input("setting-table", "data_previous"),  # 行削除を監視
    Input("setting-table", "data"),
    State("shot-data", "data"),
    prevent_initial_call=True,
)
def add_field_to_graph(previous_rows, rows, shot_data):
    df = pd.read_json(shot_data, orient="split")

    graph_max_row = 1
    graph_max_col = 1

    for row in rows:
        if graph_max_row < row["row_number"]:
            graph_max_row = row["row_number"]
        if graph_max_col < row["col_number"]:
            graph_max_col = row["col_number"]

    # TODO: M行N列は別のInputから取得
    M, N = (graph_max_row, graph_max_col)

    fig = make_subplots(rows=M, cols=N)

    # TODO: サブプロットごとにDataFrameを作っているが非効率。もっと良い方法がないか？
    for m in range(1, M + 1):
        for n in range(1, N + 1):
            display_df = pd.DataFrame({"sequential_number": df.index})
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
                fig.add_trace(go.Scatter(x=d["x"], y=d["y"], name=d["name"]), row=m, col=n)

    fig.update_layout(height=600, width=1000)

    return fig


def get_data_source(data_source):
    df = pd.read_csv(data_source, encoding="cp932", skiprows=[0, 1, 2, 3, 4, 5, 6, 7])
    df = pd.read_csv(
        data_source,
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


@app.callback(
    Output("field-dropdown", "options"),
    # Output("shot-data", "data"),
    Input("add-button", "n_clicks"),
    Input("data-source-dropdown", "value"),
    State("field-dropdown", "value"),
    State("field-dropdown", "options"),
    State("preprocess-dropdown", "value"),
    prevent_initial_call=True,
)
def add_field_to_dropdown(n_clicks, data_source, field, options, preprocess):
    """
    データソースドロップダウンの変更を検知したときはフィールドオプションをセットする。
    追加ボタンが押下されたときはフィールドオプションに新しいフィールドを追加する。
    """

    df = get_data_source(data_source)

    if ctx.triggered_id == "data-source-dropdown":
        options = [{"label": c, "value": c} for c in df.columns]
    elif ctx.triggered_id == "add-button":
        if field is not None and preprocess is not None:
            new_field = field + preprocess
            # 既存のフィールドは追加しない
            if new_field not in df.columns:
                options.append({"label": new_field, "value": new_field})

    return options


if __name__ == "__main__":  # app.run_server(debug=True)
    app.run_server(host="0.0.0.0", port=8053, debug=True)
