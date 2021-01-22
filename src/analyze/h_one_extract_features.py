# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "./"))
import fft_tools as fft


def _idiff(x):
    # 必ずraw=Trueで呼ぶこと。
    # x は窓内の値が入った配列                                                                                                                                          # x[0]が最も古い、x[-1]が最も新しい値
    # 集計後の値を return する
    i_width = int(len(x) / 2)
    return x[-i_width:].mean() - x[:i_width].mean()


def breaking(d, spm, fs=100000, low=0, high=8000, r_window=19, Debug=False, shot=9999, ch="loadxx"):
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
    s, f, p = fft.fft_spectrum(df.o, fs=fs)  # FFT
    df["d"] = fft.bandpass_ifft(s, f, low, high).real  # バンドパス
    df["v"] = df.o.diff()  # 速度
    df["a"] = df.v.diff()  # 加速度
    df["v9"] = df.d.rolling(9, center=True).var() * -df.d.rolling(9, center=True).apply(_idiff)
    df["v29"] = df.d.rolling(29, center=True).var() * -df.d.rolling(29, center=True).apply(_idiff)
    varmax9idiff = df.v9.argmax()
    varmax29idiff = df.v29.argmax()
    if varmax29idiff >= varmax9idiff:  # varmaxにidiffをかけることで下降局面に絞る; 731:1
        h = varmax9idiff  #
    else:  #
        h = df[varmax29idiff:varmax9idiff]["a"].argmin()  #

    if Debug is True:
        ax = df[["d", "v", "a", "v9", "v29"]].plot(
            figsize=(10, 8), subplots=True, c="b", title="shot:%d,ch=%s" % (shot, ch)
        )
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        fft.plt.xlim(h - 100, h + 100)
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.o[h]


def load_start(d, spm, r_window=399, Debug=False, shot=9999, ch="loadxx"):
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

    argmax = df.d.argmax()  # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.v[df.d.argmax()]
    l_min = df.v[100 : df.d.argmax()].min()
    df["s"] = (df.v - l_min) / (l_max - l_min)
    h = df[df.d.argmax() - 1200 :][df.s > 0.2].index[0]  # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    if Debug is True:
        fft.plt.figure(figsize=(12, 5))
        ax = df[["d", "v", "s"]].plot(figsize=(10, 8), subplots=True, c="b", title="shot:%d,ch=%s" % (shot, ch))
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[2].axhline(0.2, c="g")
        ax[2].set_ylim(0, 1)
        fft.plt.show()

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h]


def load_start2(d, spm, r_window=399, Debug=False, shot=999, ch="loadxx"):
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

    argmax = df.d.argmax()  # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.d[argmax]
    l_min = df.d[100:argmax].min()
    df["sd"] = (df.d - l_min) / (l_max - l_min)  # 標準化変位
    l_max = df.v[0:argmax].max()
    # print(l_max)
    l_min = df.v[100:argmax].min()
    # print(l_min)   # これをできるだけ直前に持っていきたい
    df["sv"] = (df.v - l_min) / (l_max - l_min)

    #     h = df[df.d.argmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    sd_start = df[100 : df.d.argmax()].sd.argmin()  # 100:最大荷重の範囲の荷重最小点 -> sd_start
    sd_end = df[100 : df.d.argmax()][df.sd > 0.2].index[0]  # 標準化変位が0.2を超えた -> sd_end
    h = df[sd_start:sd_end][df.sv > 0.2].index[0]  # sd_start:sd_endの範囲で、標準化速度が0.2を超えた最初の点
    if Debug is True:
        ax = df[["d", "sd", "v", "sv"]].plot(figsize=(10, 8), subplots=True, c="b", title="shot:%d ch:%s" % (shot, ch))
        df.o.plot(ax=ax[0], alpha=0.3, c="black")
        ax[0].axvline(h, c="r")
        ax[1].set_ylim(-0.1, 1.1)
        ax[1].axvspan(sd_start, sd_end, color="g", alpha=0.3)
        ax[3].set_ylim(-0.1, 1.1)
        ax[3].axhline(0.2, c="g")

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h]


def max_load(d, spm, fs=100000, low=0, high=2000, r_window=19, Debug=False, shot=9999, ch="loadxx"):
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
    s, f, p = fft.fft_spectrum(df.o, fs=fs)  # FFT
    df["b"] = fft.bandpass_ifft(s, f, low, high).real  # バンドパス
    df["m"] = df.b.rolling(r_window).mean()  # 破断の影響を前方に出さないようcenter=Trueしない
    h = df["m"].argmax()
    if Debug is True:
        ax = df.plot(figsize=(10, 4), subplots=True, title="shot:%d ch:%s" % (shot, ch), alpha=0.3)
        fft.plt.xlim(h - 300, h + 300)
        ax[0].axvline(h, c="r")
        # ax[2].axhline(criteria,c='g')

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.m[h]


def extract_features(shot_data, spm, func, disp_chart=False, **kwargs):
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

    if disp_chart:
        fft.plt.figure(figsize=(12, 5))

    argmax = []
    valmax = []
    for ch in ["load01", "load02", "load03", "load04"]:
        kwargs["ch"] = ch  # 可変キーワードにch追加
        i, v = func(np.array(shot_data[ch]), spm, **kwargs)
        argmax.append(i)
        valmax.append(v)
        if disp_chart:
            fft.plt.plot(shot_data[ch], label=ch, alpha=0.3)  # plotはplotで、scatterはscatterで、それぞれcmapを順番に使うので、
            fft.plt.scatter([i], [v], marker="o", s=200, alpha=0.5)  # plotもscatterもcolorを明示しなければたまたま同じ色になる。

    if disp_chart:
        if "shot" in kwargs:
            shot = kwargs["shot"]  # 可変キーワード変数から拝借; 掟破り
        else:
            shot = 9999
        fft.plt.title("shot:%d" % shot)
        fft.plt.legend()
        fft.plt.xlim(np.array(argmax).min() - 1000, np.array(argmax).max() + 1000)
        fft.plt.show()

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
        # argmax,valmax = extract_features(df1, 80.0, breaking)    # SPMここでは固定
        argmax, valmax = extract_features(df1, 80.0, load_start)  # SPMここでは固定
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
