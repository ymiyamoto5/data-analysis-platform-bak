# データ分析基盤

## プロジェクト構成

### frontend

#### src

##### src.components

Web アプリケーションの管理画面を構成するボタンやグラフなどのコンポーネント。

##### src.views

Web アプリケーションの管理画面。

### backend

#### analyzer

分析ロジックの適用を行う。

#### app

データ収集をコントロールするための Web アプリケーション。

##### app.alembic

データベースマイグレーションツール。 models の変更内容を自動検出して、更新内容を管理、反映する。

##### app.api

HTTP メソッドに応じて実行される API 群。

##### app.crud

各データの CRUD 処理を行う。

##### app.db

データベースのエンジンのインスタンスやセッションを生成する。

##### app.models

データベースのテーブル定義。models に model(エンティティ)を追加する場合、\_\_init\_\_.py への model インポート追加が必要。

##### app.schemas

データベースのスキーマ。

##### app.services

ショット切り出しやデータ収集履歴のデータ処理を行う。

#### common

共通のグローバル定数やエラーメッセージなどの定義。

#### cut_out_shot

ショット切り出し処理を行う。

#### data_converter

ショット切り出し処理で扱うデータコンバーター。

#### data_importer

Elasticsearch にデータフレームとして提供されるデータをインポートする。

#### data_reader

Elasticsearch に格納されたデータを読み取り、データフレームとして返却する。

#### data_recorder

収集データを Elasticsearch およびテンポラリファイル(.pkl ファイル)に保存する。  
cron により毎分起動される。

#### elastic_manager

Elasticsearch に対する処理を wrapping するクラス。

#### file_manager

処理対象のファイルデータや日時データの管理を行うクラス。

#### mappings

データマッピング。

### tests

テスト用モジュール群。

#### utils

汎用処理。グローバル定数は common.py に保持する。

### docker

docker コンテナーのファイル群。コンテナーの構成定義や image の build を行う。

### notebooks

jupyter notebook のファイル群。ショット切り出しや分析ロジック適用は jupyter notebook から行う。

### その他

#### log

各モジュールのログ出力先。

#### .env

本システム共通で利用する設定値。開発用は .env.development 、本番環境用は .env.production から取得する。

#### cron_job.sh

data_recorder を実行するシェルスクリプト。cron 用。

#### Elasticsearch

ショットの切り出しや分析結果を扱う全文検索エンジン。

#### Kibana

Elasticsearch からデータを取得して可視化。

#### Jupyter Notebook

データの加工や分析を行い、Elasticsearch に結果を保存。

#### mlflow

モデルの保管。情報のトラッキング。

#### getting started

（記載）
