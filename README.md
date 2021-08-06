# データ分析基盤
## プロジェクト構成

### frontend

### backend
#### analyzer
分析ロジックの適用を行う。

#### config_file_manager
IoTGWの動作制御を行うためのconfigファイルを読み書きする。

#### cut_out_shot
ショット切り出し処理を行う。

#### data_collect_manager
データ収集をコントロールするためのWebアプリケーション。

#### data_reader
Elasticsearchに格納されたデータを読み取り、データフレームとして返却する。

#### data_recorder
収集データをElasticsearchおよびテンポラリファイル(.pklファイル)に保存する。  
cronにより毎分起動される。

#### elastic_manager
Elasticsearchに対する処理をwrappingするクラス。

#### utils
汎用処理。グローバル定数はcommon.pyに保持する。

### tests
テスト用モジュール群。  

### notebooks
jupyter notebookのファイル群。ショット切り出しや分析ロジック適用はjupyter notebookから行う。

### その他
#### log
各モジュールのログ出力先。

#### mappings
Elasticsearch indexのmappingファイルとsettingファイル。

#### app_config.json
本システム共通で利用する設定値。

#### cron_job.sh
data_recorderを実行するシェルスクリプト。cron用。
