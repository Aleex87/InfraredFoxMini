import paho.mqtt.client as mqtt
import json
from database import create_table, insert_event


# Runs when a new MQTT message is received
def on_message(client, userdata, message):
    # Decode MQTT payload
    payload = message.payload.decode()

    try:
        # Convert JSON to Python dictionary
        data = json.loads(payload)

        # Extract safety data from message
        zone = data["zone"]
        zone_duration = float(data["zone_duration"])
        danger_duration = float(data["danger_duration"])

        print(zone, zone_duration, danger_duration)

        # Store valid MQTT data in TimescaleDB
        insert_event(zone, zone_duration, danger_duration)

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        print(f"Invalid MQTT message: {error}")


# Runs when the consumer connects to the MQTT broker
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to MQTT broker: {reason_code}")
    client.subscribe("infraredfox/safety")


if __name__ == "__main__":
    # Create database table if it does not already exist
    create_table()

    # Connect to Mosquitto for InfraredFox Mini safety data
    # Use the current Paho MQTT callback API
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("mosquitto", 1883)

    # Keep listening for incoming MQTT messages
    client.loop_forever()
