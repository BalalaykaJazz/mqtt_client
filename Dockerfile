FROM python

WORKDIR /app

COPY mqtt_client_run.py /app
COPY requirements.txt /app
COPY src /app/src

RUN pip install -r /app/requirements.txt
RUN ["mkdir", "/app/src/mqtt_client/logs"]
CMD ["python", "mqtt_client_run.py"]