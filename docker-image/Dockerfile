FROM locustio/locust

COPY docker-entrypoint.sh /

USER root

RUN chmod +x /docker-entrypoint.sh

RUN chown locust:locust /docker-entrypoint.sh

USER locust

ENTRYPOINT ["/docker-entrypoint.sh"]
