FROM jupyter/base-notebook

WORKDIR /home/jovyan/backend
COPY --chown=1000:100 ./backend .

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

RUN pip install -r requirements.txt