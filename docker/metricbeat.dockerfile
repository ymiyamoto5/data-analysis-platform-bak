FROM docker.elastic.co/beats/metricbeat:7.14.0

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

USER root

COPY ./docker/metricbeat.docker.yml /usr/share/metricbeat/metricbeat.yml

# RUN yum install -y tzdata && \
#     ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# COPY --chown=0:0 ./docker/metricbeat.docker.yml /usr/share/metricbeat/metricbeat.yml
# RUN chmod go-w /usr/share/metricbeat/metricbeat.yml