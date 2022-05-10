FROM jupyter/base-notebook

USER root
RUN chmod -R 777 /var/log
RUN apt-get update -y && \
    apt-get install -y tzdata \
    curl && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock /home/jovyan/

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/home/jovyan/poetry python - \
    && cd /usr/local/bin \
    && ln -s /home/jovyan/poetry/bin/poetry \
    && cd /home/jovyan \
    && poetry config virtualenvs.create false \
    && poetry install
