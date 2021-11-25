# データ分析基盤

## ルール

push 前に以下を実行すること。
ターミナルでプロジェクト直下に移動し、ユニットテスト実行。

```
pytest
```

ターミナルでプロジェクト直下に移動し、backend の型チェック実行。

```
mypy backend
```

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

本システム共通で利用する環境変数。git 管理外のため、各自のローカルで管理すること。また、このファイルに変更を行った場合は他の開発者にアナウンスし、共有すること。

サンプル

- プロジェクト直下の.env ファイル

```
API_URL=http://localhost:8000/api/v1
SQLALCHEMY_DATABASE_URI=sqlite:////mnt/datadrive/app.db
DB_SQL_ECHO=0
NO_PROXY=localhost
mlflow_server_uri=http://localhost:5000
mlflow_experiment_name=some
MLFLOW_S3_ENDPOINT_URL=http://localhost:9000
AWS_ACCESS_KEY_ID=minio-access-key
AWS_SECRET_ACCESS_KEY=minio-secret-key
data_dir=/mnt/datadrive/data/
elastic_url=localhost:9200
elastic_user=elastic
elastic_password=P@ssw0rd
mapping_rawdata_path=backend/mappings/mapping_rawdata.json
setting_rawdata_path=backend/mappings/setting_rawdata.json
setting_shots_path=backend/mappings/setting_shots.json
setting_shots_meta_path=backend/mappings/setting_shots_meta.json
setting_resample_path=backend/mappings/setting_resample.json
```

- frontend/.env.production

```
NODE_ENV='production'
VUE_APP_API_BASE_URL='http://<ローカルIP>'
VUE_APP_KIBANA_URL='http://<ローカルIP>:5601/'
VUE_APP_JUPYTER_URL='http://<ローカルIP>:8888/'
VUE_APP_MLFLOW_URL='http://<ローカルIP>:5000'
```

### mypy.ini

mypy による型チェックのルール設定。主に除外設定を行う。

# getting started

## git clone

```
git clone http://dev2.sphinx.uniadex.co.jp/ymiyamoto5/data-analysis-platform.git
```

## git setup

```
git config --global user.name {ユーザ名}
git config --global user.email {メールアドレス}
```

## Frontend setup

### yarn install

```
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt-get update && sudo apt-get install yarn
```

### package install

```
cd ~/data-analysis-platform/frontend
yarn install
```

## Backend setup

### timezone

```
sudo timedatectl set-timezone Asia/Tokyo
```

### logging

```
cd /var
sudo chmod 777 log
```

### venv

```
sudo apt install python3.8-venv
cd ~/data-analysis-platform
python3 -m venv venv
```

### bashrc

```
nano ~/.bashrc
-->
PATH="$PATH:$HOME/.local/bin/"
export HTTP_PROXY="http://proxy.unisys.co.jp:8080/"
export HTTPS_PROXY="http://proxy.unisys.co.jp:8080/"
export http_proxy="http://proxy.unisys.co.jp:8080"
export https_proxy="http://proxy.unisys.co.jp:8080"
source venv/bin/activate
-->
source ~/.bashrc
```

### pip

```
cd backend
pip install -r requirements.txt
```

## Docker Container 起動

### Docker install

```
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
```

### sudo なしで Docker コマンドを実行する設定

```
sudo usermod -aG docker \${USER}
su - ${USER}
id -nG
```

### proxy

```
cd /etc/systemd/system/
sudo mkdir docker.service.d
cd docker.service.d
sudo nano override.conf
-->
[Service]
Environment = 'http_proxy=http://proxy.unisys.co.jp:8080' 'https_proxy=http://proxy.unisys.co.jp:8080'
-->
```

### Docker 再起動/ステータス確認

```
sudo systemctl restart docker
sudo systemctl status docker
```

### ファイル格納先作成

```
sudo mkdir -p /mnt/datadrive/data
ls /mnt/datadrive/
sudo chmod -R 777 /mnt
```

### コンテナー起動

```
cd ~/data-analysis-platform/docker
docker-compose up -d
```

### コンテナー image リビルドして起動

```
cd ~/data-analysis-platform/docker
docker-compose up -d --build
```

### 起動中のコンテナー確認

```
docker ps
```

## DB setup

### SQLite3 install

```
sudo apt install sqlite3
```

### create db

```
python -m backend.utils.create_db
```

## デバッグ

### Current File

エディタで開いているファイルをスクリプト実行する場合に選択。

### パッケージ

analyzer などのパッケージをデバッグする場合は、それに応じたものを選択。

### Jest

frontend テストを実行する場合に選択。（frontend テストは未実装）

### FastAPI

FastAPI 単体をデバッグする場合に選択。

### Full-stack

frontend と FastAPI を連携する場合に選択。

### data_recorder with FastAPI

data_recorder はバックエンドにリクエストするため、FastAPI とともに起動する。
