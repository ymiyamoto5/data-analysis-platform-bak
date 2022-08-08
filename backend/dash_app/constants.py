from enum import Enum, auto

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
    REGRESSION_LINE = "回帰直線"
    THINNING_OUT = "間引き"


class FIND_TYPE(Enum):
    FIX = "固定"
    RANGE_MORE = "値域>"
    RANGE_LESS = "値域<"
    FEATURE_POINT = "特徴点"


class FIND_TARGET(Enum):
    DPT = "DPT"
    VCT = "VCT"
    ACC = "ACC"


class FIND_DIR(Enum):
    MAX = "MAX"
    MIN = "MIN"
    RMS = "RMS"
    VAR = "VAR"
    AMP = "AMP"


class DATA_SOURCE_TYPE(Enum):
    ELASTIC = auto()
    CSV = auto()


MAX_ROWS = 5
MAX_COLS = 2
