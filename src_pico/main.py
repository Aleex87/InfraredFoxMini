import time
from machine import Pin, PWM
from wifi import connect_wifi
from mqtt import connecting_mqtt, publish_infraredfox_data
from display import show_ready, show_train_warning, button_pressed


# Wifi and MQTT
print("Connecting to Wifi please wait..")
connect_wifi()
print("Wifi successfully connected!")

print("Connecting to MQTT please wait...")

try:
    mqtt_client = connecting_mqtt()
    print("MQTT successfully connected!")
except Exception as error:
    print("MQTT connection failed:", error)
    raise


# Inputs. Buttons will replace IR sensors
warningzone_button = Pin(2, Pin.IN, Pin.PULL_UP)
dangerzone_button = Pin(3, Pin.IN, Pin.PULL_UP)


# Outputs LED
green_led = Pin(9, Pin.OUT)
warning_led = Pin(10, Pin.OUT)
red_led = Pin(11, Pin.OUT)


# Buzzer
buzzer = PWM(Pin(5))
buzzer.duty_u16(0)


# Timing duration of zones
starttime_dangerzone = None
danger_duration = 0

starttime_warningzone = None
warning_duration = 0  # Changed name into warning for clarity


# Functions for BUZZER, ZONE CONTROL and MQTT publishing

def alarm(freq, duration, duty):  # LLM USAGE *
    buzzer.freq(freq)
    buzzer.duty_u16(duty)
    time.sleep(duration)
    buzzer.duty_u16(0)


def set_zone(zone):
    global starttime_warningzone
    global starttime_dangerzone

    print("ZONE:", zone)

    if zone == "SAFE":
        green_led.value(1)
        warning_led.value(0)
        red_led.value(0)
        buzzer.duty_u16(0)

    elif zone == "WARNING":
        if starttime_warningzone is None:
            starttime_warningzone = time.ticks_ms()

        green_led.value(0)
        warning_led.value(1)
        red_led.value(0)

        alarm(700, 0.20, 3000)
        time.sleep(0.15)
        alarm(700, 0.20, 3000)

    elif zone == "DANGER":
        if starttime_dangerzone is None:
            starttime_dangerzone = time.ticks_ms()

        green_led.value(0)
        warning_led.value(0)
        red_led.value(1)

        for i in range(4):
            alarm(1500, 0.20, 5000)
            time.sleep(0.08)


def publish_zone(zone, warning_duration=0, danger_duration=0):
    print("Publishing:", zone)

    publish_infraredfox_data(
        mqtt_client,
        zone,
        warning_duration,
        danger_duration
    )


## Button control
print("Button control started")

current_zone = "SAFE"
train_detection_active = False

set_zone(current_zone)
publish_zone(current_zone)
show_ready()


while True:

    # LCD train detection
    if button_pressed() and not train_detection_active:
        show_train_warning()
        train_detection_active = True

    elif not button_pressed() and train_detection_active:
        show_ready()
        train_detection_active = False


    # SAFE <-> WARNING
    if warningzone_button.value() == 0:

        # SAFE -> WARNING
        if current_zone == "SAFE":
            current_zone = "WARNING"

            set_zone(current_zone)

            publish_zone(
                current_zone,
                warning_duration,
                danger_duration
            )

        # WARNING -> SAFE
        elif current_zone == "WARNING":

            warning_duration = time.ticks_diff(
                time.ticks_ms(),
                starttime_warningzone
            ) / 1000

            starttime_warningzone = None

            print(
                "Time in WARNING:",
                warning_duration,
                "seconds"
            )

            current_zone = "SAFE"

            set_zone(current_zone)

            publish_zone(
                current_zone,
                warning_duration,
                danger_duration
            )

        # Wait until button is released
        while warningzone_button.value() == 0:
            time.sleep(0.05)

        time.sleep(0.1)


    # WARNING <-> DANGER
    elif dangerzone_button.value() == 0:

        # WARNING -> DANGER
        if current_zone == "WARNING":

            warning_duration = time.ticks_diff(
                time.ticks_ms(),
                starttime_warningzone
            ) / 1000

            starttime_warningzone = None

            print(
                "Time in WARNING:",
                warning_duration,
                "seconds"
            )

            current_zone = "DANGER"

            set_zone(current_zone)

            publish_zone(
                current_zone,
                warning_duration,
                danger_duration
            )

        # DANGER -> WARNING
        elif current_zone == "DANGER":

            danger_duration = time.ticks_diff(
                time.ticks_ms(),
                starttime_dangerzone
            ) / 1000

            starttime_dangerzone = None

            print(
                "Time in DANGER:",
                danger_duration,
                "seconds"
            )

            current_zone = "WARNING"

            set_zone(current_zone)

            publish_zone(
                current_zone,
                warning_duration,
                danger_duration
            )

        # Wait until button is released
        while dangerzone_button.value() == 0:
            time.sleep(0.05)

        time.sleep(0.1)


    time.sleep(0.05)