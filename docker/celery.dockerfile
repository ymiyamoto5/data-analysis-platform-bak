FROM python:3.8.12-slim-buster

ARG USERNAME
ARG UID
ARG GID

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g $GID $USERNAME \
    && useradd -m -g $GID -u $UID $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

COPY --chown=$USERNAME:$USERNAME ./pyproject.toml ./poetry.lock /backend/

RUN mkdir /backend/poetry \
    && chown $USERNAME:$USERNAME /backend/poetry

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/backend/poetry python - \
    && cd /usr/local/bin \
    && ln -s /backend/poetry/bin/poetry \
    && cd /backend \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev
