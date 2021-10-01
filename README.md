# データ分析基盤

## プロジェクト構成

### frontend

### backend

#### analyzer

分析ロジックの適用を行う。

#### cut_out_shot

ショット切り出し処理を行う。

#### app

データ収集をコントロールするための Web アプリケーション。

##### app.models

models に model(エンティティ)を追加する場合、\_\_init\_\_.py への model インポート追加が必要。

#### data_reader

Elasticsearch に格納されたデータを読み取り、データフレームとして返却する。

#### data_recorder

収集データを Elasticsearch およびテンポラリファイル(.pkl ファイル)に保存する。  
cron により毎分起動される。

#### elastic_manager

Elasticsearch に対する処理を wrapping するクラス。

#### utils

汎用処理。グローバル定数は common.py に保持する。

### tests

テスト用モジュール群。

### notebooks

jupyter notebook のファイル群。ショット切り出しや分析ロジック適用は jupyter notebook から行う。

### その他

#### log

各モジュールのログ出力先。

#### app_config.json

本システム共通で利用する設定値。

#### cron_job.sh

data_recorder を実行するシェルスクリプト。cron 用。
