# -*- coding: utf-8 -*-
"""
 ==================================
  fft_tools.py
 ==================================

  Copyright(c) 2021 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""

try:
    __IPYTHON__  # type: ignore # Jupyter/IPythonでインタラクティブにグラフ描画可能な環境でのみ実行。__IPYTHON__が定義されていない環境ではNameErrorが発生し以下は実行されない。
    from bokeh.plotting import figure, show, output_notebook
    from bokeh.models import Range1d

    output_notebook()
except NameError:
    pass
import matplotlib.pyplot as plt
import numpy as np

# from envelope import *


def find_peaks(a, amp_thre=None, local_width=1, min_peak_distance=1, num_peaks=5):
    """
    閾値と極大・極小を判定する窓幅、ピーク間最小距離を与えて配列からピークを検出する。
    内部的にはピーク間距離は正負で区別して算出されるため、近接した正負のピークは検出される。
    :rtype (int, float)
    :amp_thre            ピーク検出閾値を明示
    :local_width  　     近傍何点の中でピークを検出するか
    :min_peak_distance   検出対象のピーク間の最小値
    :num_peaks           検出するピークの個数
    :return tuple (ndarray of peak indices, ndarray of peak value)
    """
    if amp_thre is None:  # amp_threが指定された場合はピーク検出閾値として採用
        amp_thre = np.std(a) * 5  # 指定されない場合は、標準偏差*10とする

    # amp_thre = 10
    # ピーク閾値を超えている点を検出候補とする
    idxs = np.where(np.abs(a) > amp_thre)[0]

    idxs_with_offset = idxs + local_width  # ピーク候補のindex配列をlocal_width分右にずらす
    a_extend = np.r_[[a[0]] * local_width, a, [a[-1]] * local_width]  # local_width個のダミー配列を元データの前後に追加 (最大/最小検出処理用)

    last_pos_peak_idx = 0
    last_neg_peak_idx = 0
    result_idxs = []

    for i in idxs_with_offset:
        is_local_maximum = a_extend[i] >= 0 and a_extend[i] >= np.max(
            a_extend[i - local_width : i + local_width + 1]
        )  # 最大値を検出
        is_local_minimum = a_extend[i] < 0 and a_extend[i] <= np.min(
            a_extend[i - local_width : i + local_width + 1]
        )  # 最小値を検出
        if is_local_maximum or is_local_minimum:
            if is_local_minimum:
                if i - last_pos_peak_idx > min_peak_distance:
                    result_idxs.append(i)
                    last_pos_peak_idx = i
            else:
                if i - last_neg_peak_idx > min_peak_distance:
                    result_idxs.append(i)
                    last_neg_peak_idx = i

    result_idxs = np.array(result_idxs) - local_width  # ずらした分を戻す
    pvalues = None
    if len(result_idxs) > 0:
        pvalues = np.array(a[result_idxs])  # indexでアクセスしたいのでnp.arrayにしておく
        sort_idx = np.argsort(pvalues)[::-1][0:num_peaks]  # argsort(昇順)を逆順にして先頭からnum_peaksまでを取る。
        return (result_idxs[sort_idx], pvalues[sort_idx])
    else:
        return ([], [])  # peak未検出の場合は空listを返す。
        # plot_spectrum()はlistの長さでpeak描画を判断。


# FFT、及びSTFTの関数定義
def fft_spectrum(
    x,
    fs,
    num_average=1,
    overlap=0.5,
    c=False,
    xrange=None,
    peak=False,
    amp_thre=None,
    min_peak_distance=1,
    num_peaks=5,
):
    """
    入力データをFFT処理しスペクトルに変換する。
    変換したスペクトルをグラフ描画(bokeh)するとともにスペクトルからpeakを検出する。
    戻り値はスペクトルとピークのリストであることに注意。
    グラフ描画におけるY軸はスペクトルの絶対値をそのまま表示している。plot_spectrum()とは
    異なっていることに注意。
    :x (list)            FFT処理の対象になる波形データ
    :fs (int)            サンプリング周波数(Hz)
    :num_average (int)   平均化回数
    :overlap (int)       平均化処理時のオーバーラップ。0.0-1.0の範囲で指定。
    :c (bool)            グラフ描画(bokeh)の有無
    :xrange (Range1d)        グラフ描画の範囲(初期値)
    :peak (bool)         peak検出の有無
    :amp_thre (list)     peak候補の閾値
    :min_peak_distance (int)   検出するpeak同士の最小距離(これ以上隣接していたら独立のpeakと見なさない)
    :return (list,list,list)  スペクトル, 周波数配列、ピーク

                        x
       --------------------------------
       --------------------                       --+
           --------------------                     | 平均化回数=4
               --------------------                 |
                   --------------------           --+
                   |              |   |
                   |              |   |
                   +--------------+   |
                   |  overlap=0.8     |
                   |                  |
                   +------------------+
                         data_len


    平均化回数=num_average(上図では4)、オーバーラップ=overlap(上図では0.8)とすると、
    全データ長(引数:x)と1回のFFT処理対象のデータ長の関係は、
        平均化処理時のデータ長 = 全データ長 / ((1-overlap)*num_average + overlap)
    となる。

    この関数が返すスペクトルは実効値スペクトルであり、そのまま合算したものがRMSになる。
       s,f,p = fft_spectrum(data,fs=FS)
       RMS = s.sum()
    虚部は捨てて、後半の折り返し部分も捨ててあるので、abs()や自乗平均平方根のような処理は不要である。
    特定の周波数帯域のみのRMSが必要な場合は、第二戻り値の周波数配列と組み合わせて必要な部分のみを
    検索して合算すれば良い。
    ただし、スペクトルの周波数解像度が充分でない場合、RMSの誤差が非常に大きく(ピークの裾野が広くなりすぎる)ため、
    実用的な値とは言えない。RMSは元波形の時系列データから求めるべきである。
      (Jupyter "FFTによるスペクトル算出方法"参照のこと)
    """
    fs = float(fs)

    data_len = int(len(x) / ((1 - overlap) * num_average + overlap))  # 1回のFFT処理対象となるデータ長
    # print('data_len:',data_len)
    frq = np.fft.fftfreq(data_len, 1.0 / fs)  # 算出されるスペクトル配列の周波数インデックス
    # frq = frq[0:int(data_len/2)]           # 後半半分は要らないので捨てる

    spectrum_array = []
    for i in range(num_average):
        start_idx = int(i * (1 - overlap) * data_len)
        # print('start index:',start_idx)
        # print('end index:',start_idx + data_len)
        d = x[start_idx : start_idx + data_len]
        size = data_len

        dt1 = np.fft.fft(d)  # スペクトル配列
        # dt1 = (dt1[0:int(size/2)] / (size/2)) / np.sqrt(2)    # スペクトル配列の個々の値をデータ長の1/2で割る
        spectrum_array.append(dt1)  # スペクトルをリストに追加

    s = np.vstack(spectrum_array).mean(axis=0)  # スペクトルのリストを連結してarrayを生成、スペクトル値の算術平均を求める。
    # s = np.abs(dt1)
    # x0 = [0.0]*len(x)
    # x1 = [0.0]*len(x)
    # x2 = [0.0]*len(x)

    peaks = []
    if peak:
        peaks, pvalues = find_peaks(s, amp_thre=amp_thre, min_peak_distance=min_peak_distance, num_peaks=num_peaks)
    # if peak:
    #    print(np.std(x[1:]))
    #    for i in range(1,len(x)-1):               #
    #        x0[i] = np.mean(x[i-1:i+1])            # 平滑化
    #    for i in range(1,len(x)-1):               # 超低周波無視
    #        x1[i] = x0[i+1] - x0[i]                 # 一階微分
    #    for i in range(1,len(x)-1):               # 超低周波無視
    #        x2[i] = x1[i+1] - x1[i]               # 二階微分
    #        if np.abs(x2[i]) > np.std(x[1:])*30:    # 超低周波無視
    #            peaks.append(i)

    if c:
        p = figure(height=300)  # bokehの画像サイズ
        p.line(frq, abs(s), alpha=1)
        if xrange is None:
            xrange = Range1d(0, fs / 2)
        if peak:
            r = (xrange.end - xrange.start) / 50
            for i in range(len(peaks)):
                # print(frq[i],x[i])
                # p.circle(x=frq[i],y=x[i],radius=5,color='red',fill_alpha=0.1)
                p.circle(x=frq[peaks[i]], y=abs(dt1[peaks[i]]), radius=r, color="red", fill_alpha=0.1)
        p.x_range = xrange
        p.y_range = Range1d(0, max(abs(dt1[5 : np.int(len(dt1) / 2)])) * 1.2)  # 超低周波はオーバーフローして構わない
        # p.set(x_range=xrange)
        # p.set(y_range=Range1d(0,max(abs(dt1[5:np.int(len(dt1)/2)]))*1.2))  # 超低周波はオーバーフローして構わない
        show(p)

    return (s, frq, peaks)


def plot_raw(data, fs, xlim=[], ylim=[]):
    x = np.arange(0, len(data)) / fs
    plt.plot(x, data, label="")
    if xlim:
        plt.xlim(xlim)
    if ylim:
        plt.ylim(ylim)
    plt.xlabel("sec")
    plt.ylabel("m/s^2")


def plot_spectrum(s, frq, fs=0, data_len=0, peaks=[], label="", xlim=None, ylim=None, marker=""):
    """
    FFTスペクトルをグラフ描画する。
    matplotlibによる画像生成。javascriptによるinteractiveな描画はfft_spectrum()参照。
    :s (list)            スペクトル (floatのリスト, 虚数を含んだもので構わない)
    :fs (int)            元データのサンプリング周波数(Hz)
    :frq (list)          周波数配列
    :data_len (int)      データ長 (スペクトルの長さではなく、元データのデータ長)
    :peaks (list)        ピークのインデックスを含むリスト
    :label (string)      データ系列を表す文字列(legendに書かれる, グラフのタイトルではない)
    :xlim (list)         グラフ上のxlimを周波数で指定
    :ylim (list)         ylim
    """
    # if xlim is None:
    #    xlim = [0,fs/2]
    # plt.plot(np.arange((fs/2)/len(s)*xlim[0],(fs/2)/len(s)*xlim[1],(fs/2)/len(s)),np.abs(s)[xlim[0]:xlim[1]], label=label);
    # if frq is None:
    #    xrange = np.arange(xlim[0],xlim[1],(fs/2)/len(s))
    # else:
    #    xrange = frq
    # xlen = len(xrange)
    # ystart = int(xlim[0]/((fs/2)/len(s)))
    # plt.plot(np.arange(xlim[0],xlim[1],(fs/2)/len(s)),np.abs(s)[ystart:ystart + xlen], label=label);
    # plt.plot(frq,np.abs(s)[ystart:ystart + xlen], label=label); plt.xlim(xlim)

    # plt.plot(frq,np.abs(s)/(len(s)/2), label=label)
    plt.plot(frq[0 : int(len(s) / 2)], np.abs(s[0 : int(len(s) / 2)]) / (len(s) / 2), label=label, marker=marker)  # 暫定
    if xlim is None:
        xlim = [0, int(frq.max() * 2 / 2.56)]
    plt.xlim(xlim)

    if ylim is not None:
        plt.ylim(ylim)

    # 検出したピークを示すハイライト表示
    if len(peaks) > 0:
        h_width = (xlim[1] - xlim[0]) * 0.01  # X軸の値範囲からpeakを示すハイライトの描画幅を決定
        for i in range(len(peaks)):
            p = peaks[i]
            # axvspanは、何故かxlimの範囲指定より優先してしまう
            if frq[p] > xlim[1]:  # xlimで指定した描画範囲の右端より大きい
                continue
            if frq[p] < xlim[0]:  # xlimで指定した描画範囲の左端より小さい
                continue
            plt.axvspan(frq[p] - h_width, frq[p] + h_width, facecolor="r", alpha=0.3, linewidth=0)

    plt.legend()
    plt.xlabel("Hz")
    plt.ylabel("m/s^2")
    if ylim:
        plt.ylim(ylim[0], ylim[1])

    return frq[0 : int(len(s) / 2)], np.abs(s[0 : int(len(s) / 2)]) / (len(s) / 2)


def rms_raw(x):
    """
    入力データのRMSを算出する。

    RMS(root mean squre)は振動波形の積分値の時間平均であり、
    全サンプリングデータの自乗平均平方根として求められる。
    入力に複素数(スペクトルのケースを想定)があり得るので、絶対値の自乗としている。

    :x (list)   (主に振動センサーから得た加速度時間波形データを想定しているが基本的には何でも)数値のリスト
    """
    return np.sqrt(np.mean(np.abs(x) ** 2))


def rms_spectrum(spectrum, freq=None, lo=0, hi=0, is_v=False):
    """
    FFTスペクトルからRMSを算出する。

    パーセバルの定理により、FFTスペクトルの平方の総和は、元波形の平方の総和に等しい。
    これによりFFTスペクトルからもRMSを求めることができる。
    その前提には、FFTスペクトル長が元波形のデータ長と一致していることがある。
    また、複数の周波数成分の合算としてのRMSは、その位相差により増幅/相殺され、
    位相情報を持つ虚部が重要となる。従って、
    この関数の入力とするスペクトルは、実部/虚部を含み元波形と同一の長さを持つ
    完全なスペクトルでなければならない。
    後続の処理にて有効となる、1/2、もしくは1/2.56の長さのスペクトルでは、
    正しいRMS値を算出することができない。

    :spectrum (list)  FFTスペクトル fft_spectrum()の戻り値[0]を想定
    :freq (list)      周波数リスト  fft_spectrum()の戻り値[1]を想定
    :lo (float)       RMS算出の対象周波数下限
    :hi (float)       RMS算出の対象周波数上限
    :is_v (bool)      速度RMSを算出する。defaultでは加速度RMSを算出。
    """
    #
    # スペクトル算出→RMS計算→グラフ描画→帯域別RMS のように使いまわしが頻繁に発生するので、
    # 入力を汚染してはならない。
    s = np.copy(spectrum)
    f = None
    if lo < 0:
        lo = 0
    if hi < 0:
        hi = 0
    if freq is not None:
        f = np.copy(freq)
    if is_v:
        f[np.where(f == 0.0)] = f[np.where(f == 0.0)[0] + 1] / 2  # divide by zeroを避けるため
        s = s / (2 * np.pi * np.abs(f)) * 1000  # スペクトルを速度スペクトルに変換

    """
    サンプリング周波数:10Hz, データ長:10だったとすると、FFTスペクトルの有効な上限周波数は、
    サンプリング周波数の1/2である5Hzとなり、この時np.fft.fftfreq()は、
    以下のように-5から4の周波数配列を生成する。

      fft_spectrum(np.random.randn(10),fs=10)
      (array([ 4.00295636 +0.00000000e+00j, -2.96264684 +3.18950207e+00j,
           2.08720666 +1.08505794e+00j, -1.72787649 -3.84286172e+00j,
           5.42082684 +1.47552086e+00j,  1.32549463 -5.55111512e-15j,
           5.42082684 -1.47552086e+00j, -1.72787649 +3.84286172e+00j,
           2.08720666 -1.08505794e+00j, -2.96264684 -3.18950207e+00j]),
      array([ 0.,  1.,  2.,  3.,  4., -5., -4., -3., -2., -1.]),
      [])
    
    ここで2〜3Hzの帯域RMSを求めたい場合、以下のように正負両方の該当周波数範囲の
    スペクトルを足し込む必要がある。
       0, 1, 2, 3, 4,-5,-4,-3,-2,-1
             ****          *****
    以下では、この処理をrms_flat()に行わせるため、該当以外の周波数範囲に0を代入している。
    rms_flat()では全要素の自乗平均平方根を求めるため、配列の長さを変えてはならない。
    """
    if (f is not None) & (hi > 0):
        s[np.where(((f >= 0) & (f < lo)) | (f > hi))] = 0
        s[np.where(((f <= 0) & (f > -lo)) | (f < -hi))] = 0

    return rms_raw(s) / np.sqrt(len(s))


# STFT (Short-Time Fourier Transform)
def stft(x, fs, n_fft=128, hop=None):
    """STFT (Short-Time Fourier Transform)
    :x (int, float)      生波形データ
    :fs (int)            サンプリング周波数(Hz)
    :n_fft (int)         1回のFFT処理対象となる窓幅 (default=128)
    :hop (int)           窓のずらし幅 (default=n_fft/4)
    :return numpy.array  スペクトルのリストで表現されるスペクトログラム
    """
    a = []
    # n_fft = 128
    if hop is None:
        hop = int(n_fft / 4)
    out_len = int((len(x) - n_fft) / hop)
    hammingWindow = np.hamming(n_fft)
    # hammingWindow = np.ones(n_fft)     # hamming window無効化
    for i in range(out_len):
        b = i * hop  # windowスタート位置
        e = b + n_fft  # windowエンド位置
        s = fft_spectrum(x[b:e] * hammingWindow, fs)[0]
        a.append(abs(s[int(len(s) / 2) :]))  # window範囲をFFT処理して得られたスペクトルを追加
    na = np.transpose(np.array(a))
    # sns.heatmap(na.T)
    return na


if __name__ == "__main__":
    x = np.linspace(0, 6 * np.pi, 300)
    y = np.sin(x)
    y += np.sin(2 * x)

    sgm = stft(y, fs=100)  # とりあえずエラーにならなければOK
    print(sgm.shape)


def bandpass_ifft(s, f, low, high):
    """FFTによるスペクトル上で特定の周波数領域をカットし、
       逆FFTすることでバンドパスフィルタとして機能する。
       scipyのFIRフィルタでは元波形に対する位相ズレが発生するが、
       この方法では発生しない。減衰性能も優れていると思われる。
       引数のs,fはfft_spectrum()の戻り値を想定しており、
       虚数を含んだものでなければならない。
    :s (list)          スペクトル (floatのリスト, 虚数を含んだものが必要)
    :f (list)          周波数配列
    :low               下限周波数
    :high              上限周波数
    :return  numpy.array   バンドパス後の時系列データ
    """
    ss = s.copy()
    ss[np.where(np.abs(f) < low)] = 0
    ss[np.where(np.abs(f) > high)] = 0
    d_ifft = np.fft.ifft(ss)

    return d_ifft
