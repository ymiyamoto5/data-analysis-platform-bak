FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
# FROM python:3.8.12-slim-buster

ARG USERNAME
ARG UID
ARG GID
ARG DOCKER_GID

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sqlite3 \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

# ホスト側のログインユーザーと一致するグループ追加とユーザー追加
# コンテナ内にDockerグループ追加、およびDockerグループにユーザー追加
RUN groupadd -g $GID $USERNAME \
    && groupadd -g $DOCKER_GID docker \
    && useradd -m -g $GID -u $UID $USERNAME \
    && usermod -aG docker $USERNAME \
    && apt-get update \
    && apt-get install -y sudo curl \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

COPY --chown=$USERNAME:$USERNAME ./pyproject.toml ./poetry.lock /app/
COPY --chown=$USERNAME:$USERNAME ./prestart.sh /app/

RUN mkdir /app/poetry \
    && chown $USERNAME:$USERNAME /app/poetry

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/app/poetry python - \
    && cd /usr/local/bin \
    && ln -s /app/poetry/bin/poetry \
    && cd /app \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# USER $USERNAME
# WORKDIR /app
# CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
