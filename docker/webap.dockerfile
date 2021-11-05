FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    sqlite3 \
    tzdata \
    && ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./backend/requirements.txt /app
RUN pip3 install -r /app/requirements.txt