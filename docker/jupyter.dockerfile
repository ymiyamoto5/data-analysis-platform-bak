FROM jupyter/base-notebook

USER root
RUN chmod -R 777 /var/log

USER jovyan
WORKDIR /home/jovyan
COPY --chown=1000:100 ./backend/requirements.txt .
COPY --chown=1000:100 ./app_config_dev.json .

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080
ENV APP_CONFIG_PATH=$HOME/app_config_dev.json

RUN pip install -r ./requirements.txt