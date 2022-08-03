import numpy as np
import plotly.graph_objs as go
import dash

# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html
import dash_bootstrap_components as dbc


def _plotly_add_shape(fig, ftype, xmin, xmax, ymin, ymax, fillcolor, alpha, xref, yref, layer, line_width):
    """
    plotly_hspan(),plotly_vspan()からのみ呼ばれ、figオブジェクトにshapeを描きこむ。
    """
    shapes = []
    # for s in fig.layout['shapes']:
    for s in fig["layout"]["shapes"]:
        shapes.append(s)
    if ftype == "rect":
        shapes.append(
            {
                "type": "rect",
                "x0": xmin,
                "x1": xmax,
                "y0": ymin,
                "y1": ymax,
                "xref": xref,
                "yref": yref,
                "fillcolor": fillcolor,
                "opacity": alpha,
                "layer": layer,
                "line_width": 0,
            }
        )
    elif ftype == "line":
        alpha = 1.0
        shapes.append(
            {
                "type": "line",
                "x0": xmin,
                "x1": xmax,
                "y0": ymin,
                "y1": ymax,
                "xref": xref,
                "yref": yref,
                "line": {"color": fillcolor, "width": line_width},
                "opacity": alpha,
                "layer": layer,
            }
        )
    fig.update_layout(shapes=shapes)


def plotly_hspan(fig, ymin, ymax, ftype="rect", xref="x", yref="y", fillcolor="LightSalmon", alpha=0.5, layer="below", line_width=1):
    """
    figオブジェクトに、X方向最大、Y方向任意の矩形、もしくは直線をshapeとして描画する。
    Y方向の描画位置はymin,ymaxの必須引数として指定する。矩形と直線はftypeとして指定する。
    matplotlibのaxhspan/axhlineを統合した仕様だが、
    ftype='line'の場合、yminとymaxはそれぞれ、ymin:Xが最小の時のYの値、ymax:Xが最大の時のYの値、という意味になる。
    yminとymaxが同じであれば、描画される直線は水平線となり、異なっていれば斜線となる。この点はaxhlineとは異なる。
    また、ftype='rect'の場合も、yminとymaxは矩形を描画するための対向頂点の座標を示すものである。
    よって、ftypeが'line'の場合においても、'rect'の場合においても、
    必ずしもymin <= ymaxとなっていなくても構わない。
    
    fig.layout['shapes']は複数のshapeをタプルとして保持しているが、
    fig.update_layout()はfig.layout['shapes']を上書きしており、
    shapeを追加、もしくは既存のshape要素を置き換えることはできない。
    このため、既存のfig.layout['shapes']をリストとして取り出し、
    描き込みたいshapeをこのリストに追加した上で、fig.update_layout()で上書きしている。

    :fig (list)             plotlyのfigオブジェクト
    :ymin (float)           矩形の下方値
    :ymax (float)           矩形の上方値
    :ftype (str)      　    'rect'|'line'
    :xref (str)             描画対象のaxis
    :yref (str)             描画対象のaxis
    :fillcolor (str)        塗りつぶし色
    :alpha (float(0.0-1.0)) 透明度
    :return                 なし
    """

    for d in fig.data:
        if d["xaxis"] == xref:
            xmin = d["x"].min()
            xmax = d["x"].max()
            break
    _plotly_add_shape(fig, ftype, xmin, xmax, ymin, ymax, fillcolor, alpha, xref, yref, layer, line_width)


def plotly_vspan(fig, xmin, xmax, ftype="rect", xref="x", yref="y", fillcolor="LightSalmon", alpha=0.5, layer="below", line_width=1):
    """
    plotly_hspan()のX軸/Y軸を入れ替えたもの。plotly_hspan()参照。
    """
    # for d in fig.data:
    for d in fig["data"]:
        if d["yaxis"] == yref:

            #             s = '%s'%d
            #             f = open('/tmp/debug.log','a')
            #             f.write(s)
            #             f.close()

            ymin = d["y"][~np.isnan(d["y"])].min()
            ymax = d["y"][~np.isnan(d["y"])].max()

            #             f = open('/tmp/debug.log','a')
            #             s = 'ymin:%f ymax:%f\n'%(ymin,ymax)
            #             f.write(s)
            #             f.close()

            break
    _plotly_add_shape(fig, ftype, xmin, xmax, ymin, ymax, fillcolor, alpha, xref, yref, layer, line_width)


import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def multi_col_figure(df, title="", row_titles=None, width=500, height=600, margin={"t": 80, "l": 60, "r": 30, "b": 30}, heights_list=None):
    #
    if row_titles is None:
        row_titles = list(df.columns)
    fig = make_subplots(
        rows=len(df.columns), cols=1, shared_xaxes=True, vertical_spacing=0.01, row_titles=row_titles, row_heights=heights_list
    )
    for i in range(len(df.columns)):
        fig.add_trace(go.Scatter(x=df.index, y=df.iloc[:, i], name=df.columns[i], marker_color="#3498db"), row=i + 1, col=1)

    fig.update_xaxes(matches="x")  # X軸だけ連動
    # fig.update_layout(showlegend=False, title_text=title,width=width,height=height,margin=margin)
    fig.update_layout(showlegend=False, title_text=title, height=height, margin=margin)
    return fig


def plot_multi_col(df, title="", width=800, height=1000, margin={"t": 80, "l": 60, "r": 30, "b": 60}, heights_list=None):
    fig = multi_col_figure(df, title, width, height, margin)
    fig.show()
