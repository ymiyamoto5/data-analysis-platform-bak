from enum import Enum

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "22rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


class PREPROCESS(Enum):
    DIFF = "微分"
    ADD = "加算"
    SUB = "減算"
    MUL = "係数乗算"
    SHIFT = "シフト"
    CALIBRATION = "校正"
    MOVING_AVERAGE = "移動平均"
    REGRESSION_LINE = "回帰直線"
    THINNING_OUT = "間引き"


MAX_ROWS = 5
MAX_COLS = 2
