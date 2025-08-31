# Embedded IoT: ESP32 → MQTTS → FastAPI(JWT) → React over HTTPS

See `docs/README.md` for diagrams. Quick start:

```bash
cd infrastructure
# dev non-TLS
docker compose up -d --build
# enable TLS overlay
mkdir -p certs passwords
openssl req -x509 -newkey rsa:2048 -keyout certs/ca.key -out certs/ca.crt -days 365 -nodes -subj "/CN=Local IoT CA"
openssl req -new -newkey rsa:2048 -keyout certs/server.key -out certs/server.csr -nodes -subj "/CN=localhost"
openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 365
mosquitto_passwd -c passwords device_01
mosquitto_passwd passwords backend
docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d --build
````

* UI: [https://localhost](https://localhost)
* API: [https://localhost/api/](https://localhost/api/)
* Broker: 8883 (TLS)

CI: see `.github/workflows/`.
