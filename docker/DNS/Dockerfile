FROM python:3.8 as builder 
WORKDIR /
RUN pip install pyyaml jinja2
COPY templates/* /templates/
COPY inventory.yaml / 
COPY gen-db.py / 
RUN ["python", "gen-db.py"]  

FROM ubuntu:focal 

RUN apt-get update -q -y && apt-get upgrade -y && apt-get install -y -q bind9

RUN rm -f /etc/bind/named.conf
COPY --chown=bind:bind --from=builder build/db.* /etc/bind/
COPY --chown=bind:bind source/named*.conf /etc/bind/
COPY source/entrypoint.sh /

EXPOSE 53/udp 

CMD ["/bin/sh", "/entrypoint.sh"]
