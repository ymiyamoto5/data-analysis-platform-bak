FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sqlite3 \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*


COPY ./backend /app/backend
# COPY ./backend/requirements.txt .

RUN pip3 install -r /app/backend/requirements.txt
# RUN pip3 install -r ./requirements.txt

# ENV APP_CONFIG_PATH=/app/backend/app_config_docker.json


