mqtt_client - это микросервис, который записывает получение из брокера mqtt сообщения в базу данных (influxDB) для последующего отображения в графане.
Микросервис получает сообщения только из тех топиков в брокере mqtt, которые перечислены в файле topics.json. Для подключения к брокеру так же требуется наличие сертификатов tls.

В файле .env задаются параметры подключения к брокеру mqtt и базе данных.
