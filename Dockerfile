FROM ubuntu:20.04

RUN apt update; apt upgrade; \
  apt install -y python3 python3-venv; \
  useradd -m -s /bin/bash mqtt;

COPY ./requirements.txt /home/mqtt/
RUN cd ~mqtt; \
  su mqtt -c "python3 -m venv venv"; \
  su mqtt -c "./venv/bin/pip install wheel"; \
  su mqtt -c "./venv/bin/pip install chardet \"idna<3\" influxdb \
              msgpack requests setuptools -r requirements.txt"; \
  mkdir ~mqtt/mqtt_client;

COPY ./pod_mqtt_client    /home/mqtt/mqtt_client/
COPY ./scripts/autorun.sh /home/mqtt/mqtt_client/
#COPY ./settings.json      /home/mqtt/mqtt_client/
RUN  chown -R mqtt\: ~mqtt/mqtt_client

USER mqtt

CMD ["/usr/bin/bash", "/home/mqtt/mqtt_client/autorun.sh"]
