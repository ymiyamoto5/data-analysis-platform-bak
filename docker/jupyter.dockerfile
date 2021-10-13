FROM jupyter/base-notebook

USER root
RUN chmod -R 777 /var/log

USER jovyan
WORKDIR /home/jovyan
COPY --chown=1000:100 ./backend/requirements.txt .

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

RUN pip install -r ./requirements.txt