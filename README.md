# データ分析基盤

## プロジェクト構成

### frontend

vue@2.6.14  
@vue/cli 4.5.13

### backend

#### analyzer

分析ロジックの適用を行う。

#### app

Web アプリケーション

- データ収集コントロール
- データ収集履歴
- ショット切り出し
- モデル作成、管理
- 管理画面
- 関連リンク

##### app.alembic

データベースマイグレーションツール。 models の変更内容を自動検出して、更新内容を管理、反映する。

##### app.api

HTTP メソッドに応じて実行される API 群。

##### app.crud

各データの CRUD 処理を行う。

##### app.db

データベースエンジンのインスタンスやセッションを生成する。

##### app.models

データベースのテーブル定義。models に model(エンティティ)を追加する場合、\_\_init\_\_.py への model インポート追加が必要。

##### app.schemas

API スキーマ。URL パラメーターや Request Body、Response データのバリデーションを行う。

##### app.services

API エンドポイントからロジック部を分離したもの。複雑な処理は API エンドポイントに  
直接コーディングせず、services に分離すること。

#### common

共通のグローバル定数やエラーメッセージなどの定義。

#### cut_out_shot

ショット切り出し処理を行う。実行方法は Web アプリケーションからの実行と Juypter からの実行の 2 通りがある（Web アプリケーションに一本化する可能性あり）。

#### data_converter

ショット切り出し処理で扱うデータコンバーター。主に生のセンサー値（電圧値）を物理量に変換する式を実装する。

#### data_importer

DataFrame として提供されるデータを Elasticsearch にインポートする。

#### data_reader

Elasticsearch に格納されたデータを読み取り、DataFrame として返却する。

#### data_recorder

収集したバイナリデータを中間ファイル(.pkl ファイル)に保存する。本モジュールは systemd に登録する。また、本モジュールは同じく systemd に登録した data_recorder.timer より毎分起動される。（Docker コンテナー化により実行方式が変更になる可能性あり。）

#### elastic_manager

Elasticsearch に対する処理を wrapping するクラス。

#### file_manager

バイナリファイルに対する処理（ファイル名から対象ファイルの判定など）を行う。また、中間ファイル（.pkl ファイル）に対する処理を行う。

#### mappings

Elasticsearch のインデックスマッピング。フィールドの型等を指定する。

### tests

ユニットテスト用モジュール群。

#### utils

汎用モジュール、またはアドホックなモジュール置き場。

##### utils.study

検証用や学習用のソースコード置き場。

### docker

docker コンテナーのファイル群。

### notebooks

jupyter notebook のファイル群。分析ロジック適用は jupyter notebook から行う。

### .env

本システム共通で利用する環境変数。開発用は .env.development 、本番環境用は .env.production から取得する。（.env.production は git 管理外とする）

### mypy.ini

mypy による型チェックのルール設定。主に除外設定を行う。

# getting started

## git clone

## Frontend setup

## Backend setup

## Docker Container 起動

## DB setup

## デバッグ
