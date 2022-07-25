"""
 ==================================
  brew_features.py
 ==================================

  Copyright(c) 2022 UNIADEX, Ltd. All Rights Reserved.
  CONFIDENTIAL
  Author: UNIADEX, Ltd.

"""
import json
import os
from textwrap import dedent as d
import pandas as pd
import numpy as np
from datetime import date, datetime,timedelta
from fft_tools import *
from plotly_utils import *
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import numpy as np



## データごとにこの関数を書けば良いように
#def read_logger(f):
#    # 9行目以降のメタ情報を読み込むために一旦8行目以降を読み込み
#    df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7] )
#    unit = df.iloc[4]
#    offset = df.iloc[3]
#    calibration = df.iloc[2]
#    v_range = df.iloc[1]
#    channel = df.iloc[0]
#    # 改めて8行目をヘッダにして読み込む
#    # df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1).set_index('time')
#    # floatのindex作っちゃダメ!!!
#    df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1)
#    try:
#        df['プレス荷重shift'] = df['プレス荷重'].shift(-640)
#        df['dF/dt'] = df['プレス荷重shift'].diff()
#        df['F*dF/dt'] = df['プレス荷重shift'] * df['dF/dt']
#        if '加速度左右_X_左+' in df.columns:
#            df = df.rename({'加速度左右_X_左+':'加速度左右_X_左+500G'},axis=1)
#        if '加速度上下_Y_下+' in df.columns:
#            df = df.rename({'加速度上下_Y_下+':'加速度上下_Y_下+500G'},axis=1)        
#        if '加速度前後_Z_前+' in df.columns:
#            df = df.rename({'加速度前後_Z_前+':'加速度前後_Z_前+500G'},axis=1)        
#    except KeyError:
#        print('プレス荷重　無し')
#
#    return df,unit,offset,calibration,v_range,channel
#
## 項目の情報を取得するため1ファイルだけ先に読む。ToDo:前データ項目共通の前提
#from pathlib import Path
#p = Path('/Users/hao/data/ADDQ/20211004ブレークスルー/')
#flist = list(sorted(p.glob('*.CSV')))
#f = flist[10]
#df = read_logger(f)[0][:3000]

## "項目名" => 表示subplot-id のdictionary
#disp_col = {}
#disp_col['プレス荷重shift'] = 0
#disp_col['右垂直'] = 0
#disp_col['スライド変位右'] = 1
#disp_col['加速度左右_X_左+500G'] = 2
#
#yref = {0:'y', 1:'y2', 2:'y3'}

# "項目名" => 表示subplot-id のdictionary
#nrows = 3; ncols = 2; 
#disp_col = {}
#disp_col['プレス荷重shift'] = [1,1]
#disp_col['右垂直'] = [1,1]
#disp_col['左垂直'] = [1,1]
#disp_col['スライド変位右'] = [2,1]
#disp_col['スライド変位左'] = [2,1]
#disp_col['M30ボルスタ右奥'] = [1,2]
#disp_col['加速度左右_X_左+500G'] = [3,1]
#disp_col['加速度上下_Y_下+500G'] = [3,1]
#disp_col['加速度前後_Z_前+500G'] = [3,1]
#disp_col['スライド＿金型隙間'] = [2,2]


#class DataAccessor:
#    def __init__(self):
#        # 抽出済み特徴量の "名前=>値(index)" となるdictionary。
#        from pathlib import Path
#        p = Path('/Users/hao/data/ADDQ/20211004ブレークスルー/')
#        self.flist = list(sorted(p.glob('*.CSV')))
#
#    def get_shot_list(self):
#        return self.flist
#
#    def get_shot(self,num):
#        return self.flist[num]
#
#    def read_logger(self,f):
#        # 9行目以降のメタ情報を読み込むために一旦8行目以降を読み込み
#        df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7] )
#        unit = df.iloc[4]
#        offset = df.iloc[3]
#        calibration = df.iloc[2]
#        v_range = df.iloc[1]
#        channel = df.iloc[0]
#        # 改めて8行目をヘッダにして読み込む
#        # df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1).set_index('time')
#        # floatのindex作っちゃダメ!!!
#        df = pd.read_csv(f,encoding='cp932' ,skiprows=[0,1,2,3,4,5,6,7,9,10,11,12,13], ).rename({'CH名称':'time'},axis=1)
#        try:
#            df['プレス荷重shift'] = df['プレス荷重'].shift(-640)
#            df['dF/dt'] = df['プレス荷重shift'].diff()
#            df['F*dF/dt'] = df['プレス荷重shift'] * df['dF/dt']
#            if '加速度左右_X_左+' in df.columns:
#                df = df.rename({'加速度左右_X_左+':'加速度左右_X_左+500G'},axis=1)
#            if '加速度上下_Y_下+' in df.columns:
#                df = df.rename({'加速度上下_Y_下+':'加速度上下_Y_下+500G'},axis=1)        
#            if '加速度前後_Z_前+' in df.columns:
#                df = df.rename({'加速度前後_Z_前+':'加速度前後_Z_前+500G'},axis=1)        
#        except KeyError:
#            print('プレス荷重　無し')
#
#        #return df,unit,offset,calibration,v_range,channel
#        return df

class brewFeatures:
    def __init__(self):
        self.nrows = 2
        self.ncols = 1
        # disp_colのdefaultの初期値をここで設定
        self.disp_col = {}
        self.disp_col['プレス荷重shift'] = [1,1,None]
        self.disp_col['スライド変位右'] = [2,1,None]
        # 抽出済み特徴量の "名前=>値(index)" となるdictionary。
        self.dr = None
        self.gened_features = {}

    def set_DataAccessor(self,dr):
        self.dr = dr

    def set_dispcol(self, disp_col):
        '''  ToDo:
        3項目目の禁則文字チェックが必要。コーテーションとか。
        '''
        '''  ToDo:
        disp_colの要素を[row,col,値の変換式:Noneだったら元の項目そのまま]のまま行くとしたら、
        ほとんどの場合意味のない3項目目のNoneをユーザが書き忘れる可能性が高い。
        書き忘れると、対応の難しいバグとして現れるので、
        ここでsetする時に足りないNoneを補うとかした方が良さそう。
        その前に、この変な形のまま行くかどうかを考えるべきだが。
        '''
        '''
        disp_colは、項目名 => [表示位置row, 表示位置col] となるdictionary。
        '''
        self.disp_col = disp_col
        '''
        disp_colからnrows,ncolsを算出
        values()でdict_valuesを取り出してlistにcast、さらにnumpy.arrayにcast
        (2,x)のarrayになるので、[:,0]でrowだけ、[:,1]でcolだけ取り出す。
            disp_col.values()                        # dict_values([[1, 1], [1, 1], [2, 1], [2, 1], [2, 1]])
            list(disp_col.values())                  # [[1, 1], [1, 1], [2, 1], [2, 1], [2, 1]]
            np.array(list(disp_col.values()))        # array([[1, 1],
                                                              [1, 1],
                                                              [2, 1],
                                                              [2, 1],
                                                              [2, 1]])
            np.array(list(disp_col.values()))[:,0]   #   array([1, 1, 2, 2, 2])
        '''
        self.nrows = int(np.array(list(disp_col.values()))[:,0].max())   # intにcastしないとダメ、なんでだ?
        self.ncols = int(np.array(list(disp_col.values()))[:,1].max())

    def get_dispcol(self):
        return self.disp_col


    # 特徴抽出操作指示のgridの1行を生成   
    ''' ToDo: 選択肢はdisp_colにある項目のみで良い '''
    def gen_input_forms(self,row_id,fname='',sel_col='',rw=1,llim=0,ulim=0):
        return dbc.Col( dcc.Input(id='feature_name%d'%row_id,value=fname), width=1,),\
            dbc.Col( dcc.Dropdown(id='select_col%d'%row_id,value=sel_col,
                options=[{'label':str(s),'value':str(s)} for s in self.disp_col.keys()]), width=2,),\
            dbc.Col( dcc.Input(id='rolling_width%d'%row_id,value=rw), width=1,),\
            dbc.Col( dcc.Dropdown(id='low_find_type%d'%row_id,value='固定',
                options=[{'label':str(s),'value':str(s)} for s in ['固定','値域>','値域<','特徴点']]), width=1,),\
            dbc.Col( dcc.Dropdown(id='low_feature%d'%row_id,value='-',
                options=[{'label':'-','value':'-'}]), width=1,),\
            dbc.Col( dcc.Input(id='low_lim%d'%row_id,value=llim), width=1,),\
            dbc.Col( dcc.Dropdown(id='up_find_type%d'%row_id,value='固定',
                options=[{'label':str(s),'value':str(s)} for s in ['固定','値域>','値域<','特徴点']]), width=1,),\
            dbc.Col( dcc.Dropdown(id='up_feature%d'%row_id,value='-',
                options=[{'label':'-','value':'-'}]), width=1,),\
            dbc.Col( dcc.Input(id='up_lim%d'%row_id,value=ulim), width=1,),\
            dbc.Col( dcc.Dropdown(id='find_target%d'%row_id,clearable=False,value='DPT',
                options=[{'label':'元波形','value':'DPT'},{'label':'速度','value':'VCT'},{'label':'加速度','value':'ACC'}]), width=1,),\
            dbc.Col( dcc.Dropdown(id='find_dir%d'%row_id,clearable=False,value='MAX',
                options=[{'label':str(s),'value':str(s)} for s in ['MAX','MIN','RMS','VAR','AMP']]), width=1,)

    '''  locate_feature()を呼ぶために必要なパラメタ群をdictに '''
    def params_to_dict(self,feature_name,select_col,rolling_width,low_find_type,low_feature,low_lim,
                        up_find_type,up_feature,up_lim,find_target,find_dir):
        params = {}
        params['feature_name'] = feature_name
        params['select_col'] = select_col
        params['rolling_width'] = rolling_width
        params['low_find_type'] = low_find_type
        params['low_feature'] = low_feature
        params['low_lim'] = low_lim
        params['up_find_type'] = up_find_type
        params['up_feature'] = up_feature
        params['up_lim'] = up_lim
        params['find_target'] = find_target
        params['find_dir'] = find_dir

        return params

    ''' locate_feature()の結果(検索範囲と検索結果)をfigに描き込む
        figは既に時系列データがplotされている前提
    '''
    def draw_result(self,
                    fig,     # figオブジェクト
                    result   # 検索結果(検索範囲、検索結果(index, value))
                    ):
        if 'target_i' in result:
            select_col = result['select_col']
            row = self.disp_col[select_col][0]
            col = self.disp_col[select_col][1]

            # 値域 -> 水平方向(hrect)緑網掛け
            ''' ToDo: add_hrect()はY軸方向の下限と上限を指定する。下限だけ指定して上限はグラフの上限まで、というような
                都合の良い機能は無さそう。
                dataから網掛けの上限下限を決めると上下に隙間ができる。1.2倍とかでいいのか?  '''
            ''' low_less_ylimだけ描けない、なんでだ? '''
            for hrect_key in ['low_less_ylim','low_more_ylim','up_less_ylim','up_more_ylim']:
                if hrect_key in result:
                    y_lim = result[hrect_key]
                    fig.add_hrect(y0=y_lim[0],y1=y_lim[1],line_width=0, fillcolor="green", opacity=0.2,layer='below', row=row,col=col)

            # 検索範囲 -> 垂直方向(vrect)オレンジ網掛け
            x_lim = result['x_lim']
            fig.add_vrect(x0=x_lim[0],x1=x_lim[1],line_width=0, fillcolor="LightSalmon", opacity=0.2,layer='below', row=row,col=col)

            # 検索結果 -> 赤縦線   ToDo: 特徴量ごとに色分けしたい
            fig.add_vline(x=result['target_i'],line_color="red", row=row,col=col)

    # 特徴抽出機能のコア部   ToDo: グラフ操作を分離して特徴抽出だけを呼べるように
    def locate_feature(self,
                       df,              # 対象データ:pandas.DataFrame
                       feature_name,    # 特徴量名:str
                       select_col,      # 処理対象項目:str
                       rolling_width,   # 検索下限限方法:'固定' or '値域>' or '値域<' or '特徴点'
                       low_find_type,   # 検索下限限特徴量名:str
                       low_feature,     # 検索下限限値:int
                       low_lim,         # 検出下限対象:'DPT' or 'VCT' or 'ACC'
                       up_find_type,    # 検索上限方法:'固定' or '値域>' or '値域<' or '特徴点'
                       up_feature,      # 検索上限特徴量名:str
                       up_lim,          # 検索上限値:int
                       find_target,     # 検出上限対象:'DPT' or 'VCT' or 'ACC'
                       find_dir         # ピーク方向:'MAX' or 'MIN'
                       ):
        target_i = None
        result = {}
        result['feature_name'] = feature_name

        if feature_name == '':
            return result
        if select_col == '':
            return result

        x_lim = [0,0]   # 初期値
        
        # 検索範囲下限(左端)の決定
        if low_find_type == '固定':
            x_lim[0] = int(low_lim)
        elif low_find_type == '値域>':                      # 指定値より大きい範囲を検索して左端のindexを返す
            result['low_more_ylim'] = [float(low_lim),df[select_col].max()]
            sdf = df[(df[select_col]>=float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
        elif low_find_type == '値域<':                      # 指定値より小さい範囲を検索して左端のindexを返す
            result['low_less_ylim'] = [df[select_col].min(),float(low_lim)]
            sdf = df[(df[select_col]<=float(low_lim))]
            if len(sdf) > 0:
                x_lim[0] = sdf.index[0]
            # print('value:',x_lim)
        elif low_find_type == '特徴点':
            try:
                x_lim[0] = self.gened_features[low_feature] + int(low_lim)
                #, gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print('Error')

        # 検索範囲上限(右端)の決定
        if up_find_type == '固定':
            x_lim[1] = int(up_lim)
        elif up_find_type == '値域>':                      # 指定値より大きい範囲を検索して右端のindexを返す
            result['up_more_ylim'] = [float(up_lim),df[select_col].max()]
            sdf = df[(df[select_col]>=float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
        elif up_find_type == '値域<':                      # 指定値より小さい範囲を検索して右端のindexを返す
            result['up_less_ylim'] = [df[select_col].min(),float(up_lim)]
            sdf = df[(df[select_col]<=float(up_lim))]
            if len(sdf) > 0:
                x_lim[1] = sdf.index[-1]
            # print('value:',x_lim)
        elif up_find_type == '特徴点':
            try:
                x_lim[1] = self.gened_features[up_feature] + int(up_lim)
                #, gened_features[up_feature] + int(up_lim)]
            except KeyError:
                print('Error')

        # 検索対象時系列データの生成
        if find_target == 'DPT':
            target = df[select_col]
        elif find_target == 'VCT':
            target = df[select_col].rolling(int(rolling_width),center=True).mean().diff()
        elif find_target == 'ACC':
            target = df[select_col].rolling(int(rolling_width),center=True).mean().diff().rolling(int(rolling_width),center=True).mean().diff()
        if x_lim[1] - x_lim[0] > 0:     # 検索範囲が適切に指定されてなければ何もしない  ToDo:「何もしない」ことのフィードバック? 範囲指定せずに検索したい時もある
            if find_dir == 'MAX':
                target_i = target[x_lim[0]:x_lim[1]].idxmax()
                target_v = df[select_col][target_i]   # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == 'MIN':
                target_i = target[x_lim[0]:x_lim[1]].idxmin()
                target_v = df[select_col][target_i]   # ToDo: 値は元波形の値を返さないと意味が無い
            elif find_dir == 'RMS':
                target_i = x_lim[0]
                target_v = np.sqrt((df[select_col][x_lim[0]:x_lim[1]]**2).mean())
            elif find_dir == 'VAR':
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0]:x_lim[1]].var()
            elif find_dir == 'AMP':
                target_i = x_lim[0]
                target_v = df[select_col][x_lim[0]:x_lim[1]].max() - df[select_col][x_lim[0]:x_lim[1]].max()

        result['select_col'] = select_col
        result['x_lim'] = x_lim

        if target_i is not None:
            self.gened_features[feature_name] = target_i
            result['target_i'] = target_i             # 検索結果 インデックス
            result['target_v'] = target_v             # 検索結果 値

        return result

    def make_app(self):

        import plotly.express as px
        from jupyter_dash import JupyterDash
        import dash_core_components as dcc
        import dash_bootstrap_components as dbc
        import dash_html_components as html
        from dash.dependencies import Input, Output, State

        app = JupyterDash('brewFeatures', external_stylesheets=[dbc.themes.CERULEAN])

        flist = self.dr.get_shot_list()

        # 画面全体のレイアウト
        app.layout = html.Div([
        #     dcc.Dropdown(id='shot_select',options=[{'label':'a','value':'a'},{'label':'b','value':'b'},]),
            # ショット選択
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(id='shot_select',value=str(flist[9]),
                        options=[{'label':str(f), 'value':str(f)} for f in flist[8:]]),
                    width=5,
                    style={'width':'50vw'} # viewpoint height
                ),
            ]),
            # グラフ表示部
            dcc.Graph(id='graph'),
            # 特徴抽出操作指示: gen_input_forms()がInput,Dropdownを含むdbc.Colのリストを生成する
            dbc.Row([
                dbc.Col(dbc.Label('特徴量名')),
                dbc.Col(dbc.Label('対象項目'),width=2),
                dbc.Col(dbc.Label('移動平均範囲')),
                dbc.Col(dbc.Label('下限限定方法')),
                dbc.Col(dbc.Label('下限特徴量')),
                dbc.Col(dbc.Label('下限位置')),
                dbc.Col(dbc.Label('上限限定方法')),
                dbc.Col(dbc.Label('上限特徴量')),
                dbc.Col(dbc.Label('上限位置')),
                dbc.Col(dbc.Label('検索対象')),
                dbc.Col(dbc.Label('検索方向')),
            ]),        
    #         dbc.Row(gen_input_forms(0,fname='vct_min',sel_col='プレス荷重shift',rw=9,llim=1000,ulim=3000)),        
            dbc.Row(self.gen_input_forms(0,fname='',sel_col='プレス荷重shift',rw=9,llim=1000,ulim=3000)),                
            dbc.Row(self.gen_input_forms(1)),
            dbc.Row(self.gen_input_forms(2)),
            dbc.Row(self.gen_input_forms(3)),

            dbc.Button("Export", id="export"),
            dbc.Modal(
                [
                    dbc.ModalHeader("Header",id = 'modalheader'),
                    dbc.ModalBody("This is the content of the modal"),
                    dbc.ModalFooter(
                        dbc.Button("Close", id="close", className="ml-auto")
                    ),
                ],
                size="xl",
                id="modal",
            )
        ])

        # 検索範囲限定方法として「特徴点」が選択されたら、自身より上の行で定義されている特徴量名をDropdownのoptionとしてセットする
        #   特徴点セット2行目下限
        @app.callback(
            Output('low_feature1', 'options'),
            [Input('low_find_type1', 'value'),Input('feature_name0', 'value'),Input('low_feature1', 'options'),
            ])
        def set_low_features1(find_type,fname0,options):
            if find_type == '特徴点':
                return [{'label':fname0, 'value':fname0}]
            else:
                return options       # 「特徴点」以外ならoptionをクリアした方が良いか?

        #   特徴点セット2行目上限
        @app.callback(
            Output('up_feature1', 'options'),
            [Input('up_find_type1', 'value'),Input('feature_name0', 'value'),Input('up_feature1', 'options'),
            ])
        def set_up_features1(find_type,fname0,options):
            if find_type == '特徴点':
                return [{'label':fname0, 'value':fname0}]
            else:
                return options

        # 特徴点セット3行目上限 (1行目と2行目のfeature_nameをDropdownにセットする。このコーディングどうにかならんか....)
        @app.callback(
            Output('low_feature2', 'options'),
            [Input('low_find_type2', 'value'),Input('feature_name0', 'value'),Input('feature_name1', 'value'),Input('low_feature2', 'options'),
            ])
        def set_low_features2(find_type,fname0,fname1,options):
            if find_type == '特徴点':
                return [{'label':f, 'value':f} for f in [fname0,fname1]]
            else:
                return options

        # 特徴点セット3行目下限
        @app.callback(
            Output('up_feature2', 'options'),
            [Input('up_find_type2', 'value'),Input('feature_name0', 'value'),Input('feature_name1', 'value'),Input('up_feature2', 'options'),
            ])
        def set_up_features2(find_type,fname0,fname1,options):
            if find_type == '特徴点':
                return [{'label':f, 'value':f} for f in [fname0,fname1]]
            else:
                return options

        # 特徴点セット4行目上限
        ''' ToDo: feature_name0などのgridの要素をリストに納めてリストのindexで参照できるようにすれば? '''
        @app.callback(
            Output('low_feature3', 'options'),
            [Input('low_find_type3', 'value'),Input('feature_name0', 'value'),Input('feature_name1', 'value'),
                Input('feature_name2', 'value'),Input('low_feature3', 'options'),
            ])
        def set_low_features3(find_type,fname0,fname1,fname2,options):
            if find_type == '特徴点':
                return [{'label':f, 'value':f} for f in [fname0,fname1,fname2]]
            else:
                return options      # '特徴点'以外の場合は現状のまま...で良いのか?

        # 特徴点セット4行目下限
        @app.callback(
            Output('up_feature3', 'options'),
            [Input('up_find_type3', 'value'),Input('feature_name0', 'value'),Input('feature_name1', 'value'),
                Input('feature_name2', 'value'),Input('up_feature3', 'options'),
            ])
        def set_up_features3(find_type,fname0,fname1,fname2,options):
            if find_type == '特徴点':
                return [{'label':f, 'value':f} for f in [fname0,fname1,fname2]]
            else:
                return options
            
        # 波形グラフ描画のためのcallback関数。ショット選択及び下部のgridに含まれる入力フォームを全てobserveしている。
        # つまり入力フォームのいずれかが書き変わると必ずfigオブジェクト全体を再生成して置き換えている。
        ''' ToDo: 入力フォーム操作で再描画時にzoom/panがリセットされる; relayoutDataの維持 '''
        @app.callback(
    #     dash.dependencies.Output('graph', 'figure'),
            Output('graph', 'figure'),
            [Input('shot_select', 'value'),
                Input('feature_name0','value'),Input('select_col0','value'),Input('rolling_width0','value'),
                 Input('low_find_type0','value'),Input('low_feature0','value'),Input('low_lim0','value'),
                 Input('up_find_type0','value'),Input('up_feature0','value'),Input('up_lim0','value'),
                 Input('find_target0','value'),Input('find_dir0','value'),
                Input('feature_name1', 'value'),Input('select_col1', 'value'),Input('rolling_width1', 'value'),
                 Input('low_find_type1', 'value'),Input('low_feature1', 'value'),Input('low_lim1','value'),
                 Input('up_find_type1','value'),Input('up_feature1', 'value'),Input('up_lim1', 'value'),
                 Input('find_target1', 'value'),Input('find_dir1', 'value'),
                Input('feature_name2', 'value'),Input('select_col2', 'value'),Input('rolling_width2', 'value'),
                 Input('low_find_type2', 'value'),Input('low_feature2', 'value'),Input('low_lim2','value'),
                 Input('up_find_type2','value'),Input('up_feature2', 'value'),Input('up_lim2', 'value'),
                 Input('find_target2', 'value'),Input('find_dir2', 'value'),
                Input('feature_name3', 'value'),Input('select_col3', 'value'),Input('rolling_width3', 'value'),
                 Input('low_find_type3', 'value'),Input('low_feature3', 'value'),Input('low_lim3','value'),
                 Input('up_find_type3','value'),Input('up_feature3', 'value'),Input('up_lim3', 'value'),
                 Input('find_target3', 'value'),Input('find_dir3', 'value'),
            ])
        def callback_figure(shot,
                feature_name0,select_col0,rolling_width0,low_find_type0,low_feature0,low_lim0,up_find_type0,up_feature0,up_lim0,find_target0,find_dir0,
                feature_name1,select_col1,rolling_width1,low_find_type1,low_feature1,low_lim1,up_find_type1,up_feature1,up_lim1,find_target1,find_dir1,
                feature_name2,select_col2,rolling_width2,low_find_type2,low_feature2,low_lim2,up_find_type2,up_feature2,up_lim2,find_target2,find_dir2,
                feature_name3,select_col3,rolling_width3,low_find_type3,low_feature3,low_lim3,up_find_type3,up_feature3,up_lim3,find_target3,find_dir3,
                ):
            #print(shot)
            #df = read_logger(shot)[0][:7000]    ##############################
            df = self.dr.read_logger(shot)[:7000]   ##### こっちは[0]が無い　　!!!注意!!!  ######
            for col in self.get_dispcol().keys():
                if not col in df.columns:
                    df[col] = eval(self.get_dispcol()[col][2])
                    '''
                    execだとスタンドアローンではうまく行くが、jupyterからの実行でエラー。disp_colがnot fefined.
                    コンテキストが違う?  exec()にコンテキストを指定する方法があるようだが良くわからず。
                    恐らくeval()は、その構文がそこに書いてあるものとして評価するので、むしろeval()がふさわしい。
                    '''
                    #exec_str = self.get_dispcol()[col][2]
                    #exec(exec_str)
                    #exec(self.disp_col[col][2])

    #         fig = multi_col_figure(df[['プレス荷重shift','スライド変位右','加速度左右_X_左+500G']])
            '''
            make_subplots(shared_xaxes=True)X軸連動の対象は同じcol同志のみ。複数colある場合は縦に並んだsubplotだけが連動する。
            update_xaxes(matches='x')で連動させた場合は全てのsubplotが連動。
            shared_xaxes=Trueとupdate_xaxes(matches='x')は同じ機能にアクセスするAPIだとの議論もあるが、
            試した範囲では動作が異なる。バグか?
            https://github.com/plotly/plotly.py/issues/775
            https://community.plotly.com/t/shared-x-axis-with-sub-and-side-by-side-plots-and-click-events-in-html-output-file/34613
            '''
            # make_subplots()はgo.Figureインスタンスを生成。go.FigureWidgetはgo.Figureの継承クラスで、
            # go.Figureインスタンスを引数にコンストラクタを呼ぶとsubplot化されたgo.FigureWidgetインスタンスになる。
            fig = go.FigureWidget(
                #make_subplots(rows=self.nrows, cols=self.ncols, shared_xaxes=True,vertical_spacing = 0.03,horizontal_spacing=0.05)
                make_subplots(rows=self.nrows, cols=self.ncols, vertical_spacing = 0.04,horizontal_spacing=0.05)
            )
            fig.update_xaxes(matches='x')

            # disp_colで定義された項目を時系列グラフとして描画
            for col in self.disp_col:
                ''' ToDo: 要検討 このスコープのdfにはread_logger()で読んだ項目全て含まれてるので「表示しない項目」を考慮する必要無し? '''
#                if self.disp_col[col][0] == 0:  # disp_col['time'] = [0,0,None] と定義されてたら表示対象外
#                    continue
                fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=self.disp_col[col][0], col=self.disp_col[col][1])            
    #             fig.add_trace(go.Scatter(x=df.index, y=df[col], name=col), row=disp_col[col]+1, col=1)            

            '''
            matplotlibのsubplotでは、各subplotがそれぞれaxであるため、そのaxに対する操作が、
            非subplot環境、つまりfigure全体がaxである場合と同様に行えるようになっているのだが、
            そういった考え方がplotlyには無く、subplotはただ単にfigureを分割したものになっている。
            そのため、subplotごとにlegendを描く、という発想が無い。
            legendgroupという機能があり、複数データ系列のlegendをグルーピングすることができるが、
            これはsubplotとは無関係、あくまでlegend描画エリアの中でグルーピングし、
            そのグループ間のgapが指定可能(legend_tracegroupgap)になっているだけ。
            legend描画エリアはgo.Figureの中に一つだけだ。
            '''
            fig.update_layout(showlegend=True, title_text='shot No.', width=1600,height=800)
            # ToDo: legendはsubplotのtitleで入れた方が見栄えが良いが、一つのsubplotに複数ある時の対応をどうするか?

            # ToDo: 今のところ、gridの1行ごとにlocate_featureが必要
            # 
            # 検索範囲限定と屈折点検索の本体。resultには検索範囲と検索結果がdictで返るので、
            # バッチ化する時はこのメソッドだけ呼べば良い。
            #   1行目
            result = self.locate_feature(df,feature_name0,select_col0,rolling_width0,
                    low_find_type0,low_feature0,low_lim0,up_find_type0,up_feature0,up_lim0,find_target0,find_dir0)
            #print(result)
            # 検索範囲と検索結果の可視化
            self.draw_result(fig,result)
            
            #   2行目
            result = self.locate_feature(df,feature_name1,select_col1,rolling_width1,
                    low_find_type1,low_feature1,low_lim1,up_find_type1,up_feature1,up_lim1,find_target1,find_dir1)
            self.draw_result(fig,result)
            #print(result)

            #   3行目
            result = self.locate_feature(df,feature_name2,select_col2,rolling_width2,
                    low_find_type2,low_feature2,low_lim2,up_find_type2,up_feature2,up_lim2,find_target2,find_dir2)
            self.draw_result(fig,result)

            #   4行目
            result = self.locate_feature(df,feature_name3,select_col3,rolling_width3,
                    low_find_type3,low_feature3,low_lim3,up_find_type3,up_feature3,up_lim3,find_target3,find_dir3)        
            self.draw_result(fig,result)

            return fig

        ''' Exportが押されたら入力フォームgridの内容をjsonにしてpopup
            とりあえずバッチ化できることを示すための機能。
            このjsonをELSに保存、実行できるようにする?  '''
        @app.callback([Output("modal", "children"),
                       Output("modal", "is_open")],
                      [Input("export", "n_clicks"),
                       Input("close", "n_clicks"),
                       Input('feature_name0','value'),Input('select_col0','value'),Input('rolling_width0','value'),
                        Input('low_find_type0','value'),Input('low_feature0','value'),Input('low_lim0','value'),
                        Input('up_find_type0','value'),Input('up_feature0','value'),Input('up_lim0','value'),
                        Input('find_target0','value'),Input('find_dir0','value'),
                       Input('feature_name1', 'value'),Input('select_col1', 'value'),Input('rolling_width1', 'value'),
                        Input('low_find_type1', 'value'),Input('low_feature1', 'value'),Input('low_lim1','value'),
                        Input('up_find_type1','value'),Input('up_feature1', 'value'),Input('up_lim1', 'value'),
                        Input('find_target1', 'value'),Input('find_dir1', 'value'),
                       Input('feature_name2', 'value'),Input('select_col2', 'value'),Input('rolling_width2', 'value'),
                        Input('low_find_type2', 'value'),Input('low_feature2', 'value'),Input('low_lim2','value'),
                        Input('up_find_type2','value'),Input('up_feature2', 'value'),Input('up_lim2', 'value'),
                        Input('find_target2', 'value'),Input('find_dir2', 'value'),
                       Input('feature_name3', 'value'),Input('select_col3', 'value'),Input('rolling_width3', 'value'),
                        Input('low_find_type3', 'value'),Input('low_feature3', 'value'),Input('low_lim3','value'),
                        Input('up_find_type3','value'),Input('up_feature3', 'value'),Input('up_lim3', 'value'),
                        Input('find_target3', 'value'),Input('find_dir3', 'value'),
                      ],
                      [State("modal", "is_open"),
                       State("modal", "children")])
        def set_content(export,clicked,
                feature_name0,select_col0,rolling_width0,low_find_type0,low_feature0,low_lim0,up_find_type0,up_feature0,up_lim0,find_target0,find_dir0,
                feature_name1,select_col1,rolling_width1,low_find_type1,low_feature1,low_lim1,up_find_type1,up_feature1,up_lim1,find_target1,find_dir1,
                feature_name2,select_col2,rolling_width2,low_find_type2,low_feature2,low_lim2,up_find_type2,up_feature2,up_lim2,find_target2,find_dir2,
                feature_name3,select_col3,rolling_width3,low_find_type3,low_feature3,low_lim3,up_find_type3,up_feature3,up_lim3,find_target3,find_dir3,
                is_open,children):
            ctx = dash.callback_context
            #print(ctx.triggered[0]['prop_id'])

            if ctx.triggered[0]['prop_id'] == 'close.n_clicks':
                # you pressed the closed button, keeping the modal children as is, and 
                # close the model itself. 
                return children, False 
            elif ctx.triggered[0]['prop_id'] == 'export.n_clicks':
                # you clicked in the graph, returning the modal children and opening it
                params_list = []
                params_list.append(self.params_to_dict(feature_name0,select_col0,rolling_width0,low_find_type0,low_feature0,low_lim0,
                        up_find_type0,up_feature0,up_lim0,find_target0,find_dir0))
                params_list.append(self.params_to_dict(feature_name1,select_col1,rolling_width1,low_find_type1,low_feature1,low_lim1,
                        up_find_type1,up_feature1,up_lim1,find_target1,find_dir1))
                params_list.append(self.params_to_dict(feature_name2,select_col2,rolling_width2,low_find_type2,low_feature2,low_lim2,
                        up_find_type2,up_feature2,up_lim2,find_target2,find_dir2))
                params_list.append(self.params_to_dict(feature_name3,select_col3,rolling_width3,low_find_type3,low_feature3,low_lim3,
                        up_find_type3,up_feature3,up_lim3,find_target3,find_dir3))
                json_str = 'jsonstr=\'%s\''%(json.dumps(params_list))
                return [dbc.ModalHeader("Export "),
                        dbc.ModalBody(
                        html.Div([
                            html.Div([
                                #html.H6('Sales', style={'textAlign': 'center', 'padding': 10}),
                                #html.P("Bitch", id="sales_stocks", style={'textAlign': 'center', 'padding': 10}),
                                html.P(json_str)
                            ], className='pretty_container four columns'),
                            html.Div([
                            ], className='pretty_container seven columns')
                        ])),
                        dbc.ModalFooter(dbc.Button("Close", id="close"))
                        ], True
            else:
                raise dash.exceptions.PreventUpdate

        return app

if __name__ == '__main__':
    from data_accessor import DataAccessor

    # brewFeaturesインスタンスを生成
    brewFeatures = brewFeatures()
    # DataAccessorインスタンスを生成してbrewFeaturesにセット
    brewFeatures.set_DataAccessor(DataAccessor())
    # disp_colをoverrideすることで、グラフ表示をカスタマイズ
    # disp_colはDataAccessor側にあるべきか?
    disp_co = {}
    # "time"項目は表示対象外だが、微分する時に必要。DataAccessorで必ず"time"項目を作るという決まりにする?
    #disp_co['time'] = [0,0,None]    # plotlyのsubplotのrow,colは0 originではないので0,0は存在しない
    disp_co['プレス荷重shift'] = [1,1,None]
    disp_co['右垂直'] = [1,1,None]
    disp_co['スライド変位右'] = [2,1,None]
    disp_co['スライド変位左'] = [1,2,None]
    disp_co['F*dFdt'] = [3,1,'df["プレス荷重shift"]*(df["プレス荷重shift"].diff() / df["time"].diff())']
    brewFeatures.set_dispcol(disp_co)
    # サーバ実行
    app = brewFeatures.make_app()
    # JupyterDashでは今のところ0.0.0.0にbindできない
    app.run_server(host='0.0.0.0',port=8048,debug=True)
