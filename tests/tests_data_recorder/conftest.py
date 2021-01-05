import sys
import os
import pytest
import pathlib
import dataclasses

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../src/"))


@dataclasses.dataclass
class DatFiles:
    tmp_path: pathlib.Path
    tmp_dat_1: pathlib.Path
    tmp_dat_2: pathlib.Path
    tmp_dat_3: pathlib.Path
    tmp_dat_4: pathlib.Path
    tmp_dat_5: pathlib.Path


@pytest.fixture
def dat_files(tmp_path):
    """ datファイルのfixture """

    tmp_dat_1: pathlib.Path = tmp_path / "AD-00_20201216-080058.620753.dat"
    tmp_dat_2: pathlib.Path = tmp_path / "AD-00_20201216-080059.620753.dat"
    tmp_dat_3: pathlib.Path = tmp_path / "AD-00_20201216-080100.620753.dat"
    tmp_dat_4: pathlib.Path = tmp_path / "AD-00_20201216-080101.620753.dat"
    tmp_dat_5: pathlib.Path = tmp_path / "AD-00_20201216-080102.620753.dat"

    tmp_dat_1.write_text("")
    tmp_dat_2.write_text("")
    tmp_dat_3.write_text("")
    tmp_dat_4.write_text("")
    tmp_dat_5.write_text("")

    dat_files = DatFiles(tmp_path, tmp_dat_1, tmp_dat_2, tmp_dat_3, tmp_dat_4, tmp_dat_5)

    yield dat_files
