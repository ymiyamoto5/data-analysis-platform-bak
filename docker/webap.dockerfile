FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sqlite3 \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock /app/

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/app/poetry python - \
    && cd /usr/local/bin \
    && ln -s /app/poetry/bin/poetry \
    && cd /app \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev
