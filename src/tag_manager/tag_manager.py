import numpy as np
import pandas as pd
import logging
import logging.handlers
from typing import List
from pandas.core.frame import DataFrame
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TagManager:
    def __init__(self, back_seconds_for_tagging: int = 120):
        self.__back_seconds_for_tagging = back_seconds_for_tagging  # 何秒遡ってタグ付けするか

    def _get_tag_events(self, events: List[dict]) -> List[dict]:
        """ events_indexからタグ付け区間を取得。
            記録された時刻（end_time）からN秒前(back_seconds_for_tagging)に遡り、start_timeとする。
        """

        tag_events: List[dict] = [x for x in events if x["event_type"] == "tag"]
        logger.debug(tag_events)

        if len(tag_events) > 0:
            for tag_event in tag_events:
                if tag_event.get("end_time") is None:
                    logger.exception("Invalid status in tag event. Not found [end_time] key.")
                    raise KeyError

                tag_event["end_time"] = datetime.fromisoformat(tag_event["end_time"])
                tag_event["start_time"] = tag_event["end_time"] - timedelta(seconds=self.__back_seconds_for_tagging)
                # DataFrameのtimestampと比較するため、datetimeからtimestampに変換
                tag_event["start_time"] = tag_event["start_time"].timestamp()
                tag_event["end_time"] = tag_event["end_time"].timestamp()

        return tag_events

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
                continue

            # タグ追加用の列を用意し、タグ内容で初期化する
            tags_df["to_add"] = [tag_event["tag"]] * len(tags_df)
            # 元のDataFrameとタグDataFrameを、timestampをキーにして結合する
            df = pd.merge(df, tags_df, on="timestamp", how="left")

            def _add_tag(x):
                """ to_add列のタグをtagsにappend """
                if x["to_add"] is not np.nan:
                    x["tags"].append(x["to_add"])

            df.apply(_add_tag, axis=1)
            # タグ追加用の列は用を成したので破棄
            df.drop(columns="to_add", inplace=True)

        return df

    def tagging(self, df: DataFrame, events: List[dict]) -> DataFrame:
        """ tagイベントからタグ付けする """

        # イベント情報リストからタグイベントを取得
        tag_events: List[dict] = self._get_tag_events(events)

        if len(tag_events) == 0:
            return df

        df = self._add_tags_from_events(df, tag_events)

        return df


if __name__ == "__main__":
    pass
