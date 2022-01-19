FROM docker.elastic.co/beats/metricbeat:7.14.0

USER root

COPY metricbeat.docker.yml /usr/share/metricbeat/metricbeat.yml

# RUN yum install -y tzdata && \
#     ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime