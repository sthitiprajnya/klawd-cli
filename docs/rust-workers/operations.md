# Rust Worker Operations

## Local (docker-compose)
`docker compose up rust-provider-prober rust-skill-ingestor rust-event-normalizer`

## systemd
Use the templates below and set `ExecStart` to each binary with per-service ports:
- `rust-provider-prober.service`
- `rust-skill-ingestor.service`
- `rust-event-normalizer.service`

All services should restart on-failure and emit JSON logs to journald.
