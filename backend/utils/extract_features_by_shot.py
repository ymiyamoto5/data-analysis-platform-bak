import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../../"))


from backend.analyzer.extract_features import NARROW_PADDING

# import backend.analyzer.h_one_extract_features as ef
from backend.app.crud.crud_data_collect_history import CRUDDataCollectHistory
from backend.app.crud.crud_machine import CRUDMachine
from backend.app.db.session import SessionLocal
from backend.data_reader.data_reader import DataReader

### 以下大塚さんに要確認(Juypterから持ってきたが、extract_features.pyへの取込が必要) ###

ROLLING_MEAN = 1
NARROW = False
TARGET = 999
HORIZONTAL_LIMIT = [None, None]
VERTICAL_LIMIT = [None, None]

#
DST = "d"
VCT = "v"
ACC = "a"

# 4ch前提の設計になっていたので、暫定修正。処理対象カラム名を引数で渡すようにすれば行けるのでは?
def extract_features(
    shot_data, spm, func, narrowing=None, sub_func=None, disp_narrowing=False, disp_chart=False, xlim=[-100, 100], **kwargs
):
    """特徴抽出ハンドラ関数
    変位をトリガーに切り出した1ショットのデータをpd.DataFrame(shot_data)として受け取り、
    抽出した特徴値を返す。
    shot_dataは4ch('load01','load02','load03','load04')固定であり、
    特徴値はindexと値をそれぞれ長さ4のリストとして返す。

    funcは特徴抽出関数のポインタであり、kwargsはfuncにそのまま渡される。
    kwargsの内容には基本的に感知しないが、例外が二つ。
    disp_chartが指定された場合は、kwargsの中にshotの存在を期待することと、
    funcを呼び出す際にkwargsにchを追加すること。
    extract_features()にとってのshot、funcにとってのchは、
    いずれも本質的には必要のない変数だが、デバッグ、処理状況の把握のため必要となる。

    disp_chartは、元波形と特徴量をプロットすることでfuncの処理結果を可視化する。
    さらに詳細な、処理過程を確認したい場合はDebugの指定によりchごとの可視化が行われる。
    extract_features()の利用者にとって意識し辛いと思われるが、
    disp_chartはextract_features()に対する引数であり、Debugはfuncに対する可変キーワード引数である。

    :shot_data (pd.DataFrame)
    :spm (float)                      SPM(shots per minutes)
    :func (*function)                 関数ポインタ; 求めたい特徴値により対応する関数を指定
    :sub_func (*function)             関数ポインタ; 処理効率改善のため時系列検索範囲を限定する必要があり、
                                      4ch共通の範囲を指定したい場合に使用。現在は破断点の場合のみ、narrowing_var_chを指定。
    :disp_narrowing (bool)            sub_funcで指定した関数に渡され、グラフ表示を制御する
    :disp_chart (bool)                グラフ表示; ショットごとの元波形と特徴量を表示。
    :**kwargs (可変キーワード引数)    funcに指定した関数に対応した引数を指定
    :return (list, list, list)        indexリスト, 値リスト, デバッグリスト
    """
    #     print(shot_data.head())
    cmap = plt.get_cmap("tab10")
    if spm is None:  # 最後のショットは次のショットが無いためspm計算不能, 80を想定する。
        spm = 80.0

    if "shot" in kwargs:
        shot = kwargs["shot"]  # 可変キーワード変数から拝借; 掟破り
    else:
        shot = 9999

    if narrowing is not None:
        sub_start = narrowing[0] - NARROW_PADDING
        sub_end = narrowing[1] + NARROW_PADDING
    else:
        if sub_func is not None:
            sub_start, sub_end = sub_func(shot_data, disp_narrowing, shot)
            # NARROW_PADDING考慮の上で限定範囲がデータの先頭/終端を超える場合、
            # また限定範囲が10より狭い場合は範囲限定を無効にする。
            if sub_start - NARROW_PADDING < 0 or sub_end + NARROW_PADDING > shot_data.index[-1] or sub_end - sub_start < 10:
                sub_start = shot_data.index[0]
                sub_end = shot_data.index[-1]
            else:
                sub_start = sub_start - NARROW_PADDING
                sub_end = sub_end + NARROW_PADDING
        else:
            sub_start = shot_data.index[0]
            sub_end = shot_data.index[-1]

    argmax = []
    valmax = []
    debugval = []
    chs = ["load01", "load02", "load03", "load04"]
    # chs = ["load01"]
    for ch in chs:
        kwargs["ch"] = ch  # 可変キーワードにch追加
        i, v, d = func(np.array(shot_data[ch][sub_start:sub_end]), spm, **kwargs)  # ここでnp.arrayになるのでindexがなくなる
        argmax.append(i + sub_start)  # funcはsubset中の相対indexを返してくるので、offsetを加える
        valmax.append(v)
        debugval.append(d)

    if disp_chart:
        plt.figure(figsize=(12, 6))
        for c in range(len(chs)):
            plt.plot(shot_data.index, shot_data[chs[c]], label=chs[c], alpha=0.3, color=cmap(c))  # 「流れ」があるのでscatterよりlineの方が見やすいと思う
            # plt.scatter(shot_data.index,shot_data[chs[c]],label=chs[c],s=2,alpha=1.0,color=[cmap(c)]*len(shot_data))
            plt.scatter([argmax[c]], [valmax[c]], marker="o", s=200, alpha=0.5, color=[cmap(c)])  # plotとscatterのcolor mapを揃える
        plt.title("%s shot:%d" % (func.__name__, shot))
        plt.legend()
        if xlim[0] != 0 or xlim[1] != 0:
            plt.xlim(np.array(argmax).min() + xlim[0], np.array(argmax).max() + xlim[1])
        plt.show()

    return argmax, valmax, debugval


ROLLING_MEAN = 1
NARROW = False
TARGET = 999
HORIZONTAL_LIMIT = [None, None]
VERTICAL_LIMIT = [None, None]
#
DST = "d"
VCT = "v"
ACC = "a"

# 初期は元波形をdf['o']として初期化。復数系列をどうするか?
def _gendf():
    # ここにdf['d']が無かったらというifを入れる
    if "d" not in df.columns:
        #         print('T')
        df["d"] = df.o.rolling(ROLLING_MEAN, center=True).mean()
        df["v"] = df.d.rolling(ROLLING_MEAN, center=True).mean().diff()
        df["a"] = df.v.rolling(ROLLING_MEAN, center=True).mean().diff()
    # else:


def _narrowing():
    ndf = df.copy()
    if HORIZONTAL_LIMIT[0] is not None:
        ndf = ndf[ndf.index >= HORIZONTAL_LIMIT[0]]
    if HORIZONTAL_LIMIT[1] is not None:
        ndf = ndf[ndf.index <= HORIZONTAL_LIMIT[1]]
    if VERTICAL_LIMIT[0] is not None:
        ndf = ndf[ndf.d <= VERTICAL_LIMIT[0]]
    if VERTICAL_LIMIT[1] is not None:
        ndf = ndf[ndf.d <= VERTICAL_LIMIT[1]]

    return ndf


# 使う関数の数だけ以下を用意する。と言ってもこれ以外にMAXとMINだけか?
# 現在は各関数に記述してるが、共通化できる。と言うか、クラスにしちゃった方が良いか?
def IDXMAX(d):
    _gendf()
    if NARROW is True:
        ndf = _narrowing()
    else:
        ndf = df
    target = ndf[d].idxmax()
    return target


def IDXMIN(d):
    _gendf()
    if NARROW is True:
        ndf = _narrowing()
    else:
        ndf = df
    target = ndf[d].idxmin()
    return target


# デバッグ用可視化関数。上位のメニュー?から呼ぶことを想定
def disp_data():
    axes = df[["o", "d", "v", "a"]].plot(subplots=True, figsize=(10, 6))
    for ax in axes:
        hlimit = [0, 0]
        ax.axvline(TARGET, color="r")  # 検索結果

        if not (HORIZONTAL_LIMIT[0] is None and HORIZONTAL_LIMIT[1] is None):  # 上下限とも無指定なら範囲限定無し
            if HORIZONTAL_LIMIT[0] is None:
                hlimit[0] = df.index[0]
            else:
                hlimit[0] = HORIZONTAL_LIMIT[0]
            if HORIZONTAL_LIMIT[1] is None:
                hlimit[1] = df.index[-1]
            else:
                hlimit[1] = HORIZONTAL_LIMIT[1]
            ax.axvspan(hlimit[0], hlimit[1], color="b", alpha=0.3)
    if VERTICAL_LIMIT[0] is not None or VERTICAL_LIMIT[1] is not None:
        if VERTICAL_LIMIT[0] is not None:
            axes[1].axhline(VERTICAL_LIMIT[0], color="b")
            vlimit_low = VERTICAL_LIMIT[0]
        else:
            vlimit_low = df["d"].min()
        if VERTICAL_LIMIT[1] is not None:
            axes[1].axhline(VERTICAL_LIMIT[1], color="b")
            vlimit_high = VERTICAL_LIMIT[1]
        else:
            vlimit_high = df["d"].max()
        #         axes[1].axhspan(vlimit_low,vlimit_high,color='b',alpha=.3)
        axes[1].fill_between(df.index, df["d"], vlimit_high)

    plt.show()


# 特徴抽出関数。これをextract_features()に渡す。
def eval_dsl(d, spm, fs=100000, low=0, high=None, r_window=19, Debug=False, shot=9999, ch="loadxx", debug_xlim=[-1500, 1000], dslstr=""):

    global df
    df = pd.DataFrame(np.array(d), columns=["o"])
    #     _gendf()
    #     print(df.o.idxmin())

    dslstr = "NARROW = False\n" + dslstr.replace("TARGET", "NARROW = True\nTARGET")
    dslstr = "global df, ROLLING_MEAN, HORIZONTAL_LIMIT, VERTICAL_LIMIT, TARGET, NARROW\n" + dslstr
    exec(dslstr)

    return TARGET, df["d"][TARGET], None  # ここからdfは参照できない..
    # return TARGET, 0, None


###

### ここからサンプル

db = SessionLocal()

# 機器に設定されたDSLを取得するサンプル
machine_id = "machine-01"
machine = CRUDMachine.select_by_id(db, machine_id)

# print(machine.start_point_dsl)
# print(machine.max_point_dsl)
# print(machine.break_point_dsl)

# 処理対象のインデックスを特定するため、yyyyMMdd文字列を取得するサンプル
latest_data_collect_history = CRUDDataCollectHistory.select_latest_by_machine_id(db, machine_id)
target_dir_str = latest_data_collect_history.processed_dir_path.split("-")[-1]  # yyyyMMdd文字列

# ここでは最新のデータ収集ではなく20210709190000のサンプルデータを使う
target_dir_str = "20210709190000"
shots_index = f"shots-{machine_id}-{target_dir_str}-data"

# ショットデータを取得するサンプル
dr = DataReader()
shot_df = dr.read_shot(shots_index, shot_number=1)

# print(shot_df.head())

# 特徴量を抽出するサンプル
# 本来はセンサーごとに設定したDSLを取得し適用
machine = CRUDMachine.select_by_id(db, machine_id)
sensors = machine.sensors

argstart, valstart, _ = extract_features(shot_df, 80.0, eval_dsl, sub_func=None, dslstr=machine.start_point_dsl)
print(argstart, valstart)

argmax, valmax, _ = extract_features(shot_df, 80.0, eval_dsl, sub_func=None, dslstr=machine.max_point_dsl)

print(argmax, valmax)

argbreak, valbreak, _ = extract_features(shot_df, 80.0, eval_dsl, sub_func=None, dslstr=machine.break_point_dsl)
print(argbreak, valbreak)
