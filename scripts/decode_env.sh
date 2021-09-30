#!/bin/bash
# Декодирование настроек

sops -d src/mqtt_client/settings/enc_topics.json > src/mqtt_client/settings/topics.json
sops -d src/mqtt_client/settings/enc_env > src/mqtt_client/settings/.env