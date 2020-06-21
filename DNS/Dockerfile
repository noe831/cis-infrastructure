FROM python:3.8 as builder 
WORKDIR /
RUN pip install pyyaml jinja2
COPY templates/* /templates/
COPY source/*.yaml /source/
COPY gen-db.py / 
RUN ["python", "gen-db.py"]  

FROM builder as tester
WORKDIR /
RUN apt-get update -q -y && DEBIAN_FRONTEND=noninteractive apt-get install -y -q dnsutils 
RUN pip3 install pydig
COPY test.py /   
CMD ["python3", "test.py"]  

FROM ubuntu:focal as main
RUN apt-get update -q -y && apt-get upgrade -y && apt-get install -y -q bind9
RUN rm -f /etc/bind/named.conf
COPY --chown=bind:bind --from=builder build/db.* /etc/bind/
COPY --chown=bind:bind named*.conf /etc/bind/
COPY entrypoint.sh /
EXPOSE 53/udp 
CMD ["/bin/sh", "/entrypoint.sh"]
