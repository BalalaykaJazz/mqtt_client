FROM ubuntu:20.04

RUN apt update; apt upgrade; \
  apt install -y python3 python3-venv; \
  useradd -m -s /bin/bash mqtt;

RUN cd ~mqtt; \
  su mqtt -c "python3 -m venv venv"; \
  su mqtt -c "./venv/bin/pip install wheel"; \
  su mqtt -c "./venv/bin/pip install certifi chardet \"idna<3\" influxdb influxdb-client \
              msgpack paho-mqtt pip python-dateutil pytz requests Rx setuptools six urllib3"; \
  mkdir ~mqtt/mqtt;

COPY ./mqtt /home/mqtt/mqtt/
COPY ./scripts/autorun.sh /home/mqtt/mqtt/
COPY ./settings.json      /home/mqtt/mqtt/
RUN  chown mqtt\: ~mqtt

USER mqtt
CMD /home/mqtt/mqtt/autorun.sh
#docker run -it --rm --mount type=bind,source="/home/san/",target=/home/san/ san:v1 /run.sh
# docker run --rm -p 8086:8086 -v $(pwd)/influxdb:/var/lib/influxdb influxdb:1.8
