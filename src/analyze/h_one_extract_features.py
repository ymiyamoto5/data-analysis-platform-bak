# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
import sys
from fft_tools import *

"""
開発環境(pandas 0.25/1.0)とテスト環境(pandas 0.21.1)の間で非互換。
df[b:e].a.argmax()のように、スライスしたサブセットにargmax()を適用した時、
pandas 0.21ではサブセット内の相対的なindexが返る。
argmaxではなくidxmaxを使えば、0.25/0.21共通の仕様に。

かつてpandasのargmaxはnumpy.argmaxを呼んでるだけだったので、
スライス後の相対的なindexを返していた。
それだと使いにくいのでスライス前の本来のindexを返すように変更したかったけど、
いきなりだと非互換出て困る人がいるだろうから、idxmaxを新設してargmaxはdeprecatedに。
だったらargmax廃止しちゃえば良いのに、その後どこかの時点でargmaxも
本来望ましい仕様に変更して、今はidxmaxとargmaxは同じ仕様に。
ということみたい。
結論としては、idxmax使っておけば、pandas0.21移行の環境であれば動くはず。
https://pandas-docs.github.io/pandas-docs-travis/reference/api/pandas.Series.argmax.html
https://stackoverflow.com/questions/47596390/can-i-use-idxmax-instead-of-argmax-in-all-cases
"""


def _idiff(x):
    # 必ずraw=Trueで呼ぶこと。
    # x は窓内の値が入った配列                                                                                                                                          # x[0]が最も古い、x[-1]が最も新しい値
    # 集計後の値を return する
    i_width = int(len(x) / 2)
    return x[-i_width:].mean() - x[:i_width].mean()


def breaking_varmax29(
    d, spm, low=0, high=8000, r_window=1, Debug=False, shot=999, ch="loadxx", debug_xlim=[-100, 100]
):
    """ 破断点
    

    """
    df = pd.DataFrame({"o": d})
    df["d"] = df.o.rolling(r_window, center=True, min_periods=1).mean()  # 移動平均
    df["v"] = df.d.diff().rolling(r_window, center=True, min_periods=1).mean()  # 速度
    df["a"] = df.v.diff().rolling(r_window, center=True, min_periods=1).mean()  # 加速度

    df["var9"] = df.o.rolling(9, center=True).var()
    df["var29"] = df.o.rolling(29, center=True).var()
    varmax9 = df.var9.idxmax()
    varmax29 = df.var29.idxmax()
    if varmax29 >= varmax9:  # 502全ch破綻,rollingの範囲をspmに連動させるか?  346:3, 731:3
        h = varmax9  # varmax29とvarmax9が一致 or 逆転した場合はvarmax9を採用、その範囲でmax採るより前倒した方が吉
    else:
        h = df[varmax29:varmax9]["a"].idxmin()  ####        601:ff2でvarmax29とvarmax9が一致,29を広げるのは逆効果

    if Debug is True:
        ax = df[["d", "var9", "var29", "v", "a"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d ch:%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[1].axvline(varmax9, color="r")
        ax[2].axvline(varmax29, color="r")
        ax[4].axvspan(varmax29, varmax9, color="g", alpha=0.3)
        ax[4].axvline(h, color="r")
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h, df.d[h]


def breaking_varmax29idiff(
    d, spm, fs=100000, low=0, high=8000, r_window=19, Debug=False, shot=9999, ch="loadxx", debug_xlim=[-100, 100]
):
    """ 破断点
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({"o": d})
    s, f, p = fft_spectrum(df.o, fs=fs)  # FFT
    df["d"] = bandpass_ifft(s, f, low, high).real  # バンドパス
    df["v"] = df.o.diff()  # 速度
    df["a"] = df.v.diff()  # 加速度
    df["v9"] = df.d.rolling(9, center=True).var() * -df.d.rolling(9, center=True).apply(_idiff)
    df["v29"] = df.d.rolling(29, center=True).var() * -df.d.rolling(29, center=True).apply(_idiff)
    varmax9idiff = df.v9.idxmax()
    varmax29idiff = df.v29.idxmax()
    if varmax29idiff >= varmax9idiff:  # varmaxにidiffをかけることで下降局面に絞る; 731:1
        h = varmax9idiff  #
    else:  #
        h = df[varmax29idiff:varmax9idiff]["a"].idxmin()  #

    if Debug is True:
        ax = df[["d", "v", "v29", "v9", "a"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[2].axvline(varmax29idiff, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[3].axvline(varmax9idiff, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[4].axvspan(varmax29idiff, varmax9idiff, color="g", alpha=0.3)
        ax[4].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.o[h]


def breaking_varmax29idiff_tmpfix(
    d, spm, fs=100000, low=0, high=8000, r_window=19, Debug=False, shot=9999, ch="loadxx", debug_xlim=[-100, 100]
):
    """ 破断点
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({"o": d})
    s, f, p = fft_spectrum(df.o, fs=fs)  # FFT
    df["d"] = bandpass_ifft(s, f, low, high).real  # バンドパス
    df["v"] = df.o.diff()  # 速度
    df["a"] = df.v.diff()  # 加速度
    df["v9"] = df.d.rolling(9, center=True).var() * -df.d.rolling(9, center=True).apply(_idiff)
    df["v29"] = df.d.rolling(29, center=True).var() * -df.d.rolling(29, center=True).apply(_idiff)
    varmax9idiff = df.v9.argmax()
    varmax29idiff = df.v29.argmax()
    h = varmax29idiff  # これなら確実に動くはず???
    #    if varmax29idiff >= varmax9idiff:                     # varmaxにidiffをかけることで下降局面に絞る; 731:1
    #        h = varmax9idiff                                  #
    #    else:                                                 #
    #        h = df[varmax29idiff:varmax9idiff]['a'].argmin()  #

    if Debug is True:
        ax = df[["d", "v", "v29", "v9", "a"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[2].axvline(varmax29idiff, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[3].axvline(varmax9idiff, c="r")
        # ax[2].axhline(criteria,c='g')
        ax[4].axvspan(varmax29idiff, varmax9idiff, color="g", alpha=0.3)
        ax[4].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.o[h]


def load_start(d, spm, r_window=399, Debug=False, shot=9999, ch="loadxx", debug_xlim=[-1000, 1500]):
    """ 荷重開始点 (速度変化版; 加速度ではない)
    最大荷重に至るまでの範囲の速度推移を標準化(論理的には初期0、荷重開始以降は1となる想定)し、
    この標準化速度が0.2を超えた最初の点を荷重開始点とする。
    この時、0.2超え検索の範囲を荷重最大点-1200とする。
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float)  最大開始点index, 荷重開始値

    ToDo: 検索範囲を決める1200の値はSPMによって大きく変わる。
          逆にSPMが正確にわかれば、かなり正確に特定できるはずなので、
          標準化加速度の閾値0.2ももっと小さくできるはず。
          現状は、低SPMではこの1200が狭すぎるので、坂道の途中を求めてしまう。
    
    """
    df = pd.DataFrame({"o": d})
    df["d"] = df.o.rolling(r_window, center=True, min_periods=1).mean()  # 移動平均
    df["v"] = df.d.diff().rolling(r_window, min_periods=1).mean()  # 速度

    argmax = df.d.idxmax()  # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.v[0 : df.d.idxmax()].max()
    l_min = df.v[100 : df.d.idxmax()].min()
    df["sv"] = (df.v - l_min) / (l_max - l_min)
    h = df[df.d.idxmax() - 1200 :][df.sv > 0.2].index[0]  # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    if Debug is True:
        plt.figure(figsize=(12, 5))
        ax = df[["d", "v", "sv"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[2].axhline(0.2, c="g")
        ax[2].axvspan(df.d.idxmax() - 1200, df.d.idxmax(), color="g", alpha=0.3)
        ax[2].set_ylim(-0.1, 1.1)
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])
        plt.show()

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h]


def load_start2(d, spm, r_window=399, Debug=False, shot=999, ch="loadxx", debug_xlim=[-1000, 1500]):
    """ 荷重開始点 (速度変化版 rev.2)
    速度に加え荷重値も開始:最大荷重の範囲を標準化(初期0、最大荷重1に向けて徐々に上昇)し、
    標準化荷重の下限から0.2を超えるまでの範囲を検索範囲とする。これによって、SPMの考慮は必須ではなくなった。
    この検索範囲の中で標準化速度が0.2を初めて超えた点を荷重開始点とする。

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用>  。                                           囲
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float)  最大開始点index, 荷重開始値

    ToDo: 荷重開始前の水平区間は、全体の傾向としてやや下降していることが多く、
          荷重下限は荷重開始の直前に来ることが多い。この場合、アルゴリズムはうまく機能するが、
          稀に荷重下限がショット開始付近になることがあり(shot#441,442,541)、この場合に0.2の閾値が怪しくなる。
          検索範囲及び標準化範囲を、標準化荷重が0.2を超えた点から遡って固定長(この場合はspmの考慮必要)とすることで、
          アルゴリズムとしては、より良好に機能すると思われる。
          しかしながら、荷重開始前の水平区間のゆらぎが、鋼板のたわみのようなものだとすると、
          このような考慮はむしろ特定される荷重開始点のゆらぎに繋がるのではないか?
    """
    df = pd.DataFrame({"o": d})
    df["d"] = df.o.rolling(r_window, center=True, min_periods=1).mean()  # 移動平均
    df["v"] = df.d.diff().rolling(r_window, min_periods=1).mean()  # 速度

    argmax = df.d.idxmax()  # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.d[argmax]
    l_min = df.d[100:argmax].min()
    df["sd"] = (df.d - l_min) / (l_max - l_min)  # 標準化変位
    l_max = df.v[0:argmax].max()
    # print(l_max)
    l_min = df.v[100:argmax].min()
    # print(l_min)   # これをできるだけ直前に持っていきたい
    df["sv"] = (df.v - l_min) / (l_max - l_min)

    #     h = df[df.d.argmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    sd_start = df[100 : df.d.idxmax()].sd.idxmin()  # 100:最大荷重の範囲の荷重最小点 -> sd_start
    sd_end = df[100 : df.d.idxmax()][df.sd > 0.2].index[0]  # 標準化変位が0.2を超えた -> sd_end
    h = df[sd_start:sd_end][df.sv > 0.2].index[0]  # sd_start:sd_endの範囲で、標準化速度が0.2を超えた最初の点
    if Debug is True:
        ax = df[["d", "sd", "v", "sv"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[1].set_ylim(-0.1, 1.1)
        ax[1].axvspan(sd_start, sd_end, color="g", alpha=0.3), ax[1].axhline(0.2, c="g")
        ax[3].set_ylim(-0.1, 1.1)
        ax[3].axhline(0.2, c="g")
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h]


def load_start3(d, spm, r_window=399, Debug=False, shot=999, ch="loadxx", debug_xlim=[-1000, 1500]):
    """ 荷重開始点 (加速度版)
    load_start2の方法で範囲を絞った後、加速度最大を採る

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用>  。                                           囲
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float)  最大開始点index, 荷重開始値

    ToDo: 402:4, 444:1, 601:2

    """
    df = pd.DataFrame({"o": d})
    df["d"] = df.o.rolling(r_window, center=True, min_periods=1).mean()  # 移動平均
    df["v"] = df.d.diff().rolling(r_window, center=True, min_periods=1).mean()  # 速度
    df["a"] = df.v.diff().rolling(r_window, center=True, min_periods=1).mean()  # 加速度

    argmax = df.d.idxmax()  # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.d[argmax]
    l_min = df.d[100:argmax].min()
    df["sd"] = (df.d - l_min) / (l_max - l_min)  # 標準化変位
    l_max = df.v[0:argmax].max()
    # print(l_max)
    l_min = df.v[100:argmax].min()
    # print(l_min)   # これをできるだけ直前に持っていきたい
    df["sv"] = (df.v - l_min) / (l_max - l_min)

    #     h = df[df.d.argmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    sd_start = df[100 : df.d.idxmax()].sd.idxmin()  # 100:最大荷重の範囲の荷重最小点 -> sd_start
    sd_end = df[100 : df.d.idxmax()][df.sd > 0.2].index[0]  # 標準化変位が0.2を超えた -> sd_end
    h = df[sd_start:sd_end].a.idxmax()  # sd_start:sd_endの範囲で、
    if Debug is True:
        ax = df[["d", "sd", "v", "sv", "a"]].plot(
            figsize=(10, 8),
            subplots=True,
            c="b",
            title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch),
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[1].set_ylim(-0.1, 1.1)
        ax[1].axhline(0.2, c="g")
        ax[1].axvspan(sd_start, sd_end, color="g", alpha=0.3)
        ax[3].set_ylim(-0.1, 1.1)
        ax[3].axhline(0.2, c="g")
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h]


def max_load(
    d, spm, fs=100000, low=0, high=2000, r_window=19, Debug=False, shot=9999, ch="loadxx", debug_xlim=[-1500, 1000]
):
    """ 最大荷重点
    1系列のデータをリストで受け取り、最大荷重点のindexとvalueを返す。
    バンドパス→移動平均でノイズを除去後、最大点を検出する単純なアルゴリズムなので、
    バンドパス、移動平均のパラメタ調整が全て。
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :low (float)         バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :return (int,float)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({"o": d})
    s, f, p = fft_spectrum(df.o, fs=fs)  # FFT
    df["b"] = bandpass_ifft(s, f, low, high).real  # バンドパス
    df["m"] = df.b.rolling(r_window).mean()  # 破断の影響を前方に出さないようcenter=Trueしない
    h = df["m"].idxmax()
    if Debug is True:
        ax = df.plot(
            figsize=(10, 4), subplots=True, title="%s shot:%d,ch=%s" % (sys._getframe().f_code.co_name, shot, ch)
        )
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')
        plt.xlim(h + debug_xlim[0], h + debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.m[h]


def extract_features(shot_data, spm, func, disp_chart=False, xlim=[0, 0], **kwargs):
    """ 特徴抽出ハンドラ関数
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
    :disp_chart (bool)                グラフ表示; ショットごとの元波形と特徴量を表示。
    :**kwargs (可変キーワード引数)    funcに指定した関数に対応した引数を指定
    :return (list, list)              indexリスト, 値リスト
    """
    #     print(shot_data.head())
    if spm is None:  # 最後のショットは次のショットが無いためspm計算不能, 80を想定する。
        spm = 80.0

    argmax = []
    valmax = []
    chs = ["load01", "load02", "load03", "load04"]
    for ch in chs:
        kwargs["ch"] = ch  # 可変キーワードにch追加
        i, v = func(np.array(shot_data[ch]), spm, **kwargs)
        argmax.append(i)
        valmax.append(v)

    if disp_chart:
        plt.figure(figsize=(12, 6))
        for c in range(len(chs)):
            plt.plot(shot_data[chs[c]], label=chs[c], alpha=0.3)  # plotはplotで、scatterはscatterで、それぞれcmapを順番に使うので、
            plt.scatter(
                [argmax[c]], [valmax[c]], marker="o", s=200, alpha=0.5
            )  # plotもscatterもcolorを明示しなければたまたま同じ色になる。
        if "shot" in kwargs:
            shot = kwargs["shot"]  # 可変キーワード変数から拝借; 掟破り
        else:
            shot = 9999
        plt.title("%s shot:%d" % (func.__name__, shot))
        plt.legend()
        if xlim[0] != 0 or xlim[1] != 0:
            plt.xlim(np.array(argmax).min() + xlim[0], np.array(argmax).max() + xlim[1])
        plt.show()

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

        # argmax,valmax = extract_features(df1, 80.0, max_load)    # SPMここでは固定
        # argmax,valmax = extract_features(df1, 80.0, breaking_varmax29)    # SPMここでは固定
        # argmax,valmax = extract_features(df1, 80.0, breaking_varmax29idiff)    # SPMここでは固定
        argmax, valmax = extract_features(df1, 80.0, breaking_varmax29idiff_tmpfix)  # SPMここでは固定
        # argmax,valmax = extract_features(df1, 80.0, load_start)    # SPMここでは固定
        argmax, valmax = extract_features(df1, 80.0, load_start3)  # SPMここでは固定
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
