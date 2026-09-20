import time
from machine import Pin, PWM

from wifi import connect_wifi
from mqtt import connecting_mqtt, publish_infraredfox_data
from display import show_ready, show_train_warning, button_pressed

# -------------------------------------------------
# WIFI + MQTT
# -------------------------------------------------

print("Connecting to Wi-Fi...")
connect_wifi()
print("Wi-Fi connected")

print("Connecting to MQTT...")
mqtt_client = connecting_mqtt()
print("MQTT connected")

show_ready()
show_train_warning()
button_pressed()


# -------------------------------------------------
# INPUTS - BUTTONS
# -------------------------------------------------

warning_button = Pin(2, Pin.IN, Pin.PULL_UP)
danger_button = Pin(3, Pin.IN, Pin.PULL_UP)


# -------------------------------------------------
# OUTPUTS
# -------------------------------------------------

green_led = Pin(9, Pin.OUT)
yellow_led = Pin(10, Pin.OUT)
red_led = Pin(11, Pin.OUT)

buzzer = PWM(Pin(5))
buzzer.duty_u16(0)


def beep(freq, duration, duty):
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    time.sleep(duration)
    buzzer.duty_u16(0)


def set_zone(zone):
    print("ZONE:", zone)

    if zone == "SAFE":
        green_led.on()
        yellow_led.off()
        red_led.off()
        buzzer.duty_u16(0)

    elif zone == "WARNING":
        green_led.off()
        yellow_led.on()
        red_led.off()

        beep(700, 0.20, 3000)
        time.sleep(0.15)
        beep(700, 0.20, 3000)

    elif zone == "DANGER":
        green_led.off()
        yellow_led.off()
        red_led.on()

        for _ in range(4):
            beep(1500, 0.20, 5000)
            time.sleep(0.08)


def publish_zone(zone, zone_duration=0, danger_duration=0):
    print("Publishing:", zone)

    publish_infraredfox_data(mqtt_client, zone, zone_duration, danger_duration)


# -------------------------------------------------
# BUTTON CONTROL
# SAFE <-> WARNING <-> DANGER
# -------------------------------------------------

print("BUTTON CONTROL START")

current_zone = "SAFE"

set_zone(current_zone)
publish_zone(current_zone)


while True:

    # SAFE <-> WARNING
    if warning_button.value() == 0:

        if current_zone == "SAFE":
            current_zone = "WARNING"
            set_zone(current_zone)
            publish_zone(current_zone)

        elif current_zone == "WARNING":
            current_zone = "SAFE"
            set_zone(current_zone)
            publish_zone(current_zone)

        while warning_button.value() == 0:
            time.sleep(0.05)

        time.sleep(0.1)

    # WARNING <-> DANGER
    if danger_button.value() == 0:

        if current_zone == "WARNING":
            current_zone = "DANGER"
            set_zone(current_zone)
            publish_zone(current_zone)

        elif current_zone == "DANGER":
            current_zone = "WARNING"
            set_zone(current_zone)
            publish_zone(current_zone)

        while danger_button.value() == 0:
            time.sleep(0.05)

        time.sleep(0.1)

    time.sleep(0.05)
