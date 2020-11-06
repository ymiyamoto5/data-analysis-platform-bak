from .es_wrapper import ElasticsearchWrapper
from datetime import datetime
from pytz import timezone


# TODO: 共通の定数はコンフィグファイルから読み取る
SENSOR_DATA_INDEX = "sensor-data"
META_DATA_INDEX = "meta-data"


class Monitor():
    def __init__(self, es=None) -> None:
        if es is None:
            self.es = ElasticsearchWrapper()
        else:
            self.es = es

    def run(self, event_id: str, base_time: str = None, past_time: str = None) -> str:
        ''' 稼働監視
         Elasticsearchからセンサーデータを読み取り、異常判定を行う。
         読み取るデータは、既定でリクエスト時点から過去10秒間。
        '''
        if base_time is None:
            base_time = "now"
        if past_time is None:
            past_time = "now-10s"

        self.es.create_index(index=META_DATA_INDEX)

        # イベント開始時、メタデータに稼働監視イベントを記録
        if not self.es.exists(index=META_DATA_INDEX, id=event_id):
            start_time = datetime.now(timezone('UTC'))
            event_info = {
                "event_id": event_id,
                "event": "monitoring",
                "start_time": start_time,
                "molding_machine_name": "テスト成形機",
                "mold_name": "テスト金型",
                "material_name": "テスト材料",
                "stop_reason": "未記録",
                "stop_factor": "",
            }
            # 同時に更新処理がされてconflictしてしまう場合があるため、upsertしている
            self.es.upsert(index=META_DATA_INDEX, data=event_info, id=event_id)

        # 特定時刻（デフォルトはリクエスト開始時刻）を起点に、過去N秒間（デフォルト10秒）のデータを取得する
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": past_time,
                        "lt": base_time
                    }
                }
            },
            "size": 100
        }
        result = self.es.search(index=SENSOR_DATA_INDEX, query=query)

        # TODO: エラー時はmessageにエラーメッセージを格納して返すが、エラーフラグも返したほうが自明
        message = ""

        if len(result) == 0:
            message = "一定時間センサーデータを受信しませんでした"
            return message

        # TODO: 異常判定ロジックは仮。今後要検討。
        anormaly_count = sum(x['displacement'] == 0 for x in result)
        if anormaly_count >= 5:
            message = "変位0が一定回数以上発生しています"
            return message

        return message

    def record_stop_event(self, event_id: str, stopped_time: str, stop_reason: str, stop_factor: str) -> None:
        data = {
            "end_time": stopped_time,
            "stop_reason": stop_reason,
            "stop_factor": stop_factor,
        }

        self.es.update(index=META_DATA_INDEX, data=data, id=event_id)
