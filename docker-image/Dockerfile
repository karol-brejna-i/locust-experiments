FROM locustio/locust

COPY docker-entrypoint.sh /

USER root

RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
