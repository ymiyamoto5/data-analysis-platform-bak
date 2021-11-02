FROM python:3.7-slim-buster

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080
ENV no_proxy=minio

RUN pip install mlflow sqlalchemy boto3
RUN mkdir -p /mlflow
WORKDIR /mlflow
