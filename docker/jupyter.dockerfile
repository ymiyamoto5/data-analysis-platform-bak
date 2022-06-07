FROM jupyter/base-notebook

ARG USERNAME
ARG UID
ARG GID

USER root
RUN chmod -R 777 /var/log
RUN apt-get update -y && \
    apt-get install -y tzdata \
    curl && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

# UIDが1000の場合、jovyanの1000とコンフリクトするため、jovyanには適当なUID（8888）を割り当てておく
RUN groupadd -g $GID $USERNAME \
    && usermod -u 8888 jovyan \
    && useradd -m -g $GID -u $UID $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

COPY --chown=$USERNAME:$USERNAME ./pyproject.toml ./poetry.lock /home/$USERNAME/

RUN mkdir /home/$USERNAME/poetry \
    && chown $USERNAME:$USERNAME /home/$USERNAME/poetry \
    && chmod -R 777 /home/jovyan

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/home/$USERNAME/poetry python - \
    && cd /usr/local/bin \
    && ln -s /home/$USERNAME/poetry/bin/poetry \
    && cd /home/$USERNAME \
    && poetry config virtualenvs.create false \
    && poetry install

USER $UID
RUN jupyter contrib nbextension install --user \
    && jupyter nbextension enable hinterland/hinterland \
    && jupyter nbextension enable toc2/main \
    && jupyter nbextension enable freeze/main