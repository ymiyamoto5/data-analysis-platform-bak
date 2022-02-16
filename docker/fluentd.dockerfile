FROM fluent/fluentd:v1.14-1

USER root
RUN fluent-gem install fluent-plugin-elasticsearch \
    && fluent-gem install fluent-plugin-detect-exceptions