FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080
ENV POETRY_HOME=/app/poetry

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sqlite3 \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml /app
COPY ./poetry.lock /app
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN cd /usr/local/bin && ln -s /app/poetry/bin/poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev
