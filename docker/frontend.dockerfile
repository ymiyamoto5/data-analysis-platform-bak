FROM node:16.1

ENV http_proxy=http://proxy.unisys.co.jp:8080 \
    https_proxy=http://proxy.unisys.co.jp:8080

WORKDIR /app

# NOTE: package.jsonとyarn.lockのみ先にCOPYしてinstall。これによりパッケージ追加がない限りキャッシュを利用できる。
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install

COPY frontend .
RUN yarn build
