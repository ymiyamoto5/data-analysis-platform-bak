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

python 3.8.12  
fastapi 0.68.2

#### analyzer

分析ロジックの適用を行う。

##### alembic

データベースマイグレーションツール。 models の変更内容を自動検出して、更新内容を管理、反映する。

#### app

Web アプリケーション

- データ収集コントロール
- データ収集履歴
- ショット切り出し
- モデル作成、管理
- 管理画面
- 関連リンク

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

ショット切り出し処理を行う。

#### data_converter

ショット切り出し処理で扱うデータコンバーター。主に生のセンサー値（電圧値）を物理量に変換する式を実装する。

#### data_importer

DataFrame として提供されるデータを Elasticsearch にインポートする。

#### data_reader

Elasticsearch に格納されたデータを読み取り、DataFrame として返却する。

#### data_recorder

収集したバイナリデータを中間ファイル(.pkl ファイル)に保存する。本モジュールは celery タスクとして実行される。手動実行も可能。

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

docker コンテナー関連のファイル群。Dockerfile 等々。

### notebooks

jupyter notebook のファイル群。分析ロジック適用は jupyter notebook から行う。

### .env, .env.local

本システム共通で利用する環境変数。git 管理外のため、各自のローカルで管理すること。また、このファイルに変更を行った場合は他の開発者にアナウンスし、共有すること。なお、環境変数の設定値はプロジェクトごとに異なる値を設定する。

- .env: Docker コンテナーで利用する環境変数を定義
- .env.local: ローカルデバッグ時に利用する環境変数を定義
- docker/.env: docker-compose の本番デプロイ時で利用する環境変数
- docker/.env.dev: docker-compose の開発時で利用する環境変数
- frontend/.env.production: フロントエンドの本番ビルド時（yarn build）で利用する環境変数
- frontend/.env.development: フロントエンドの開発サーバー（yarn serve）で利用する環境変数

サンプル

- .env

```
HTTP_PROXY=http://proxy.unisys.co.jp:8080
HTTPS_PROXY=http://proxy.unisys.co.jp:8080
NO_PROXY=localhost,elasticsearch,redis,rabbitmq,mlflow,minio,127.0.0.1
no_proxy=localhost,elasticsearch,redis,rabbitmq,mlflow,minio,127.0.0.1
SQLALCHEMY_DATABASE_URI=sqlite:////mnt/datadrive/app.db
DB_SQL_ECHO=0
NO_PROXY=localhost,elasticsearch,redis,rabbitmq,mlflow,minio
no_proxy=localhost,elasticsearch,redis,rabbitmq,mlflow,minio
MLFLOW_SERVER_URI=http://mlflow:5000
MLFLOW_EXPERIMENT_NAME=some
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
AWS_ACCESS_KEY_ID=minio-access-key
AWS_SECRET_ACCESS_KEY=minio-secret-key
DATA_DIR=/mnt/datadrive/data
ELASTIC_URL=elasticsearch:9200
ELASTIC_USER=<elastic user>
ELASTIC_PASSWORD=<elastic password>
MAPPING_RAWDATA_PATH=backend/mappings/mapping_rawdata.json
SETTING_RAWDATA_PATH=backend/mappings/setting_rawdata.json
SETTING_SHOTS_PATH=backend/mappings/setting_shots.json
SETTING_SHOTS_META_PATH=backend/mappings/setting_shots_meta.json
SETTING_RESAMPLE_PATH=backend/mappings/setting_resample.json
CELERY_BROKER_URL=pyamqp://guest:guest@rabbitmq:5672
CELERY_RESULT_BACKEND=redis://redis/0
```

.env.local

```
LOCAL_IP=<ローカルIP>
SQLALCHEMY_DATABASE_URI=sqlite:////mnt/datadrive/app.db
DB_SQL_ECHO=1
MLFLOW_SERVER_URI=http://${LOCAL_IP}:5000
MLFLOW_EXPERIMENT_NAME=some
MLFLOW_S3_ENDPOINT_URL=http://${LOCAL_IP}:9000
AWS_ACCESS_KEY_ID=minio-access-key
AWS_SECRET_ACCESS_KEY=minio-secret-key
DATA_DIR=/mnt/datadrive/data
ELASTIC_URL=${LOCAL_IP}:9200
ELASTIC_USER=<elastic user>
ELASTIC_PASSWORD=<elastic password>
MAPPING_RAWDATA_PATH=backend/mappings/mapping_rawdata.json
SETTING_RAWDATA_PATH=backend/mappings/setting_rawdata.json
SETTING_SHOTS_PATH=backend/mappings/setting_shots.json
SETTING_SHOTS_META_PATH=backend/mappings/setting_shots_meta.json
SETTING_RESAMPLE_PATH=backend/mappings/setting_resample.json
CELERY_BROKER_URL=pyamqp://guest:guest@${LOCAL_IP}:5672
CELERY_RESULT_BACKEND=redis://${LOCAL_IP}/0
```

- docker/.env

```
COMPOSE_PROJECT_NAME=data-analysis-platform
DATA_DIR=/mnt/datadrive/data
DATA_DRIVE=/mnt/datadrive
IP=<ローカルIP>
ELASTIC_USERNAME=<elastic user>
ELASTIC_PASSWORD=<elastic password>
ENV_FILE=../.env
```

- docker/.env.dev

```
COMPOSE_PROJECT_NAME=data-analysis-platform
DATA_DIR=/mnt/datadrive/data
DATA_DRIVE=/mnt/datadrive
IP=<ローカルIP>
ELASTIC_USERNAME=<elastic user>
ELASTIC_PASSWORD=<elastic password>
ENV_FILE=../.env
ELASTICSEARCH_PORT=<デフォルトポート番号（9200）+ X>
KIBANA_PORT=<デフォルトポート番号（5601）+ X>
NOTEBOOK_PORT=<デフォルトポート番号（8888）+ X>
WEBAP_PORT=<デフォルトポート番号（80）+ X>
MLFLOW_PORT=<デフォルトポート番号（5000）+ X>
MINIO_PORT_1=<デフォルトポート番号（9000）+ X>
MINIO_PORT_2=<デフォルトポート番号（9011）+ X>
RABBITMQ_PORT_1=<デフォルトポート番号（4369）+ X>
RABBITMQ_PORT_2=<デフォルトポート番号（5672）+ X>
RABBITMQ_PORT_3=<デフォルトポート番号（25672）+ X>
RABBITMQ_PORT_4=<デフォルトポート番号（15672）+ X>
REDIS_PORT=<デフォルトポート番号（6379）+ X>
FLOWER_PORT=<デフォルトポート番号（5555）+ X>
```

- frontend/.env.production

```
NODE_ENV='production'
VUE_APP_API_BASE_URL='http://<ローカルIP>'
VUE_APP_KIBANA_URL='http://<ローカルIP>:5601/'
VUE_APP_JUPYTER_URL='http://<ローカルIP>:8888/'
VUE_APP_MLFLOW_URL='http://<ローカルIP>:5000'
```

- frontend/.env.development

```
NODE_ENV='development'
VUE_APP_API_BASE_URL='http://localhost:8000'
VUE_APP_KIBANA_URL='http://localhost:5601/'
VUE_APP_JUPYTER_URL='http://localhost:8888/'
VUE_APP_MLFLOW_URL='http://localhost:5000'
```

### mypy.ini

mypy による型チェックのルール設定。主に除外設定を行う。

# getting started

## git clone

```
git clone https://github.com/ual-technologycenter/data-analysis-platform.git
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

### bashrc

```
nano ~/.bashrc
```

--> 以下を追記

```
PATH="$PATH:$HOME/.local/bin/"
export HTTP_PROXY="http://proxy.unisys.co.jp:8080/"
export HTTPS_PROXY="http://proxy.unisys.co.jp:8080/"
export http_proxy="http://proxy.unisys.co.jp:8080"
export https_proxy="http://proxy.unisys.co.jp:8080"
source .venv/bin/activate
```

--> 以下を実行

```
source ~/.bashrc
```

### poetry

```
poetry install
```

## Docker

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
```

--> 以下を記述

```
[Service]
Environment = 'http_proxy=http://proxy.unisys.co.jp:8080' 'https_proxy=http://proxy.unisys.co.jp:8080'
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

## DB setup

### SQLite3 install

```
sudo apt install sqlite3
```

### create db (local)

```
alembic -c backend/alembic.ini upgrade head
python -m backend.utils.create_dummy_data
```

### create db (docker)

```
docker-compose exec webap /bin/bash
python -m backend.utils.create_dummy_data
```
