#! /usr/bin/env bash

# Let the DB start
sleep 1;
# Run migrations
alembic upgrade head