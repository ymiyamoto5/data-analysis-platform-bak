FROM fluent/fluentd:v1.14-1

ENV http_proxy=http://proxy.unisys.co.jp:8080
ENV https_proxy=http://proxy.unisys.co.jp:8080

USER root
RUN fluent-gem install fluent-plugin-elasticsearch \
    && fluent-gem install fluent-plugin-detect-exceptions