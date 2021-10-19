FROM jupyter/base-notebook

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

USER root
RUN chmod -R 777 /var/log
RUN apt-get update -y && \
    apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

USER jovyan
WORKDIR /home/jovyan
COPY --chown=1000:100 ./backend/requirements.txt .

RUN pip install -r ./requirements.txt