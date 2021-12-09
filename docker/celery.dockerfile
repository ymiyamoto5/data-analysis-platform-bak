FROM python:3.7-slim-buster

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080
ENV no_proxy=rabbitmq,redis

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN pip install --upgrade pip
RUN pip install -U celery[redis] python-dotenv
