# InfraredFoxMini

![InfraredFoxMini hardware](docs/immages/immage_station.png)

InfraredFoxMini is an edge computing prototype for detecting and monitoring objects entering railway risk zones.

The system uses a Raspberry Pi Pico 2 W with infrared sensors to detect movement between SAFE, WARNING and DANGER zones. The Pico publishes zone changes through MQTT to a containerized backend, where events are stored in TimescaleDB and visualized in Grafana.

## How to run

The Raspberry Pi Pico must be connected to the same network as the MQTT broker during local testing.

azure link: 
http://68.210.186.123:3000/

`docker compose up -d` 

shuth down the docker 

`docker compose down`

## Architecture

![InfraredFoxMini hardware](docs/immages/workflow.png)


Pico 2 W
→ MQTT / Mosquitto
→ Python Consumer
→ TimescaleDB
→ Grafana

## Hardware

- Raspberry Pi Pico 2 W
- 2 infrared sensors
- Green, yellow and red LEDs
- Buzzer
- LCD 16x2 HD44780
- Push button
- Breadboard
- Potentiometer
- 330 Ω resistor

## Zone Logic

- SAFE: normal state
- WARNING: object approaching the danger area
- DANGER: object detected inside the danger area

The buzzer and LEDs provide local warnings based on the current zone.

## LCD Display

### Wokwi simulation

The hardwere setup has been simulated in Wokwi

![InfraredFoxMini hardware](docs/immages/wiring.png)

link: https://wokwi.com/projects/475231800493635585

The LCD provides local edge monitoring.

Default state:

`SYSTEM READY`

When a train detection event is active:

`ATTENTION!`
`TRAIN ARRIVING`

## Grafana

![Grafana dashboard](docs/immages/dashboard.png)

Grafana is used as the frontend of the system to visualize live data sent from the Pico.

The dashboard is automatically configured through provisioning, so the same setup can be recreated consistently on different devices and after deployment.

In the deployed version, Grafana provides the user interface for monitoring the live data stored in TimescaleDB.

## IoT Pipeline

The Pico connects to Wi-Fi and publishes MQTT messages to:

`infraredfox/safety`

Example payload:

```json
{
  "zone": "WARNING",
  "zone_duration": 2.4,
  "danger_duration": 0
} 
```

Consumer recive the message and store the data in TimescaleDB.
This steps need for fether anlaisis like:
 - when there are more danger event? 
 - in wich day?
 - in wich station  

## Docker compose 

Has been used for:
- Mosquitto
- Consumer
- TimescaleDB
- Grafana
And for a easy deployment.


## Authors 

Alessandro
Mona
Mairan
