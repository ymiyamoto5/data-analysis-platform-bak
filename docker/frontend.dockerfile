FROM node:16.1

WORKDIR /app

# NOTE: package.jsonとyarn.lockのみ先にCOPYしてinstall。これによりパッケージ追加がない限りキャッシュを利用できる。
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install

COPY frontend .
RUN yarn build
