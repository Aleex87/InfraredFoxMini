# SKAPAR MQTT LOGIKEN 
from umqtt.simple import MQTTClient 
import json 

MQTT_BROKER = '192.168.0.93'
MQTT_PORT=1883
MQTT_CLIENT_ID= "pico"
MQTT_TOPIC ="infraredfox/safety"

def connecting_mqtt():
    client=MQTTClient(
        client_id = MQTT_CLIENT_ID,
        server= MQTT_BROKER,
        port = MQTT_PORT
    )
    #tillfällig kod
    print("Connecting to MQTT broker...")
    client.connect()
    print("MQTT connected")
    client.connect()

    return client 

def publish_infraredfox_data(client,zone, zone_duration, danger_duration):

    payload = {
        "zone": zone,
        "zone_duration": zone_duration,
        "danger_duration": danger_duration,
            }
    
    message=json.dumps(payload)

    client.publish(
        MQTT_TOPIC,
        message
                )

    # tillfällig testkod
    client.publish(MQTT_TOPIC, message)
    print("MQTT message published:", message)

   