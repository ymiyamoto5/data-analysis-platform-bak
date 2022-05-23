#! /usr/bin/env bash

# distファイルを所定場所に移動
cp -rf dist backend/app/

# Let the DB start
sleep 1;
# Run migrations
alembic -c backend/alembic.ini upgrade head