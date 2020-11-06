# 非稼働分析 デモ用
## WebApp
### frontend
Vue.js 3  

### backend
Flask  

## Script
### data_generator
ダミーのセンサーデータをJSONファイルで生成するスクリプト。  
sin(x)の値を変位値とする。また、末尾の5サンプルは変位値0の異常データとしている。  
データ数Nはスクリプトを書き換えること。  

### data_recorder
data_generatorが生成したJSONファイルを読み込み、Elasticsearchに格納するスクリプト  
