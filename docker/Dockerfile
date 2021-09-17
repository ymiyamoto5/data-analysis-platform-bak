FROM jupyter/base-notebook

WORKDIR /home/jovyan
COPY --chown=1000:100 ./backend ./backend

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

RUN pip install -r ./backend/requirements.txt