FROM ubuntu:focal 

RUN apt-get update -q -y && apt-get upgrade -y && apt-get install -y -q bind9

COPY --chown=bind:bind source/external/* /etc/bind/external/
COPY --chown=bind:bind source/internal/* /etc/bind/internal/
COPY --chown=bind:bind source/common/* /etc/bind/common/
COPY --chown=bind:bind source/named*.conf /etc/bind/
COPY --chown=root:root source/entrypoint.sh / 

EXPOSE 53/udp 

CMD ["/bin/sh", "/entrypoint.sh"]
