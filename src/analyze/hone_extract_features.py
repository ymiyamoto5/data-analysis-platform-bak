# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
from .fft_tools import *


def max_load(d, spm, fs=100000, low=0, high=2000, r_window=19, Debug=False):
    """ 最大荷重点
    1系列のデータをリストで受け取り、最大荷重点のindexとvalueを返す。
    バンドパス→移動平均でノイズを除去後、最大点を検出する単純なアルゴリズムなので、
    バンドパス、移動平均のパラメタ調整が全て。
    :d (list)            荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :low (float)         バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :return (int,float)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({"o": np.array(d)})
    s, f, p = fft_spectrum(df.o, fs=fs)  # FFT
    df["b"] = bandpass_ifft(s, f, low, high).real  # バンドパス
    df["m"] = df.b.rolling(r_window).mean()  # 破断の影響を前方に出さないようcenter=Trueしない
    h = df["m"].argmax()
    if Debug is True:
        ax = df.plot(figsize=(10, 4), subplots=True, title="shot:%d ch:%s" % (shot, ch), alpha=0.3)
        plt.xlim(h - 300, h + 300)
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.m[h]


def extract_features(shot_data, spm, func, **kwargs):
    """ 特徴抽出ハンドラ関数
    変位をトリガーに切り出した1ショットのデータをpd.DataFrame(shot_data)として受け取り、
    抽出した特徴値を返す。
    shot_dataは4ch('load01','load02','load03','load04')固定であり、
    特徴値はindexと値をそれぞれ長さ4のリストとして返す。
    funcは特徴抽出関数のポインタであり、
    :shot_data (pd.DataFrame)   
    :spm (float)                荷重系列データ
    :func (*function)           荷重系列データ
    :**kwargs (可変キーワード引数)
    :return (list, list)        indexリスト, 値リスト
    """
    #     print(shot_data.head())
    argmax = []
    valmax = []
    for ch in ["load01", "load02", "load03", "load04"]:
        i, v = func(shot_data[ch], spm, **kwargs)
        argmax.append(i)
        valmax.append(v)

    return argmax, valmax


if __name__ == "__main__":
    """ この部分は大塚の作業環境依存
    """
    DATA_ROOT = "/data"

    from pathlib import Path

    p = Path(DATA_ROOT + "/H-One/20201127/shots/")
    flist = list(sorted(p.glob("shots_*.csv")))

    features = []
    for f in range(0, len(flist), 50):
        #     print(f,flist[f])
        shot = int(os.path.basename(flist[f])[6:9])

        df1 = pd.read_csv(flist[f])
        if len(df1) == 0:
            print("%s invalid" % flist[f])
            continue

        df1 = df1.rename(
            {"v1": "load01", "v2": "load02", "v3": "load03", "v4": "load04", "c1": "displacement"}, axis=1
        )

        argmax, valmax = extract_features(df1, 80.0, max_load)  # SPMここでは固定
        features.append([shot] + argmax + valmax + list(np.array(argmax).argsort() <= 1))

    features = pd.DataFrame(
        features,
        columns=[
            "shot",
            "argmax01",
            "argmax02",
            "argmax03",
            "argmax04",
            "valmax01",
            "valmax02",
            "valmax03",
            "valmax04",
            "b01",
            "b02",
            "b03",
            "b04",
        ],
    )
    print(features)
