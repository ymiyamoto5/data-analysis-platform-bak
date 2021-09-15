import os
import sys
import yaml
from logging import config, getLogger, Logger

CONF_FILE_NAME = "logging.conf"
ENV_KEY: str = "LOGGING_CONF"
logger: Logger
data_recorder_logger: Logger
uvicorn_logger: Logger


def findConf() -> str:
    """
    logging.conf を次の順に探して適用する
    1. 環境変数 LOGGING_CONF （ファイル名含めてフルパス指定）
    2. このpythonモジュールと同じディレクトリ内。ファイル名はlogging.conf固定
    3. python実行パス(getcwd)。ファイル名はlogging.conf固定
    4. PYTHONPATH上。ファイル名はlogging.conf固定
    """

    # 1.環境変数 LOGGING_CONFからの取得を試みる
    # 循環インポートを防ぐため、このモジュールはconfiguration_repositoryを使わない
    env_val = os.environ.get(ENV_KEY)
    if env_val is not None:
        if os.path.exists(env_val):
            print(f"ENV: {ENV_KEY} from os.environ. SET log configuration: {env_val}")
            return env_val
        print(f"*NOTFOUND* READ ENV: {ENV_KEY} from os.environ. but file NOT FOUND: {env_val}")

    # 2. このpythonモジュールと同じディレクトリ内からの取得を試みる
    script_path = os.path.dirname(os.path.abspath(__file__))
    current_dir_conf_path = os.path.join(script_path, CONF_FILE_NAME)
    if os.path.exists(current_dir_conf_path):
        print(f"SET log configuration (script path): {current_dir_conf_path}")
        return current_dir_conf_path

    # 3. python実行パス上から探す
    pwd_dir_conf_path = os.path.join(os.getcwd(), CONF_FILE_NAME)
    if os.path.exists(pwd_dir_conf_path):
        print(f"SET log configuration: (Current Working Directory) {pwd_dir_conf_path}")
        return pwd_dir_conf_path

    # 4. PYTHONPATH上から探す
    py_path_str = os.environ.get("PYTHONPATH")
    if py_path_str is None:
        sys.exit(1)

    for path in py_path_str.split(os.pathsep):
        conf_path = os.path.join(path, CONF_FILE_NAME)
        if os.path.exists(conf_path):
            print(f"SET log configuration: (PYTHONPATH) {conf_path}")
            return conf_path

    print("Error: There is no log configuration.")
    sys.exit(1)


def main() -> None:
    conf_file = findConf()
    if conf_file is None:
        print(f"*NOTFOUND* {CONF_FILE_NAME}.")
        return

    conf_yaml = yaml.load(open(conf_file).read(), Loader=yaml.SafeLoader)
    config.dictConfig(conf_yaml)

    global logger
    logger = getLogger("backend")

    global data_recorder_logger
    data_recorder_logger = getLogger("data_recorder")

    global uvicorn_logger
    logger = getLogger("uvicorn")


# call main.
main()
