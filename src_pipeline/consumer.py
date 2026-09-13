import paho.mqtt.client as mqtt
import json


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

    except (json.JSONDecodeError, KeyError, ValueError) as error:
        print(f"Invalid MQTT message: {error}")


if __name__ == "__main__":
    # Connect to Mosquitto and subscribe to Infrared Fox Mini safety data
    # Use the current Paho MQTT callback API
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect("mosquitto", 1883)
    client.subscribe("infraredfox/safety")
    client.on_message = on_message

    # Keep listening for incoming MQTT messages
    client.loop_forever()
