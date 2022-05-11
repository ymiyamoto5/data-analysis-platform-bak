ARG VERSION=7.14.0
FROM docker.elastic.co/elasticsearch/elasticsearch:$VERSION 

ARG UID
ARG GID

RUN echo UID
RUN echo GID

RUN groupmod -g $GID elasticsearch
RUN usermod -u $UID -g $GID elasticsearch
RUN chown -R elasticsearch /usr/share/elasticsearch

# https://qiita.com/takech9203/items/b96eff5773ce9d9cc9b3
# https://discuss.elastic.co/t/any-way-to-change-uid-of-elasticsearch-user-in-docker-image/117043
RUN sed -i -e 's/--userspec=1000/--userspec=1001/g' \
    -e 's/UID 1000/UID 1001/' \
    -e 's/chown -R 1000/chown -R 1001/' /usr/local/bin/docker-entrypoint.sh

RUN chown elasticsearch /usr/local/bin/docker-entrypoint.sh
