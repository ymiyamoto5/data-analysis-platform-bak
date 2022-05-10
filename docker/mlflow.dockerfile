FROM python:3.8.12-slim-buster

ARG USERNAME
ARG UID
ARG GID

RUN groupadd -g $GID $USERNAME \
    && useradd -m -g $GID -u $UID $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

RUN pip install mlflow sqlalchemy boto3
RUN mkdir -p /mlflow \
    && chown $USERNAME:$USERNAME /mlflow
WORKDIR /mlflow