from typing import List

import numpy as np
import pandas as pd
from backend.common.common_logger import logger
from backend.event_manager.event_manager import EventManager
from pandas.core.frame import DataFrame


class TagManager:
    def __init__(self, back_seconds_for_tagging: int = 120):
        self.__back_seconds_for_tagging = back_seconds_for_tagging  # 何秒遡ってタグ付けするか

    def _add_tags_from_events(self, df: DataFrame, tag_events: List[dict]) -> DataFrame:

        # tags列を空のリストで初期化
        df["tags"] = pd.Series([[] for _ in range(len(df))])

        # tag_eventsのstart-end範囲内であればtag付けする
        for tag_event in tag_events:
            start_time: float = tag_event["start_time"]  # noqa
            end_time: float = tag_event["end_time"]  # noqa

            # タグ対象のtimestampのDataFrameを作る
            tags_df: DataFrame = df.query("@start_time <= timestamp <= @end_time").filter(
                items=["timestamp"], axis="columns"
            )

            if len(tags_df) == 0:
                logger.debug("No tags.")
                continue

            # タグ追加用の列を用意し、タグ内容で初期化する
            tags_df["to_add"] = [tag_event["tag"]] * len(tags_df)
            # 元のDataFrameとタグDataFrameを、timestampをキーにして結合する
            df = pd.merge(df, tags_df, on="timestamp", how="left")

            def _add_tag(x):
                """to_add列のタグをtagsにappend"""
                if x["to_add"] is not np.nan:
                    x["tags"].append(x["to_add"])

            df.apply(_add_tag, axis=1)
            # タグ追加用の列は用を成したので破棄
            df.drop(columns="to_add", inplace=True)

        return df

    def tagging(self, df: DataFrame, events: List[dict]) -> DataFrame:
        """tagイベントからタグ付けする"""

        # イベント情報リストからタグイベントを取得
        tag_events: List[dict] = EventManager.get_tag_events(events, self.__back_seconds_for_tagging)

        if len(tag_events) == 0:
            return df

        df = self._add_tags_from_events(df, tag_events)

        return df


if __name__ == "__main__":
    pass
