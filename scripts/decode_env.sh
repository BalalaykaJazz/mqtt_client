#!/bin/bash
# Декодирование настроек

scp ../src/mqtt_client/settings/enc_topics.json ../src/mqtt_client/settings/topics.json
sops --hc-vault-transit $VAULT_ADDR/v1/sops/keys/iot  --verbose -d -i ../src/mqtt_client/settings/topics.json

sops --hc-vault-transit $VAULT_ADDR/v1/sops/keys/iot  --verbose -d -i ../src/mqtt_client/settings/enc_env
scp ../src/mqtt_client/settings/enc_env ../src/mqtt_client/settings/.env