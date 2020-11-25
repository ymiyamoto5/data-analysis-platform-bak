from typing import Callable, TypeVar
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=+9), 'JST')
RT = TypeVar('RT')


def time_log(func: Callable[..., RT]) -> Callable[..., RT]:
    """ 開始・終了・経過時間を表示するデコレータ """

    def wrapper(*args, **kwargs) -> RT:
        start = datetime.now(JST)
        print(f"{start} start {func.__name__}")
        func(*args, **kwargs)
        end = datetime.now(JST)
        delta = end - start
        print(f"{end} {func.__name__} finished. elapsed time: {delta}")
    return wrapper
