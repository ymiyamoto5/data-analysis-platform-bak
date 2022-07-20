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


class NoValue(Enum):
    """自動採番される値を隠ぺいする"""

    def __repr__(self):
        """PREPROCESS.DIFFでアクセスした場合の表示
        overrideなし: <PREPROCESS.DIFF: 1>
        overrideあり: <PREPROCESS.DIFF>
        """
        return "<%s.%s>" % (self.__class__.__name__, self.name)


class PREPROCESS(NoValue):
    DIFF = auto()
    ADD = auto()


MAX_ROWS = 5
MAX_COLS = 2
