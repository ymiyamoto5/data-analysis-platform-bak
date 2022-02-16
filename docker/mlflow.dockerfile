FROM python:3.8.12-slim-buster

RUN pip install mlflow sqlalchemy boto3
RUN mkdir -p /mlflow
WORKDIR /mlflow
