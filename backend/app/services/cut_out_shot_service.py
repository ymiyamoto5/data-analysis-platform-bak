from datetime import datetime


class CutOutShotService:
    @staticmethod
    def get_target_dir(machine_id: str, target_date_timestamp: str) -> str:
        """ブラウザから文字列で渡されたUNIXTIME(ミリ秒単位）から、データディレクトリ名を特定して返却"""

        # NOTE: ブラウザからは文字列のUNIXTIME(ミリ秒)で与えられる。秒単位に直して変換。
        target_date: datetime = datetime.fromtimestamp(int(target_date_timestamp) / 1000)
        target_date_str: str = datetime.strftime(target_date, "%Y%m%d%H%M%S")
        target_dir_name = machine_id + "-" + target_date_str

        return target_dir_name
