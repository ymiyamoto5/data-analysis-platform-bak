from enum import Enum
from typing import Optional, Union


class ErrorTypes(Enum):
    KEY_ERROR = "キーが不正です"
    VALUE_ERROR = "値が不正です"
    INCORRECT_FORMAT = "形式が正しくありません。"
    RANGE_ERROR = "値が範囲外です"
    EXCEPTION = "例外が発生しました。管理者に問い合わせてください。"
    CREATE_FAIL = "作成に失敗しました"
    READ_FAIL = "読み取りに失敗しました"
    UPDATE_FAIL = "更新に失敗しました"
    DELETE_FAIL = "削除に失敗しました"
    NOT_EXISTS = "対象が存在しません"
    VALID_ERROR = "検証に失敗しました"
    NO_INPUT_DATA = "入力データがありません"
    NO_DATA = "データがありません"  # len(list) == 0のとき
    GW_STATUS_ERROR = "ゲートウェイステータスが正しくありません"
    COLLECT_STATUS_ERROR = "収集ステータスが正しくありません"
    GW_RESULT_ERROR = "ゲートウェイエラーです"
    CUT_OUT_SHOT_ERROR = "ショット切り出しに失敗しました"
    MULTI_HANDLER_ERROR = "複数ハンドラー構成が正しくありません"


class ErrorMessage:
    @staticmethod
    def generate_message(error_type: ErrorTypes, target: Optional[Union[str, int]] = None):
        if error_type == ErrorTypes.KEY_ERROR:
            return f"{ErrorTypes.KEY_ERROR.value}: {target}"
        if error_type == ErrorTypes.VALUE_ERROR:
            return f"{ErrorTypes.VALUE_ERROR.value}: {target}"
        if error_type == ErrorTypes.INCORRECT_FORMAT:
            return f"{ErrorTypes.INCORRECT_FORMAT.value}: {target}"
        if error_type == ErrorTypes.RANGE_ERROR:
            return f"{ErrorTypes.RANGE_ERROR.value}: {target}"
        if error_type == ErrorTypes.EXCEPTION:
            return f"{ErrorTypes.EXCEPTION.value}"
        if error_type == ErrorTypes.CREATE_FAIL:
            return f"{ErrorTypes.CREATE_FAIL.value}"
        if error_type == ErrorTypes.READ_FAIL:
            return f"{ErrorTypes.READ_FAIL.value}"
        if error_type == ErrorTypes.UPDATE_FAIL:
            return f"{ErrorTypes.UPDATE_FAIL.value}"
        if error_type == ErrorTypes.DELETE_FAIL:
            return f"{ErrorTypes.DELETE_FAIL.value}"
        if error_type == ErrorTypes.NOT_EXISTS:
            return f"{ErrorTypes.NOT_EXISTS.value}"
        if error_type == ErrorTypes.VALID_ERROR:
            return f"{ErrorTypes.VALID_ERROR.value}: {target}"
        if error_type == ErrorTypes.NO_INPUT_DATA:
            return f"{ErrorTypes.NO_INPUT_DATA.value}"
        if error_type == ErrorTypes.NO_DATA:
            return f"{ErrorTypes.NO_DATA.value}"
        if error_type == ErrorTypes.GW_STATUS_ERROR:
            return f"{ErrorTypes.GW_STATUS_ERROR.value}: {target}"
        if error_type == ErrorTypes.COLLECT_STATUS_ERROR:
            return f"{ErrorTypes.COLLECT_STATUS_ERROR.value}: {target}"
        if error_type == ErrorTypes.GW_RESULT_ERROR:
            return f"{ErrorTypes.GW_RESULT_ERROR.value}: {target}"
        if error_type == ErrorTypes.CUT_OUT_SHOT_ERROR:
            return f"{ErrorTypes.CUT_OUT_SHOT_ERROR.value}: {target}"
        if error_type == ErrorTypes.MULTI_HANDLER_ERROR:
            return f"{ErrorTypes.MULTI_HANDLER_ERROR.value}"
