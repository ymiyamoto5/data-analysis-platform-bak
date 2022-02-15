FROM python:3.8.12-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock /backend/

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/backend/poetry python - \
    && cd /usr/local/bin \
    && ln -s /backend/poetry/bin/poetry \
    && cd /backend \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev
