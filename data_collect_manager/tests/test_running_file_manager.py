import os
import pytest
from ..models.config_file_manager import ConfigFileManager


def test_is_exists_config_file_not_exists() -> None:
    """ config fileの存在確認。ない場合 """

    cfm = ConfigFileManager("")
    assert cfm.check_file_exists() is False


def test_is_exists_config_file_already_exists(tmp_path) -> None:
    """ config fileの存在確認。すでにある場合 """

    tmp_file = tmp_path / "tmp.cnf"
    tmp_file.write_text("temporary...")

    cfm = ConfigFileManager(tmp_file._str)
    assert cfm.check_file_exists() is True


def test_create_config_file():
    """ config fileの作成 """
    pass


def test_create_running_file_already_exits():
    """ すでにRunning Fileがある場合 """
    pass
