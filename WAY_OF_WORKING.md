# InfraredFoxMini - Way of Working

## Project Overview

InfraredFoxMini is an edge computing safety prototype for railway and metro platforms.

The system uses two pairs of IR break-beam sensors:

- first line = yellow warning zone
- second line = danger zone

The system uses LEDs and a buzzer for local warnings and sends data through the following pipeline:

Pico W -> MQTT -> Mosquitto -> Python Consumer -> TimescaleDB -> Grafana

---

## Team Responsibilities

- Alessandro: Infrastructure / Integration
- Mona: Edge / Pico / MQTT Publisher
- Marian: Data / Database / Grafana

Hardware assembly and Azure deployment are shared tasks.

---

## GitHub Workflow

- Never work directly on `main`
- Every task should have an Issue
- Every Issue should have its own branch
- Branch name should be written in the Issue
- Work is merged through Pull Requests
- Project board status: Todo -> In Progress -> Review -> Done

---

## Shared Technical Contract

| Area | Value |

| Repository | `InfraredFoxMini` |
| MQTT broker | `mosquitto` |
| MQTT port | `1883` |
| Pico client ID | `pico` |
| JSON zone values | `SAFE`, `YELLOW`, `DANGER` |
| Docker services | `mosquitto`, `consumer`, `timescaledb`, `grafana` |
| TimescaleDB port | `5432` |
| Grafana port | `3000` |
| Database | `infrafox` |
| Database user | `sensor` |
| Database host | `timescaledb` |
| Docker network | default Docker Compose network |
| Docker volumes | `timescale_data`, `grafana_data` |
| Secrets | stored in `.env` |
| Python dependencies | managed with `uv` and must be committed through

### MQTT payload

```json
{
  "zone": "SAFE",
  "zone_duration": 0.0,
  "danger_duration": 0.0
}

## Logic of the Zone

SAFE -> green LED

YELLOW -> yellow LED

DANGER -> red LED + buzzer

Movement toward danger:

Sensor 1 -> Sensor 2

Movement back to safety:

Sensor 2 -> Sensor 1

When the system returns to SAFE, timers are reset for the next cycle.