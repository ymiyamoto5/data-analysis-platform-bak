#! /usr/bin/env bash

# Let the DB start
sleep 1;
# Run migrations
alembic -c backend/alembic.ini upgrade head