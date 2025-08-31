## Build & Flash
1. `cp include/secrets.h.example include/secrets.h` and edit values.
2. Paste CA PEM into `ROOT_CA_PEM`.
3. `pio run -t upload && pio device monitor`.
## Topics
Telemetry `devices/<id>/telemetry`, Status `devices/<id>/status`, Command `devices/<id>/cmd`.