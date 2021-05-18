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
結論としては、idxmax使っておけば、pandas0.21以降の環境であれば動くはず。
https://pandas-docs.github.io/pandas-docs-travis/reference/api/pandas.Series.argmax.html
https://stackoverflow.com/questions/47596390/can-i-use-idxmax-instead-of-argmax-in-all-cases
"""

def _rms(x):
    return np.sqrt(np.mean(np.abs(x)**2))

def _idiff(x):
    # 必ずraw=Trueで呼ぶこと。
    # x は窓内の値が入った配列                                                                                                                                          # x[0]が最も古い、x[-1]が最も新しい値
    # 集計後の値を return する
    i_width = int(len(x)/2)
    return x[-i_width:].mean() - x[:i_width].mean()

NARROW_PADDING = 50

def narrowing_v4min_mab(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    narrowing_v4min_maで行っている移動平均により、
    break throughを特定するための速度極小点は前方(左)にずれる。
    これを補正するため、速度移動平均の極小点前後を範囲として、
    移動平均前の速度を再検索して極小点を検出する。

    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: 
    """
    RW1 = 15; RW2 = 39
    df = shot_df.copy()
    df['v15_01'] = df['load01'].rolling(RW1,center=False).mean().diff()
    df['v15_02'] = df['load02'].rolling(RW1,center=False).mean().diff()
    df['v15_03'] = df['load03'].rolling(RW1,center=False).mean().diff()
    df['v15_04'] = df['load04'].rolling(RW1,center=False).mean().diff()    
    df['v15'] = df['v15_01'] + df['v15_02'] + df['v15_03'] + df['v15_04'] 
    df['v15ma'] = df['v15'].rolling(RW2,center=True).mean()

    ma_min = df['v15ma'].idxmin()
    var_end = df['v15'][ma_min-20:ma_min+20].idxmin()
    var_start = var_end-20

    
    if disp_narrowing == True:
        plt.figure(figsize=(12,6))
        ax1 = plt.subplot(511)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(512,sharex=ax1)
        df[['v15_01','v15_02','v15_03','v15_04']].plot(ax=ax2)        
        ax3 = plt.subplot(513,sharex=ax1)
        df[['v15']].plot(ax=ax3)
        ax4 = plt.subplot(514,sharex=ax1)
        df[['v15ma']].plot(ax=ax4)
        ax3.axvspan(ma_min-20,ma_min+20,color='g',alpha=.2)
        ax1.axvspan(var_start,var_end,color='g',alpha=.2)
        ax3.axvline(var_end,color='r',alpha=.5)
        ax4.axvline(ma_min,color='r',alpha=.5)        
#         plt.xlim([var_start-1000,var_end+1500]);
        plt.xlim([var_start-500,var_end+1000]);        
        plt.suptitle('15 points velocity / shifted vrms shot:%d'%shot)
        plt.show()

    return var_start, var_end

def narrowing_v4min_ma(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    narrowing_v4minにおいて破断後500-1000point時点で発生するたわみ同期による
    速度極小を補正。
    たわみ同期による速度変化は、かなり規則正しい周期変動を示しており、
    適切な移動平均処理により軽減、補正できる。
    目的の破断時の速度変化の波長は、たわみ同期によるもののおよそ2倍程度あり、
    分離が可能。

    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: 
    """
    RW = 15
    df = shot_df.copy()
    df['v15_01'] = df['load01'].rolling(RW,center=False).mean().diff()
    df['v15_02'] = df['load02'].rolling(RW,center=False).mean().diff()
    df['v15_03'] = df['load03'].rolling(RW,center=False).mean().diff()
    df['v15_04'] = df['load04'].rolling(RW,center=False).mean().diff()    
    df['v15'] = df['v15_01'] + df['v15_02'] + df['v15_03'] + df['v15_04'] 
    df['v15ma'] = df['v15'].rolling(39,center=True).mean()

    var_end = df['v15ma'].idxmin()
    var_start = var_end-20

    
    if disp_narrowing == True:
        plt.figure(figsize=(12,6))
        ax1 = plt.subplot(511)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(512,sharex=ax1)
        df[['v15_01','v15_02','v15_03','v15_04']].plot(ax=ax2)        
        ax3 = plt.subplot(513,sharex=ax1)
        df[['v15']].plot(ax=ax3)
        ax4 = plt.subplot(514,sharex=ax1)
        df[['v15ma']].plot(ax=ax4)
        ax1.axvspan(var_start,var_end,color='g',alpha=.2)
        ax3.axvline(df['v15'].idxmin(),color='r',alpha=.5)
        ax4.axvline(df['v15ma'].idxmin(),color='r',alpha=.5)        
#         plt.xlim([var_start-1000,var_end+1500]);
        plt.xlim([var_start-500,var_end+1000]);        
        plt.suptitle('15 points velocity / shifted vrms shot:%d'%shot)
        plt.show()

    return var_start, var_end

def narrowing_v4min_vrms(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    narrowing_v4minにおいて破断後500-1000point時点で発生するたわみ同期による
    速度極小を補正するため、
    4ch速度のRMSを算出し、後方(右)シフトして除算する。
    動きの緩やかな区間から突然発生した動きを強調する効果を期待。

    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: たわみが同期した瞬間に最大波高になるケースには対応できない。
    """
    RW = 15
    df = shot_df.copy()
    df['v15_01'] = df['load01'].rolling(RW,center=False).mean().diff()
    df['v15_02'] = df['load02'].rolling(RW,center=False).mean().diff()
    df['v15_03'] = df['load03'].rolling(RW,center=False).mean().diff()
    df['v15_04'] = df['load04'].rolling(RW,center=False).mean().diff()    
    df['v15'] = df['v15_01'] + df['v15_02'] + df['v15_03'] + df['v15_04'] 
    df['vrms'] = (df['v15'].rolling(20,center=True).apply(_rms).shift(55) + .5) ** 2
    df['v15/vrms'] = df['v15'] / df['vrms']
    
    var_end = df['v15/vrms'].idxmin()
    var_start = var_end-20

    
    if disp_narrowing == True:
        plt.figure(figsize=(12,6))
        ax1 = plt.subplot(511)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(512,sharex=ax1)
        df[['v15_01','v15_02','v15_03','v15_04']].plot(ax=ax2)        
        ax3 = plt.subplot(513,sharex=ax1)
        df[['v15']].plot(ax=ax3)
        ax4 = plt.subplot(514,sharex=ax1)
        df[['vrms']].plot(ax=ax4)
        ax5 = plt.subplot(515,sharex=ax1)
        df[['v15/vrms']].plot(ax=ax5)
        ax1.axvspan(var_start,var_end,color='g',alpha=.2)
        ax3.axvline(df['v15'].idxmin(),color='g',alpha=.5)
        plt.xlim([var_start-1000,var_end+1500]);
        plt.suptitle('15 points velocity / shifted vrms shot:%d'%shot)
        plt.show()

    return var_start, var_end

def narrowing_varch_v4min(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    narrowing_v4minにおいて破断後500-1000point時点で発生するたわみ同期を
    処理対象外にするため、
    narrowing_var_ch相当の処理で大まかに破断前後を切り出し、
    さらにnarrowing_v4minで範囲を限定する。

    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: 
    """
    SVAR_CRITERIA = 0.2   # 0.3だと破断後になるケースあり(shot#425)
    RW=15
    df = shot_df.copy()
    df['var_raw'] = df[['load01','load02','load03','load04']].var(axis=1)
    df['var'] = df['var_raw'].rolling(49,min_periods=1,center=True).mean()
    l_max = df['var'].max()
    l_min = df['var'].min()
    df['svar'] = (df['var'] - l_min) / (l_max - l_min)
    df['bool'] = (df['svar']>SVAR_CRITERIA).astype(int)         # 0.1だと荷重開始点で反応するものが10件くらい
    upward_list = df[df['bool'].diff()==1].index   # diff()を取って、1になるのは上向きに跨いだポイント
    if len(upward_list) > 0:
        s_start = upward_list[0]
    else:
        s_start = df.index[0]    # 分散が.2以上にならないケース; 標準化してるのであり得ない
    downward_list = df[df['bool'].diff()==-1].index   # diff()を取って、-1になるのは下向きに跨いだポイント
    if len(downward_list) > 0:
        s_end = downward_list[0]                        # 0.2を超えた最初の山の範囲がvar_start:var_end,  var_endが広すぎるケースがほとんど
    else:
        s_end = np.min([df.index[-1],s_start+300])    # 分散が.2以下に降りてこないケース; これはあり得る。

    df['v15_01'] = df['load01'].rolling(RW,center=False).mean().diff()
    df['v15_02'] = df['load02'].rolling(RW,center=False).mean().diff()
    df['v15_03'] = df['load03'].rolling(RW,center=False).mean().diff()
    df['v15_04'] = df['load04'].rolling(RW,center=False).mean().diff()    
    df['v15'] = df['v15_01'] + df['v15_02'] + df['v15_03'] + df['v15_04'] 

    var_end = df['v15'][s_start:s_end].idxmin()    
    var_start = var_end-20              # 非破断側最大荷重からbreak throughまで20pointと想定
    
    if disp_narrowing == True:
        plt.figure(figsize=(12,10))
        ax1 = plt.subplot(611)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(612,sharex=ax1)
        df[['var_raw']].plot(ax=ax2)
        ax3 = plt.subplot(613,sharex=ax1)
        df[['svar']].plot(ax=ax3)
        ax3.axvspan(s_start,s_end,color='r',alpha=.2)
        ax3.axhline(SVAR_CRITERIA,color='g',alpha=.5)

        ax4 = plt.subplot(614,sharex=ax1)
        df[['load01','load02','load03','load04']].plot(ax=ax4)
        ax5 = plt.subplot(615,sharex=ax1)
        df[['v15_01','v15_02','v15_03','v15_04']].plot(ax=ax5)        
        ax6 = plt.subplot(616,sharex=ax1)
        df[['v15']].plot(ax=ax6)
        ax4.axvspan(var_start,var_end,color='g',alpha=.2)
        ax6.axvline(df['v15'].idxmin(),color='g',alpha=.5)
        ax1.axvspan(var_start,var_end,color='g',alpha=.2)

        plt.xlim([var_start-1000,var_end+500]);      
        plt.suptitle('var on 4ch / 15points velocity  shot:%d'%shot)
        plt.show()

    return var_start, var_end



def narrowing_v4min(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    破断点は、非破断側最大荷重点と破断後の荷重最小点(break through)の間に必ずある。
    この区間を特徴づけているのは、4ch揃って一斉に下方に移動していることであり、
    かつ、この一斉落下区間の長さは、SPMによらず一定であると思われる。
    であれば、後方15point時点との差分が4chとも最大となる点がbreak throughとなるはず。
    
    この考え方の直接的な実装は、15point幅のrolling windowの両端の差分取得
       df['load01'].rolling(15).apply(lambda x: x[-2:].mean() - x[:1].mean())
    であるが、lambdaのため負荷が高い。15point幅での移動平均後の階差
       df['load01'].rolling(15).mean().diff()
    で、ほぼ同等の効果が得られるため、これで代用する。また、
       df['load01'].rolling(15,center=False).mean().diff()
    rolling windowの範囲を処理対象pointから後方15point(center=False)とすることで、
    この値が最小となった点が後方15pointの下向き速度最大、即ちbreak throughとなる。
    このロジックで特定したbreak bhroughから前方15pointの範囲を
    検索範囲限定区間として返す。

    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: 
    """
    RW = 15
    df = shot_df.copy()
    df['v15_01'] = df['load01'].rolling(RW,center=False).mean().diff()
    df['v15_02'] = df['load02'].rolling(RW,center=False).mean().diff()
    df['v15_03'] = df['load03'].rolling(RW,center=False).mean().diff()
    df['v15_04'] = df['load04'].rolling(RW,center=False).mean().diff()    
    df['v15'] = df['v15_01'] + df['v15_02'] + df['v15_03'] + df['v15_04'] 
    
    var_start = df['v15'].idxmin()-20
    var_end = df['v15'].idxmin()
    
    if disp_narrowing == True:
        plt.figure(figsize=(12,6))
        ax1 = plt.subplot(311)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(312,sharex=ax1)
        df[['v15_01','v15_02','v15_03','v15_04']].plot(ax=ax2)        
        ax3 = plt.subplot(313,sharex=ax1)
        df[['v15']].plot(ax=ax3)
        ax1.axvspan(var_start,var_end,color='g',alpha=.2)
        ax3.axvline(df['v15'].idxmin(),color='g',alpha=.5)
        plt.xlim([var_start-1000,var_end+500]);
        plt.suptitle('15 points velocity  shot:%d'%shot)
        plt.show()

    return var_start, var_end


def narrowing_var_ch(shot_df,disp_narrowing = False,shot=9999):
    """ 検索範囲限定のためのヘルパー関数 (破断点専用)
    荷重4ch(load01,load02,load03,load04)を含むshot dataを受け取り、
    4ch間の分散を考慮することにより、最小限の検索範囲を返す。
    破断の前に、破断側/非破断側間の同期が崩れ、分散が増大することを利用している。
    
    :shot_df (pd.DataFrame)     shotデータを含むDataFrame
    :disp_narrowing (bool)      グラフ表示
    :shot (int)                 shot番号
    :return (int,int)           検索範囲の左端と右端のindex

    ToDo: 341(破断前のch間分散が極端に小さいケース; 破断/非破断の判別は辛うじてできている)
    """
    SVAR_CRITERIA = 0.2   # 0.3だと破断後になるケースあり(shot#425)
    df = shot_df.copy()
    df['var_raw'] = df[['load01','load02','load03','load04']].var(axis=1)
    df['var'] = df['var_raw'].rolling(49,min_periods=1,center=True).mean()
    l_max = df['var'].max()
    l_min = df['var'].min()
    df['svar'] = (df['var'] - l_min) / (l_max - l_min)
    df['bool'] = (df['svar']>SVAR_CRITERIA).astype(int)         # 0.1だと荷重開始点で反応するものが10件くらい
    upward_list = df[df['bool'].diff()==1].index   # diff()を取って、1になるのは上向きに跨いだポイント
    if len(upward_list) > 0:
        var_start = upward_list[0]
    else:
        var_start = df.index[0]    # 分散が.2以上にならないケース; 標準化してるのであり得ない
    downward_list = df[df['bool'].diff()==-1].index   # diff()を取って、-1になるのは下向きに跨いだポイント
    if len(downward_list) > 0:        
        var_end = downward_list[0]                        # 0.2を超えた最初の山の範囲がvar_start:var_end,  var_endが広すぎるケースがほとんど
    else:
        var_end = np.min([df.index[-1],var_start+300])    # 分散が.2以下に降りてこないケース; これはあり得る。

    if disp_narrowing == True:
        plt.figure(figsize=(12,6))
        ax1 = plt.subplot(311)
        df[['load01','load02','load03','load04']].plot(ax=ax1)
        ax2 = plt.subplot(312,sharex=ax1)
        df[['var_raw']].plot(ax=ax2)
        ax3 = plt.subplot(313,sharex=ax1)
        df[['svar']].plot(ax=ax3)
        ax3.axvspan(var_start,var_end,color='r',alpha=.2)
        ax3.axhline(SVAR_CRITERIA,color='g',alpha=.5)
        plt.xlim([var_start-1500,var_end+800]);
        plt.suptitle('variance on 4ch  shot:%d'%shot)
        plt.show()

    return var_start, var_end

def breaking_vmin_amin(d, spm, fs=100000,low=0, high=8000,r_window=1,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-50,50]):
    """ 破断点
    narrowing_v4min/narrowing_varch_v4minと必ずセットで使用のこと。
    速度最小点以前の加速度最小点、というのがこのアルゴリズムの全てであり、
    非破断側最大点からbreak throughまでの範囲が入力データとして与えられることを前提としている。
       d:     元波形に対して0-8000Hzのバンドパス
       v:     速度(dを微分)
       a:     加速度(vを微分)

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ>未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大荷重点index, 最大荷重値, 検索範囲終端までの距離

    """
    df = pd.DataFrame({'o':d})

    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['d'] = bandpass_ifft(s,f,low,high).real

    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度

    vmin = df.v[NARROW_PADDING:-NARROW_PADDING].idxmin()        # 速度最小点
    if vmin == NARROW_PADDING:
        h = vmin
    else:
        h = df.a[NARROW_PADDING:vmin].idxmin()    # 速度最小点以前の範囲の加速度最小点

    if Debug is True:
        ax = df[['o','d','v','a']].plot(figsize=(10,8),subplots=True,c='b',
                                   title='%s shot:%d ch:%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[2].axvline(vmin,color='r')         
        ax[3].axvline(h,color='r'); ax[3].axvspan(NARROW_PADDING,vmin,color='g',alpha=.2)
        plt.xlim(h-NARROW_PADDING+debug_xlim[0],h+NARROW_PADDING+debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h, df.d[h], df.index[-1] - NARROW_PADDING - h

def breaking_var_vrms(d, spm, fs=100000,low=0, high=8000,r_window=1,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    29点移動分散の最大点(varmax)と5点移動RMSの最大点(rmsmax)に挟まれた範囲の加速度最小点を返す。
       d:       元波形に対して0-8000Hzのバンドパス
       var29:   29点移動分散
       var29_v: var29 * 速度<=0  速度が負の区間のみ有効
       vrms:    速度RMS(速度5点実効値)
       v:       速度(dを微分)
       a:        加速度(vを微分)

    移動分散は、移動平均と同様にrolling windowの範囲に分散を適用する手法。
    分散の増大はwindow内の値の変化が大きくなることを意味し、破断による急落を含む区間が大きくなる。
    windowを広め(29区間)に取ることで、ピークが破断の手前に来ることを期待。
    移動RMSも同様に、rolling windowの範囲に速度RMSを適用。
    破断の衝撃による振動エネルギー(荷重センサーだが)の増大が、破断後の速度RMSピークとして現れることを期待している。

    実際には、速度RMSピークは期待よりも後方に現れることがしばしばあり、
    最小加速度検索範囲の右端は、[ 速度RMS最大点、速度最小点、荷重最小点、移動分散最小点+50 ]の中の最も左にある点としている。

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :shot (int)          デバッグ表示用
    :ch (str)            デバッグ表示用
    :return (int,float,*)  最大荷重点index, 最大荷重値

    ToDo:  502, 327:3
    """
    df = pd.DataFrame({'o':d})
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['d'] = bandpass_ifft(s,f,low,high).real
    df = df[NARROW_PADDING:-NARROW_PADDING].reset_index()                           # FFT後のデータ両端は信用できないのでPADDING分を切り捨て
    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度

    df['var29'] = df.o.rolling(29,center=True,min_periods=1).var()                  # 29点移動分散
    df['var29_v'] = df.var29 * (df.v <= 0).astype(int)                              # 速度が負の区間に限定
    df['vrms'] = df.v.rolling(5, center=True,min_periods=1).apply(_rms)             # 速度RMS

    varmax = df.var29_v.idxmax()    
    rmsmax = np.min([df.vrms.idxmax(),df.d.idxmin(),df.v.idxmin(),varmax+50])
    if varmax >= rmsmax:                          # 
        h = rmsmax                                  # varmax29の考え方を踏襲しているが、このケースは範囲逆転して最小加速度の方が良いかも。
    else:
        h = df[varmax:rmsmax]['a'].argmin()        ####        601:ff2でvarmax29とvarmax9が一致,29を広げるのは逆効果    

    if Debug is True:
        ax = df[['d','var29','var29_v','vrms','v','a']].plot(figsize=(10,8),subplots=True,c='b',
                                   title='%s shot:%d ch:%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[2].axvline(varmax,color='r')
        ax[3].axvline(rmsmax,color='r')
        ax[5].axvspan(varmax,rmsmax,color='g',alpha=.3)
        ax[5].axvline(h,color='r')
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h+NARROW_PADDING, df.d[h], [h-varmax,rmsmax-h]      # dfは50:-50の範囲でreset_indexされているので、df.dのindexはh+50である必要は無い

def breaking_rmean_dmin(d, spm, fs=100000,low=0, high=8000,r_window=1,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    破断後の最下点=break throughが特定できれば、破断点の検索範囲を
    break through以前に限定することができ、アルゴリズムの堅牢性、
    実行効率ともに向上が期待できる。

    [破断後の最下点=break through]
    移動平均によりトレンドを求め、元波形からトレンド成分を除去する。
       m:   39点移動平均 (グレーが元波形、グレーと青の距離がo_mとなる)
       o_m: 元波形 - 39点移動平均;
    バンドパスと同じ考え方だが、FFTの副作用が無くコントロールしやすい。
    破断以前の動きの緩やかな区間では、元波形とトレンド成分はほぼ同期しており、
    破断後の急降下がより大きく表れる。
    破断後の第二波、第三波の落ち込みの方が絶対値としては大きいケースがしばしばあるが、
    第一波の落ち込みによりトレンド成分も下降を始めているため、
    第二波、第三波の落ち込みは抑制される。
    つまり、第二波が来るタイミングで、第一波の影響がトレンドに表れるような移動平均範囲の設定が必要。

    [破断点]
    破断後最下点を終端として、その前方20pointの範囲の加速度最小点を破断点とする。
    破断後の急降下、その後のリバウンドは自由落下的な動きをしていると想定され、
    SPMに依存していないと考えられ、破断点検索範囲の設定は固定長で事足りると思われる。
       d:   元波形に対して0-8000Hzのバンドパス
       v:   速度(dを微分)
       a:   加速度(vを微分)
            o_mの最小位置-20:o_mの最小位置]の範囲を緑網掛け->加速度検索範囲

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :shot (int)          デバッグ表示用
    :ch (str)            デバッグ表示用
    :return (int,float,*)  最大荷重点index, 最大荷重値

    ToDo: 502:1,3
    """
    df = pd.DataFrame({'o':d})
    df['m'] = df.rolling(39,center=False).mean()
    df['o_m'] = df.o - df.m                              # 移動平均線からの乖離; 急激な変動だけが浮かび上がる
    
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['d'] = bandpass_ifft(s,f,low,high).real            # バンドパス
    df = df[NARROW_PADDING:-NARROW_PADDING].reset_index()                           # FFT後のデータ両端は信用できないのでPADDING分を切り捨て
    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度
    
    break_through = df.o_m.idxmin()                          # 移動平均線からの乖離における最小点が破断後の最下点
    search_start = np.max([df.index[0],break_through-20])    # 破断後最下点の前方20point、もしくはデータの先頭を検索開始点とする
    if search_start == break_through:                        # 破断後最下点と検索開始が一致した場合は、そこを破断点として処理
        h = break_through                                    # あり得ないケースだが、検索範囲長:0のidxmin()を取ることになりエラーとなる
    else:
        h = df[search_start:break_through]['a'].idxmin()     # 検索範囲における加速度最小が破断点
    
    if Debug is True:
        ax = df[['m','o_m','d','v','a']].plot(figsize=(10,8),subplots=True,c='b',
                                   title='%s shot:%d ch:%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black',label='o'); plt.legend()
        ax[0].axvline(h,c='r')
        ax[1].axvline(break_through,color='r')
        ax[4].axvline(h,c='r'); ax[4].axvspan(break_through-20,break_through,color='g',alpha=.3)      
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h+NARROW_PADDING, df.d[h], [break_through-20+NARROW_PADDING,break_through+NARROW_PADDING]

def breaking_vmin(d, spm, fs=100000,low=0, high=8000,r_window=1,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    [破断後の最下点=break through]
    荷重開始から最大荷重に至る動きは低周波であり、破断後の動きは高周波なので、
    バンドパスで低周波をカットしてやると最大荷重の山は無くなり、破断後の落ち込みは残る。
    結果、破断後の落ち込みが最小点になる
       o:   元波形
       b:   oに対して700-5000Hzのバンドパス; 低周波のトレンドと高周波のノイズをカット

    [破断点]
    breaking_rmean_dminと同様、break throughを終端としてその前方20点の加速度最小を破断点とする。
       d:   元波形に対して0-8000Hzのバンドパス
       v:   速度(dを微分)
       a:   加速度(vを微分)
            bの最小位置-20:bの最小位置]の範囲を緑網掛け->加速度検索範囲

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :shot (int)          デバッグ表示用
    :ch (str)            デバッグ表示用
    :return (int,float,*)  最大荷重点index, 最大荷重値
    
    ToDo: 298:4,  502:4,  826:2,4
    """
    BP_LOW = 700; BP_HIGH = 5000
    df = pd.DataFrame({'o':d})
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['b'] = bandpass_ifft(s,f,BP_LOW,BP_HIGH).real    
    df['d'] = bandpass_ifft(s,f,low,high).real    
    df = df[NARROW_PADDING:-NARROW_PADDING].reset_index()                           # FFT後のデータ両端は信用できないのでPADDING分を切り捨て
    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度

    break_through = df.b.idxmin()
    search_start = np.max([df.index[0],break_through-20])    # 破断後最下点の前方20point、もしくはデータの先頭を検索開始点とする
    if search_start == break_through:                        # 破断後最下点と検索開始が一致した場合は、そこを破断点として処理
        h = break_through                                    # あり得ないケースだが、検索範囲長:0のidxmin()を取ることになりエラーとなる
    else:
        h = df[search_start:break_through]['a'].idxmin()     # 検索範囲における加速度最小が破断点
    
    if Debug is True:
        ax = df[['o','b','d','v','a']].plot(figsize=(10,8),subplots=True,c='b',
                                   title='%s shot:%d ch:%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[1].axvline(break_through,color='r')
        ax[4].axvline(h,color='r'); ax[4].axvspan(break_through-20,break_through,color='g',alpha=.3)
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h+NARROW_PADDING, df.d[h], None

def breaking_varmax29(d, spm, fs=100000,low=0, high=8000,r_window=1,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    移動平均で使用するrolling window範囲内の分散は、破断点前後で大きくなる。
    この「移動分散」の破断点付近におけるピークは、
    rolling windowの範囲を広く採れば広く緩やかなものとなり、
    rolling windowの範囲を狭く採れば鋭いものとなる。
    この性質を利用し、29点移動分散ピークと9点移動分散ピークに挟まれた区間を検索範囲とし、
    加速度最小点を求める。
       d:     元波形に対して0-8000Hzのバンドパス
       var9:  9点移動分散
       var29: 29点移動分散
       v:     速度(dを微分)
       a:     加速度(vを微分)
              max(var9)とmax(var29)の間を緑網掛け

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大荷重点index, 最大荷重値
    

    """
    df = pd.DataFrame({'o':d})
    df['d'] = df.o.rolling(r_window,center=True,min_periods=1).mean()   # 移動平均
    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度

    df['var9'] = df.o.rolling(9,center=True,min_periods=1).var()
    df['var29'] = df.o.rolling(29,center=True,min_periods=1).var()    
    varmax9 = df.var9.idxmax()            
    varmax29 = df.var29.idxmax()     
    if varmax29 >= varmax9:                          # 502全ch破綻,rollingの範囲をspmに連動させるか?  346:3, 731:3
        h = varmax9                                  # varmax29とvarmax9が一致 or 逆転した場合はvarmax9を採用、その範囲でmax採るより前倒した方が吉
    else:
        h = df[varmax29:varmax9]['a'].idxmin()        ####        601:ff2でvarmax29とvarmax9が一致,29を広げるのは逆効果    

    if Debug is True:
        ax = df[['d','var9','var29','v','a']].plot(figsize=(10,8),subplots=True,c='b',
                                   title='%s shot:%d ch:%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[1].axvline(varmax9,color='r')
        ax[2].axvline(varmax29,color='r')
        ax[4].axvspan(varmax29,varmax9,color='g',alpha=.3)
        ax[4].axvline(h,color='r')
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 破断点の場合は、df.d[h]ではなくdf.o[h]を返すべきか?
    return h, df.d[h], varmax29


def breaking_varmax29idiff(d, spm, fs=100000,low=0, high=8000, r_window=19,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    breaking_varmax29で行っている検索範囲の限定は、前方のvar29は概ねうまくいくものの、後方のvar9は安定しない。
    破断直後の荷重最小点前後にピークが立つことを期待しているが、第二波、第三波がより大きくなってしまうケースが多い。
    これを抑制するため、破断前は正、破断後は負となるような成分をかけ合わせたい。
       b:     元波形に対して0-8000Hzのバンドパス
       d:     元波形に対して0-8000Hzのバンドパス
       v9:    9点移動分散 * -9点積分階差
       v29:   29点移動分散 * -29点積分階差
       v:     速度(dを微分)
       a:     加速度(vを微分)
              max(v9)とmax(v29)の間を緑網掛け
    このため、9点移動分散、29点移動分散にそれぞれ9点積分階差、29点積分階差を符号反転してかけ合わせたものをv9,v29とし、
    そのピークを加速度検索範囲とする。積分階差は、よりノイズ除去効果の高い移動平均と考えて良く、
    判断後の荷重最小点以降、大きなトレンドとしては上昇して元の水準に復帰していく傾向が期待できるなら、
    第二波、第三波によるvar9のピークを符号反転して抑制してくれるはずである。
    
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({'o':d})
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['d'] = bandpass_ifft(s,f,low,high).real            # バンドパス
    df['v'] = df.o.diff()                                 # 速度
    df['a'] = df.v.diff()                                 # 加速度
    df['v9'] =  (df.d.rolling(9,center=True,min_periods=1).var() * -df.d.rolling(9,center=True,min_periods=1).apply(_idiff))
    df['v29'] = (df.d.rolling(29,center=True,min_periods=1).var() * -df.d.rolling(29,center=True,min_periods=1).apply(_idiff))
    varmax9idiff =  df.v9.idxmax()
    varmax29idiff = df.v29.idxmax()
    if varmax29idiff >= varmax9idiff:                     # varmaxにidiffをかけることで下降局面に絞る; 731:1 
        h = varmax9idiff                                  #
    else:                                                 #
        h = df[varmax29idiff:varmax9idiff]['a'].idxmin()  #

    if Debug is True:
        ax = df[['d','v','v29','v9','a']].plot(figsize=(10,8),subplots=True,c='b',
                title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[2].axvline(varmax29idiff,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[3].axvline(varmax9idiff,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[4].axvspan(varmax29idiff,varmax9idiff,color='g',alpha=.3)
        ax[4].axvline(h,c='r'); #ax[2].axhline(criteria,c='g')       
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.o[h], varmax9idiff

def breaking_varmax29idiff_tmpfix(d, spm, fs=100000,low=0, high=8000, r_window=19,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-100,100]):
    """ 破断点
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :fs (int)            サンプリング周波数(Hz)
    :low (int)           バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数    
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大荷重点index, 最大荷重値
    
    ToDo: 低SPMではバンドパスノイズの影響が前方に及んでるケースがある。
          低SPM時はノイズ除去の必要性が大きくないはずなので調整の余地あり。
    """
    df = pd.DataFrame({'o':d})
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['d'] = bandpass_ifft(s,f,low,high).real            # バンドパス
    df['v'] = df.o.diff()                                 # 速度
    df['a'] = df.v.diff()                                 # 加速度
    df['v9'] =  (df.d.rolling(9,center=True).var() * -df.d.rolling(9,center=True).apply(_idiff))
    df['v29'] = (df.d.rolling(29,center=True).var() * -df.d.rolling(29,center=True).apply(_idiff))
    varmax9idiff =  df.v9.argmax()
    varmax29idiff = df.v29.argmax()
    h = varmax29idiff    # これなら確実に動くはず???
#    if varmax29idiff >= varmax9idiff:                     # varmaxにidiffをかけることで下降局面に絞る; 731:1 
#        h = varmax9idiff                                  #
#    else:                                                 #
#        h = df[varmax29idiff:varmax9idiff]['a'].argmin()  #

    if Debug is True:
        ax = df[['d','v','v29','v9','a']].plot(figsize=(10,8),subplots=True,c='b',
                title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[2].axvline(varmax29idiff,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[3].axvline(varmax9idiff,c='r'); #ax[2].axhline(criteria,c='g')       
        ax[4].axvspan(varmax29idiff,varmax9idiff,color='g',alpha=.3)
        ax[4].axvline(h,c='r'); #ax[2].axhline(criteria,c='g')       
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.o[h], varmax9idiff

def load_start(d, spm, r_window=399,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-1000,1500]):
    """ 荷重開始点 (速度変化版; 加速度ではない)
    最大荷重に至るまでの範囲の速度推移を標準化(論理的には初期0、荷重開始以降は1となる想定)し、
    この標準化速度が0.2を超えた最初の点を荷重開始点とする。
    この時、0.2超え検索の範囲を荷重最大点-1200とする。
    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大開始点index, 荷重開始値

    ToDo: 検索範囲を決める1200の値はSPMによって大きく変わる。
          逆にSPMが正確にわかれば、かなり正確に特定できるはずなので、
          標準化加速度の閾値0.2ももっと小さくできるはず。
          現状は、低SPMではこの1200が狭すぎるので、坂道の途中を求めてしまう。
    
    """
    df = pd.DataFrame({'o':d})
    df['d'] = df.o.rolling(r_window,center=True,min_periods=1).mean()   # 移動平均
    df['v'] = df.d.diff().rolling(r_window,min_periods=1).mean()        # 速度

    argmax = df.d.idxmax()                                # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.v[0:df.d.idxmax()].max()
    l_min = df.v[100:df.d.idxmax()].min()
    df['sv'] = (df.v - l_min) / (l_max - l_min)
    h = df[df.d.idxmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    if Debug is True:
        plt.figure(figsize=(12,5))
        ax = df[['d','v','sv']].plot(figsize=(10,8),subplots=True,c='b',
                title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black'); 
        ax[0].axvline(h,c='r'); ax[2].axhline(0.2,c='g')       
        ax[2].axvspan(df.d.idxmax()-1200,df.d.idxmax(),color='g',alpha=.3)
        ax[2].set_ylim(-0.1,1.1)
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])
        plt.show()

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h], l_max

def load_start2(d, spm, r_window=399,Debug=False,shot=999,ch='loadxx',debug_xlim=[-1000,1500]):
    """ 荷重開始点 (速度変化版 rev.2)
    速度に加え荷重値も開始:最大荷重の範囲を標準化(初期0、最大荷重1に向けて徐々に上昇)し、
    標準化荷重の下限から0.2を超えるまでの範囲を検索範囲とする。これによって、SPMの考慮は必須ではなくなった。
    この検索範囲の中で標準化速度が0.2を初めて超えた点を荷重開始点とする。

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用>  。                                           囲
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大開始点index, 荷重開始値

    ToDo: 荷重開始前の水平区間は、全体の傾向としてやや下降していることが多く、
          荷重下限は荷重開始の直前に来ることが多い。この場合、アルゴリズムはうまく機能するが、
          稀に荷重下限がショット開始付近になることがあり(shot#441,442,541)、この場合に0.2の閾値が怪しくなる。
          検索範囲及び標準化範囲を、標準化荷重が0.2を超えた点から遡って固定長(この場合はspmの考慮必要)とすることで、
          アルゴリズムとしては、より良好に機能すると思われる。
          しかしながら、荷重開始前の水平区間のゆらぎが、鋼板のたわみのようなものだとすると、
          このような考慮はむしろ特定される荷重開始点のゆらぎに繋がるのではないか?
    """
    df = pd.DataFrame({'o':d})
    df['d'] = df.o.rolling(r_window,center=True,min_periods=1).mean()   # 移動平均
    df['v'] = df.d.diff().rolling(r_window,min_periods=1).mean()        # 速度

    argmax = df.d.idxmax()                                # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.d[argmax]
    l_min = df.d[100:argmax].min()
    df['sd'] = (df.d - l_min) / (l_max - l_min)           # 標準化変位 
    l_max = df.v[0:argmax].max(); #print(l_max)
    l_min = df.v[100:argmax].min(); #print(l_min)   # これをできるだけ直前に持っていきたい
    df['sv'] = (df.v - l_min) / (l_max - l_min)
      
#     h = df[df.d.argmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    sd_start = df[100:df.d.idxmax()].sd.idxmin()           # 100:最大荷重の範囲の荷重最小点 -> sd_start
    sd_end = df[100:df.d.idxmax()][df.sd>0.2].index[0]     # 標準化変位が0.2を超えた -> sd_end
    if sd_start >= sd_end:
        h = sd_start
    else:
        h = df[sd_start:sd_end][df.sv>0.2].index[0]            # sd_start:sd_endの範囲で、標準化速度が0.2を超えた最初の点    

    if Debug is True:
        ax = df[['d','sd','v','sv']].plot(figsize=(10,8),subplots=True,c='b',
                title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[1].set_ylim(-0.1,1.1); ax[1].axvspan(sd_start,sd_end,color='g',alpha=.3),ax[1].axhline(0.2,c='g')
        ax[3].set_ylim(-0.1,1.1); ax[3].axhline(0.2,c='g')
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h], sd_start

def load_start3(d, spm, r_window=399,Debug=False,shot=999,ch='loadxx',debug_xlim=[-1000,1500]):
    """ 荷重開始点 (加速度版)
    入力波形(o)から移動平均によりノイズを除去(d)、これを標準化(sd)。
    dより速度(v)、加速度(a)を求める。
    sdの最小値位置から0.2となる位置までを検索範囲とし、加速度極小位置を荷重開始点とする。

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる。今のところ未使用。
    :r_window (int)      移動平均ウィンドウ範囲
    :Debug (bool)        グラフ表示
    :return (int,float,*)  最大開始点index, 荷重開始値

    ToDo: 402:4, 444:1, 601:2

    """
    df = pd.DataFrame({'o':d})
    df['d'] = df.o.rolling(r_window,center=True,min_periods=1).mean()   # 移動平均
    df['v'] = df.d.diff().rolling(r_window,center=True,min_periods=1).mean()        # 速度
    df['a'] = df.v.diff().rolling(r_window,center=True,min_periods=1).mean()        # 加速度


    argmax = df.d.idxmax()                                # 100:変位最大値位置の範囲で速度を標準化 -> df['s']
    l_max = df.d[argmax]
    l_min = df.d[100:argmax].min()
    df['sd'] = (df.d - l_min) / (l_max - l_min)           # 標準化変位
    l_max = df.v[0:argmax].max(); #print(l_max)
    l_min = df.v[100:argmax].min(); #print(l_min)   # これをできるだけ直前に持っていきたい
    df['sv'] = (df.v - l_min) / (l_max - l_min)

#     h = df[df.d.argmax()-1200:][df.sv>0.2].index[0]        # 最大点-1200の範囲で、標準化速度が0.2を超えた最初の点
    sd_start = df[100:df.d.idxmax()].sd.idxmin()           # 100:最大荷重の範囲の荷重最小点 -> sd_start
    sd_end = df[100:df.d.idxmax()][df.sd>0.2].index[0]     # 標準化変位が0.2を超えた -> sd_end
    h = df[sd_start:sd_end].a.idxmax()           # sd_start:sd_endの範囲で、
    if Debug is True:
        ax = df[['d','sd','v','sv','a']].plot(figsize=(10,8),subplots=True,
                 title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        df.o.plot(ax=ax[0],alpha=.3,c='black');
        ax[0].axvline(h,c='r')
        ax[1].set_ylim(-0.1,1.1)
        ax[1].axhline(0.2,c='g'); ax[1].axvspan(sd_start,sd_end,color='g',alpha=.3)
        ax[3].set_ylim(-0.1,1.1); ax[3].axhline(0.2,c='g')
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.d[h], sd_end


def max_load(d, spm, fs=100000,low=0, high=None, r_window=19,Debug=False,shot=9999,ch='loadxx',debug_xlim=[-1500,1000]):
    """ 最大荷重点
    1系列のデータをリストで受け取り、最大荷重点のindexとvalueを返す。
    バンドパス→移動平均でノイズを除去後、最大点を検出する単純なアルゴリズムなので、
    バンドパス、移動平均のパラメタ調整が全て。
    低SPMでは、バンドパスノイズ(FFTの副作用)の影響が前方に及ぶケースがある一方で、
    ノイズ除去の必要性が高くないため、SPMの値に応じてバンドパス上限周波数を調整している(省略時)。

    :d (np.array)        荷重系列データ
    :spm (float)         SPM(shots per minutes)、荷重開始→最大→破断の推移の速度にほぼ反比例すると考えられる
    :low (float)         バンドパスフィルタ下限周波数
    :high (float)        バンドパスフィルタ上限周波数
    :r_window (int)      移動平均ウィンドウ範囲
    :return (int,float,*)  最大荷重点index, 最大荷重値

    """
    if high is None:               # バンドパス上限周波数が明示されない場合
        if spm > 60:               # 高SPM時はノイズ除去を優先し2kHz以上をカット
            high = 2000
        else:                      # 低SPM時はFFTの副作用のデメリットの方が大きくなるので積極的にカットしない
            high = 5000
    df = pd.DataFrame({'o':d})
    s,f,p = fft_spectrum(df.o,fs=fs)                      # FFT
    df['b'] = bandpass_ifft(s,f,low,high).real            # バンドパス
    df['m'] = df.b.rolling(r_window).mean()               # 破断の影響を前方に出さないようcenter=Trueしない
    h = df['m'].idxmax()
    if Debug is True:
        ax = df.plot(figsize=(10,4),subplots=True,
                title='%s shot:%d,ch=%s'%(sys._getframe().f_code.co_name,shot,ch))
        ax[0].axvline(h,c='r'); #ax[2].axhline(criteria,c='g')
        plt.xlim(h+debug_xlim[0],h+debug_xlim[1])

    # 値として元波形 or ノイズ除去後のいずれを採用すべきかは個々に判断されるべきと考えるので、
    # indexと併せて(ノイズ除去後の)値も返す仕様とする。
    return h, df.m[h], None

def extract_features(shot_data, spm, func, narrowing = None, sub_func=None, disp_narrowing=False,disp_chart=False,xlim=[-100,100],**kwargs):
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
    :sub_func (*function)             関数ポインタ; 処理効率改善のため時系列検索範囲を限定する必要があり、
                                      4ch共通の範囲を指定したい場合に使用。現在は破断点の場合のみ、narrowing_var_chを指定。
    :disp_narrowing (bool)            sub_funcで指定した関数に渡され、グラフ表示を制御する
    :disp_chart (bool)                グラフ表示; ショットごとの元波形と特徴量を表示。
    :**kwargs (可変キーワード引数)    funcに指定した関数に対応した引数を指定
    :return (list, list, list)        indexリスト, 値リスト, デバッグリスト
    """
#     print(shot_data.head())
    cmap = plt.get_cmap("tab10")
    if spm is None:                  # 最後のショットは次のショットが無いためspm計算不能, 80を想定する。
        spm = 80.0

    if 'shot' in kwargs:
        shot = kwargs['shot']             # 可変キーワード変数から拝借; 掟破り
    else:
        shot = 9999

    if narrowing is not None:
        sub_start = narrowing[0] - NARROW_PADDING
        sub_end = narrowing[1] + NARROW_PADDING
    else:
        if sub_func is not None:
            sub_start, sub_end = sub_func(shot_data,disp_narrowing,shot)
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

    argmax = []; valmax = []; debugval = [];
    chs = ['load01','load02','load03','load04']
    for ch in chs:
        kwargs['ch'] = ch                                    # 可変キーワードにch追加
        i,v,d = func(np.array(shot_data[ch][sub_start:sub_end]),spm,**kwargs)     # ここでnp.arrayになるのでindexがなくなる
        argmax.append(i+sub_start)                  # funcはsubset中の相対indexを返してくるので、offsetを加える
        valmax.append(v)
        debugval.append(d)

    if disp_chart:
        plt.figure(figsize=(12,6))
        for c in range(len(chs)):
            plt.plot(shot_data.index,shot_data[chs[c]],label=chs[c],alpha=.3,c=cmap(c)) # 「流れ」があるのでscatterよりlineの方が見やすいと思う
            #plt.scatter(shot_data.index,shot_data[chs[c]],label=chs[c],s=2,alpha=1.0,c=[cmap(c)]*len(shot_data))
            plt.scatter([argmax[c]],[valmax[c]],marker='o',s=200,alpha=.5,c=[cmap(c)])  # plotとscatterのcolor mapを揃える
        plt.title('%s shot:%d'%(func.__name__,shot)); plt.legend();
        if xlim[0] != 0 or xlim[1] != 0:
            plt.xlim(np.array(argmax).min()+xlim[0],np.array(argmax).max()+xlim[1]);
        plt.show()

    return argmax,valmax,debugval


if __name__ == "__main__":
    """ この部分は大塚の作業環境依存
    """
    DATA_ROOT='/data'

    from pathlib import Path
    p = Path(DATA_ROOT+'/H-One/20201127/shots/')
    flist = list(sorted(p.glob('shots_*.csv')))

    features = []; debug_features = []
    for f in range(0,len(flist),50):
    #     print(f,flist[f])
        shot = int(os.path.basename(flist[f])[6:9])

        df1 = pd.read_csv(flist[f])
        if len(df1) == 0:
            print('%s invalid'%flist[f])
            continue
	
        df1 = df1.rename({'v1':'load01',
			  'v2':'load02',
			  'v3':'load03',
			  'v4':'load04',
			  'c1':'displacement'
		   },axis=1)
	
        #argmax,valmax,debugval = extract_features(df1, 80.0, max_load)    # SPMここでは固定
        #argmax,valmax,debugval = extract_features(df1, 80.0, breaking_varmax29)    # SPMここでは固定
        #argmax,valmax,debugval = extract_features(df1, 80.0, breaking_varmax29idiff)    # SPMここでは固定
        #argmax,valmax,debugval = extract_features(df1, 80.0, breaking_varmax29idiff_tmpfix)    # SPMここでは固定
        argmax,valmax,debugval = extract_features(df1, 80.0, breaking_var_vrms, sub_func=narrowing_var_ch)    # SPMここでは固定
        #argmax,valmax,debugval = extract_features(df1, 80.0, load_start)    # SPMここでは固定
        #argmax,valmax,debugval = extract_features(df1, 80.0, load_start3)    # SPMここでは固定
        features.append([shot] + argmax + valmax + list(np.array(argmax).argsort()<=1))    
        debug_features.append([shot] + debugval)    
	
    features = pd.DataFrame(features,columns=['shot','argmax01','argmax02','argmax03','argmax04','valmax01','valmax02','valmax03','valmax04','b01','b02','b03','b04'])
    print(features)
