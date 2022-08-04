ARG VERSION=7.17.4
FROM docker.elastic.co/elasticsearch/elasticsearch:$VERSION 

ARG UID
ARG GID

RUN groupmod -g $GID elasticsearch
RUN usermod -u $UID -g $GID elasticsearch
RUN chown -R elasticsearch /usr/share/elasticsearch

# https://qiita.com/takech9203/items/b96eff5773ce9d9cc9b3
# https://discuss.elastic.co/t/any-way-to-change-uid-of-elasticsearch-user-in-docker-image/117043
RUN sed -i -e 's/--userspec=1000/--userspec='$UID'/g' \
    -e 's/UID 1000/UID '$UID'/' \
    -e 's/chown -R 1000/chown -R '$UID'/' /usr/local/bin/docker-entrypoint.sh

RUN chown elasticsearch /usr/local/bin/docker-entrypoint.sh
